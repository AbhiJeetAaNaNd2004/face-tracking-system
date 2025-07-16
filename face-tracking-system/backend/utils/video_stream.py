"""
Video streaming utilities for MJPEG streaming and camera management.
"""
import cv2
import time
import threading
import logging
from typing import Dict, Optional, Generator
from queue import Queue, Empty
import numpy as np

logger = logging.getLogger(__name__)

class CameraManager:
    """Manages multiple camera streams and provides frame access."""
    
    def __init__(self):
        self.cameras: Dict[int, cv2.VideoCapture] = {}
        self.camera_threads: Dict[int, threading.Thread] = {}
        self.frame_queues: Dict[int, Queue] = {}
        self.running: Dict[int, bool] = {}
        self.lock = threading.Lock()
    
    def add_camera(self, camera_id: int, source: str = None) -> bool:
        """Add a camera to the manager."""
        with self.lock:
            if camera_id in self.cameras:
                logger.warning(f"Camera {camera_id} already exists")
                return True
            
            try:
                # Use camera_id as source if no source provided
                cap_source = source if source is not None else camera_id
                cap = cv2.VideoCapture(cap_source)
                
                if not cap.isOpened():
                    logger.error(f"Failed to open camera {camera_id} with source {cap_source}")
                    return False
                
                # Set camera properties
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                cap.set(cv2.CAP_PROP_FPS, 30)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for lower latency
                
                self.cameras[camera_id] = cap
                self.frame_queues[camera_id] = Queue(maxsize=5)
                self.running[camera_id] = True
                
                # Start frame capture thread
                thread = threading.Thread(
                    target=self._capture_frames,
                    args=(camera_id,),
                    daemon=True
                )
                thread.start()
                self.camera_threads[camera_id] = thread
                
                logger.info(f"Camera {camera_id} added successfully")
                return True
                
            except Exception as e:
                logger.error(f"Error adding camera {camera_id}: {e}")
                return False
    
    def remove_camera(self, camera_id: int):
        """Remove a camera from the manager."""
        with self.lock:
            if camera_id not in self.cameras:
                return
            
            # Stop the capture thread
            self.running[camera_id] = False
            
            # Wait for thread to finish
            if camera_id in self.camera_threads:
                self.camera_threads[camera_id].join(timeout=2)
                del self.camera_threads[camera_id]
            
            # Release camera resources
            if camera_id in self.cameras:
                self.cameras[camera_id].release()
                del self.cameras[camera_id]
            
            # Clean up frame queue
            if camera_id in self.frame_queues:
                del self.frame_queues[camera_id]
            
            if camera_id in self.running:
                del self.running[camera_id]
            
            logger.info(f"Camera {camera_id} removed")
    
    def _capture_frames(self, camera_id: int):
        """Continuously capture frames from a camera."""
        cap = self.cameras[camera_id]
        frame_queue = self.frame_queues[camera_id]
        
        while self.running.get(camera_id, False):
            try:
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"Failed to read frame from camera {camera_id}")
                    time.sleep(0.1)
                    continue
                
                # Add frame to queue (non-blocking)
                try:
                    frame_queue.put_nowait(frame)
                except:
                    # Queue is full, remove oldest frame and add new one
                    try:
                        frame_queue.get_nowait()
                        frame_queue.put_nowait(frame)
                    except Empty:
                        pass
                
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                logger.error(f"Error capturing frame from camera {camera_id}: {e}")
                time.sleep(1)
    
    def get_frame(self, camera_id: int) -> Optional[np.ndarray]:
        """Get the latest frame from a camera."""
        if camera_id not in self.frame_queues:
            return None
        
        try:
            # Get the most recent frame
            frame = None
            while not self.frame_queues[camera_id].empty():
                frame = self.frame_queues[camera_id].get_nowait()
            return frame
        except Empty:
            return None
    
    def is_camera_active(self, camera_id: int) -> bool:
        """Check if a camera is active."""
        return camera_id in self.cameras and self.running.get(camera_id, False)
    
    def get_active_cameras(self) -> list[int]:
        """Get list of active camera IDs."""
        return [cam_id for cam_id in self.cameras.keys() if self.running.get(cam_id, False)]
    
    def cleanup(self):
        """Clean up all cameras."""
        camera_ids = list(self.cameras.keys())
        for camera_id in camera_ids:
            self.remove_camera(camera_id)

# Global camera manager instance
camera_manager = CameraManager()

def generate_mjpeg_stream(camera_id: int) -> Generator[bytes, None, None]:
    """Generate MJPEG stream for a camera."""
    if not camera_manager.is_camera_active(camera_id):
        if not camera_manager.add_camera(camera_id):
            logger.error(f"Failed to initialize camera {camera_id}")
            return
    
    while camera_manager.is_camera_active(camera_id):
        frame = camera_manager.get_frame(camera_id)
        
        if frame is not None:
            # Encode frame as JPEG
            try:
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_bytes = buffer.tobytes()
                
                # Yield frame in MJPEG format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            except Exception as e:
                logger.error(f"Error encoding frame for camera {camera_id}: {e}")
        
        time.sleep(0.033)  # ~30 FPS

def create_test_frame(camera_id: int, width: int = 640, height: int = 480) -> np.ndarray:
    """Create a test frame for debugging."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add some content
    cv2.putText(frame, f"Camera {camera_id}", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"Time: {time.strftime('%H:%M:%S')}", (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    return frame

def validate_camera_config(camera_id: int, config: dict) -> bool:
    """Validate camera configuration."""
    required_fields = ['camera_name', 'camera_type']
    
    for field in required_fields:
        if field not in config:
            logger.error(f"Missing required field '{field}' in camera config")
            return False
    
    if config.get('resolution_width', 0) <= 0 or config.get('resolution_height', 0) <= 0:
        logger.error("Invalid resolution in camera config")
        return False
    
    if config.get('fps', 0) <= 0:
        logger.error("Invalid FPS in camera config")
        return False
    
    return True