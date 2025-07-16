# Face Tracking System - Complete Backend

A comprehensive enterprise-grade face tracking and attendance management system built with FastAPI, featuring real-time face detection, recognition, and streaming capabilities.

## 🚀 Features

- **Real-time Face Detection & Recognition**: Advanced face tracking pipeline with high accuracy
- **Live Video Streaming**: MJPEG streaming from multiple cameras
- **Attendance Management**: Automated attendance tracking with confidence scoring
- **Employee Management**: Complete CRUD operations for employee data
- **Face Embedding Management**: Store and manage face embeddings with enrollment capabilities
- **JWT Authentication**: Secure API access with role-based permissions
- **Background Tasks**: Camera monitoring, database cleanup, and maintenance
- **RESTful API**: Well-documented API with OpenAPI/Swagger support
- **Production Ready**: Docker support, logging, monitoring, and deployment configurations

## 📋 Requirements

### System Requirements
- Python 3.11+
- PostgreSQL 12+
- OpenCV compatible cameras (USB/IP cameras)
- GPU support (optional, for better performance)

### Hardware Requirements
- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB+ RAM, 4+ CPU cores, GPU (NVIDIA/AMD)
- **Storage**: 10GB+ for system, additional space for face embeddings and logs

## 🛠️ Installation & Setup

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd face-tracking-system
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   nano .env
   ```

3. **Start the application**:
   ```bash
   # Start all services
   docker-compose up -d

   # Or for production with nginx
   docker-compose --profile production up -d
   ```

4. **Initialize the database**:
   ```bash
   docker-compose exec backend python scripts/init_database.py
   ```

### Option 2: Local Development Setup

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd face-tracking-system/backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PostgreSQL database**:
   ```bash
   # Install PostgreSQL and create database
   sudo -u postgres createdb face_tracking
   ```

5. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   nano .env
   ```

6. **Initialize database**:
   ```bash
   python scripts/init_database.py
   ```

7. **Start the application**:
   ```bash
   python run.py
   ```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=face_tracking
DB_USER=postgres
DB_PASSWORD=your-password

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=2

# Camera Settings
MAX_CAMERA_STREAMS=5
DEFAULT_CAMERA_RESOLUTION_WIDTH=1920
DEFAULT_CAMERA_RESOLUTION_HEIGHT=1080

# Face Recognition
FACE_DETECTION_CONFIDENCE=0.7
FACE_RECOGNITION_THRESHOLD=0.6
```

### Camera Configuration

Connect USB cameras or configure IP cameras:
```bash
# For USB cameras, ensure proper permissions
sudo usermod -a -G video $USER

# For IP cameras, configure in database or through API
curl -X POST "http://localhost:8000/cameras" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"camera_id": 1, "source": "rtsp://camera-ip:554/stream"}'
```

## 🔐 Authentication

Default credentials after initialization:
- **Username**: `admin`
- **Password**: `admin123!`

**⚠️ IMPORTANT**: Change the default password immediately in production!

### API Usage

1. **Login to get token**:
   ```bash
   curl -X POST "http://localhost:8000/auth/login/" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123!"}'
   ```

2. **Use token in requests**:
   ```bash
   curl -X GET "http://localhost:8000/employees/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

## 📚 API Documentation

Access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /auth/login/` | User authentication |
| `GET /employees/` | List all employees |
| `POST /employees/` | Create new employee |
| `GET /stream/{camera_id}` | Live video stream |
| `POST /embeddings/enroll/` | Enroll employee faces |
| `GET /attendance/` | Get attendance records |
| `GET /health` | System health check |

## 🎥 Camera Setup

### USB Cameras
```bash
# Check available cameras
ls /dev/video*

# Test camera access
ffmpeg -f v4l2 -list_formats all -i /dev/video0
```

### IP Cameras
Configure RTSP/HTTP streams through the API:
```python
camera_config = {
    "camera_id": 1,
    "camera_name": "Front Door",
    "source": "rtsp://admin:password@192.168.1.100:554/stream1",
    "resolution_width": 1920,
    "resolution_height": 1080,
    "fps": 30
}
```

## 👥 Employee Management

### Enroll Employee Faces

1. **Create employee record**:
   ```bash
   curl -X POST "http://localhost:8000/employees/" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"employee_id": "EMP001", "name": "John Doe", "department": "IT"}'
   ```

2. **Upload face images**:
   ```bash
   curl -X POST "http://localhost:8000/embeddings/enroll/" \
     -H "Authorization: Bearer TOKEN" \
     -F "employee_id=EMP001" \
     -F "employee_name=John Doe" \
     -F "files=@photo1.jpg" \
     -F "files=@photo2.jpg"
   ```

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# System health
curl http://localhost:8000/health

# Database status
docker-compose exec postgres pg_isready

# Logs
docker-compose logs -f backend
```

### Background Tasks

The system runs several background tasks:
- **Camera Health Monitoring**: Checks camera connectivity every 30 seconds
- **Database Cleanup**: Removes old logs and tracking data hourly
- **Attendance Processing**: Processes attendance events every minute

## 🚀 Production Deployment

### Security Checklist

- [ ] Change default admin password
- [ ] Generate secure SECRET_KEY (32+ characters)
- [ ] Configure firewall rules
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Set up monitoring and alerting

### Performance Optimization

1. **Database Tuning**:
   ```sql
   -- PostgreSQL optimizations
   ALTER SYSTEM SET shared_buffers = '256MB';
   ALTER SYSTEM SET effective_cache_size = '1GB';
   ALTER SYSTEM SET maintenance_work_mem = '64MB';
   ```

2. **Camera Optimization**:
   - Use hardware-accelerated encoding
   - Adjust resolution based on detection accuracy needs
   - Configure appropriate FPS for your use case

3. **Scaling**:
   ```bash
   # Scale backend workers
   docker-compose up -d --scale backend=3
   
   # Use load balancer (nginx example included)
   docker-compose --profile production up -d
   ```

## 🔧 Troubleshooting

### Common Issues

1. **Camera not detected**:
   ```bash
   # Check camera permissions
   ls -la /dev/video*
   sudo chmod 666 /dev/video0
   ```

2. **Database connection failed**:
   ```bash
   # Check PostgreSQL status
   docker-compose exec postgres pg_isready
   
   # Reset database
   docker-compose down -v
   docker-compose up -d postgres
   ```

3. **Face recognition accuracy issues**:
   - Ensure good lighting conditions
   - Use high-quality enrollment photos
   - Adjust detection/recognition thresholds
   - Check camera focus and positioning

### Logs

```bash
# Application logs
docker-compose logs -f backend

# Database logs
docker-compose logs -f postgres

# System logs (if running locally)
tail -f backend/logs/app.log
```

## 🤝 Support

For issues and support:
1. Check the troubleshooting section
2. Review logs for error messages
3. Ensure all dependencies are properly installed
4. Verify camera and database connectivity

## 📄 License

This project is proprietary software. Unauthorized copying, distribution, or modification is prohibited.

---

**⚠️ Security Notice**: This system handles biometric data. Ensure compliance with relevant privacy laws and regulations in your jurisdiction.