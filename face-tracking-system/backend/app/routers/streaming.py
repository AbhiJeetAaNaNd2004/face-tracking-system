from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.fts_system import FaceTrackingPipeline, generate_mjpeg
from utils.security import verify_token as verify_jwt_token
from utils.video_stream import generate_mjpeg_stream
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

# Setup Security
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token for streaming access."""
    payload = verify_jwt_token(credentials.credentials)
    if payload.get("status") != "active":
        raise HTTPException(status_code=403, detail="Account inactive or suspended")
    return payload


# Router Setup
router = APIRouter(prefix="/stream", tags=["Streaming"])

# Stream management
active_streams = 0
MAX_STREAMS = int(os.getenv("MAX_CAMERA_STREAMS", "5"))

# Singleton Pipeline Manager
class PipelineSingleton:
    instance = None

    @classmethod
    def get_pipeline(cls):
        if cls.instance is None:
            cls.instance = FaceTrackingPipeline()
        return cls.instance


@router.get("/{camera_id}")
async def stream_camera(camera_id: int, request: Request, user=Depends(verify_token)):
    """Stream video from a specific camera with authentication and rate limiting."""
    global active_streams
    
    # Check stream limit
    if active_streams >= MAX_STREAMS:
        raise HTTPException(status_code=503, detail="Too many active streams")
    
    active_streams += 1
    
    try:
        async def safe_stream():
            try:
                # Use the new video streaming utility
                for frame in generate_mjpeg_stream(camera_id):
                    if await request.is_disconnected():
                        logger.info(f"Client disconnected from camera {camera_id}")
                        break
                    yield frame
            except Exception as e:
                logger.exception(f"Stream error for camera {camera_id}")
                return
            finally:
                # Decrement stream counter when done
                global active_streams
                active_streams = max(0, active_streams - 1)

        logger.info(f"🔴 Stream started for camera {camera_id} by user {user.get('sub')} (Active streams: {active_streams})")

        return StreamingResponse(
            safe_stream(),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    except Exception as e:
        # Make sure to decrement counter on error
        active_streams = max(0, active_streams - 1)
        logger.error(f"Failed to start stream for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to start camera stream")


@router.get("/status/cameras")
async def get_camera_status(user=Depends(verify_token)):
    """Get status of all cameras and active streams."""
    from utils.video_stream import camera_manager
    
    active_cameras = camera_manager.get_active_cameras()
    
    return {
        "active_streams": active_streams,
        "max_streams": MAX_STREAMS,
        "active_cameras": active_cameras,
        "available_slots": MAX_STREAMS - active_streams
    }
