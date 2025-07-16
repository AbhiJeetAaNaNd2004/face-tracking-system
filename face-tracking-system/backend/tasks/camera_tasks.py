"""
Background tasks for camera monitoring, health checks, and maintenance.
"""
import asyncio
import logging
import time
from typing import Dict, List
from datetime import datetime, timedelta
from db.db_manager import DatabaseManager
from db.db_models import CameraConfig, SystemLog
from utils.video_stream import camera_manager

logger = logging.getLogger(__name__)

class CameraMonitor:
    """Monitor camera health and performance."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.monitoring = False
        self.check_interval = 30  # seconds
        self.camera_stats: Dict[int, dict] = {}
    
    async def start_monitoring(self):
        """Start camera monitoring task."""
        self.monitoring = True
        logger.info("🎥 Camera monitoring started")
        
        while self.monitoring:
            try:
                await self._check_camera_health()
                await self._cleanup_inactive_cameras()
                await self._log_camera_stats()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in camera monitoring: {e}")
                await asyncio.sleep(5)
    
    def stop_monitoring(self):
        """Stop camera monitoring."""
        self.monitoring = False
        logger.info("🛑 Camera monitoring stopped")
    
    async def _check_camera_health(self):
        """Check health of all active cameras."""
        active_cameras = camera_manager.get_active_cameras()
        
        for camera_id in active_cameras:
            try:
                # Get frame to test camera
                frame = camera_manager.get_frame(camera_id)
                
                if frame is not None:
                    self._update_camera_stats(camera_id, healthy=True)
                else:
                    self._update_camera_stats(camera_id, healthy=False)
                    logger.warning(f"Camera {camera_id} not providing frames")
                    
            except Exception as e:
                logger.error(f"Health check failed for camera {camera_id}: {e}")
                self._update_camera_stats(camera_id, healthy=False)
    
    async def _cleanup_inactive_cameras(self):
        """Clean up cameras that have been inactive for too long."""
        current_time = time.time()
        inactive_threshold = 300  # 5 minutes
        
        cameras_to_remove = []
        
        for camera_id, stats in self.camera_stats.items():
            last_activity = stats.get('last_activity', 0)
            if current_time - last_activity > inactive_threshold:
                cameras_to_remove.append(camera_id)
        
        for camera_id in cameras_to_remove:
            logger.info(f"Removing inactive camera {camera_id}")
            camera_manager.remove_camera(camera_id)
            del self.camera_stats[camera_id]
    
    async def _log_camera_stats(self):
        """Log camera statistics to database."""
        for camera_id, stats in self.camera_stats.items():
            try:
                log_entry = SystemLog(
                    log_level="INFO",
                    message=f"Camera {camera_id} stats",
                    component="camera_monitor",
                    camera_id=camera_id,
                    additional_data={
                        "healthy": stats.get("healthy", False),
                        "frame_count": stats.get("frame_count", 0),
                        "error_count": stats.get("error_count", 0),
                        "uptime": stats.get("uptime", 0)
                    }
                )
                self.db_manager.add_system_log(log_entry)
            except Exception as e:
                logger.error(f"Failed to log camera stats for camera {camera_id}: {e}")
    
    def _update_camera_stats(self, camera_id: int, healthy: bool):
        """Update camera statistics."""
        current_time = time.time()
        
        if camera_id not in self.camera_stats:
            self.camera_stats[camera_id] = {
                "healthy": healthy,
                "frame_count": 0,
                "error_count": 0,
                "last_activity": current_time,
                "start_time": current_time
            }
        
        stats = self.camera_stats[camera_id]
        stats["healthy"] = healthy
        stats["last_activity"] = current_time
        stats["uptime"] = current_time - stats["start_time"]
        
        if healthy:
            stats["frame_count"] += 1
        else:
            stats["error_count"] += 1

class DatabaseCleanupTask:
    """Background task for database maintenance and cleanup."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.cleanup_interval = 3600  # 1 hour
        self.running = False
    
    async def start_cleanup(self):
        """Start database cleanup task."""
        self.running = True
        logger.info("🧹 Database cleanup task started")
        
        while self.running:
            try:
                await self._cleanup_old_logs()
                await self._cleanup_old_tracking_records()
                await self._optimize_database()
                await asyncio.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"Error in database cleanup: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    def stop_cleanup(self):
        """Stop database cleanup task."""
        self.running = False
        logger.info("🛑 Database cleanup task stopped")
    
    async def _cleanup_old_logs(self):
        """Remove old system logs."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30)  # Keep logs for 30 days
            deleted_count = self.db_manager.delete_old_system_logs(cutoff_date)
            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} old system log entries")
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}")
    
    async def _cleanup_old_tracking_records(self):
        """Remove old tracking records."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=7)  # Keep tracking records for 7 days
            deleted_count = self.db_manager.delete_old_tracking_records(cutoff_date)
            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} old tracking records")
        except Exception as e:
            logger.error(f"Failed to cleanup old tracking records: {e}")
    
    async def _optimize_database(self):
        """Perform database optimization."""
        try:
            # This would depend on your database implementation
            # For PostgreSQL, you might run VACUUM ANALYZE
            logger.info("Running database optimization (placeholder)")
        except Exception as e:
            logger.error(f"Failed to optimize database: {e}")

class AttendanceProcessor:
    """Process attendance events and generate reports."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.processing = False
        self.process_interval = 60  # 1 minute
    
    async def start_processing(self):
        """Start attendance processing task."""
        self.processing = True
        logger.info("📊 Attendance processing started")
        
        while self.processing:
            try:
                await self._process_pending_attendance()
                await self._generate_daily_summaries()
                await asyncio.sleep(self.process_interval)
            except Exception as e:
                logger.error(f"Error in attendance processing: {e}")
                await asyncio.sleep(30)
    
    def stop_processing(self):
        """Stop attendance processing."""
        self.processing = False
        logger.info("🛑 Attendance processing stopped")
    
    async def _process_pending_attendance(self):
        """Process pending attendance records."""
        try:
            # Get unprocessed attendance records
            # This is a placeholder - implement based on your needs
            logger.debug("Processing pending attendance records")
        except Exception as e:
            logger.error(f"Failed to process attendance: {e}")
    
    async def _generate_daily_summaries(self):
        """Generate daily attendance summaries."""
        try:
            # Generate summaries for yesterday if not already done
            # This is a placeholder - implement based on your needs
            logger.debug("Generating daily attendance summaries")
        except Exception as e:
            logger.error(f"Failed to generate daily summaries: {e}")

# Global task managers
camera_monitor = CameraMonitor()
database_cleanup = DatabaseCleanupTask()
attendance_processor = AttendanceProcessor()

async def start_background_tasks():
    """Start all background tasks."""
    logger.info("🚀 Starting background tasks")
    
    tasks = [
        asyncio.create_task(camera_monitor.start_monitoring()),
        asyncio.create_task(database_cleanup.start_cleanup()),
        asyncio.create_task(attendance_processor.start_processing())
    ]
    
    return tasks

def stop_background_tasks():
    """Stop all background tasks."""
    logger.info("🛑 Stopping background tasks")
    camera_monitor.stop_monitoring()
    database_cleanup.stop_cleanup()
    attendance_processor.stop_processing()
    
    # Cleanup cameras
    camera_manager.cleanup()