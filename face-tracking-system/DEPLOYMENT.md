# Face Tracking System - Deployment Guide

## 🚀 Quick Start

### For Development (Local)

1. **Navigate to backend directory**:
   ```bash
   cd face-tracking-system/backend
   ```

2. **Run the startup script**:
   ```bash
   ./start.sh
   ```

### For Production (Docker)

1. **Navigate to project root**:
   ```bash
   cd face-tracking-system
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your settings
   ```

3. **Start the application**:
   ```bash
   docker-compose up -d
   ```

4. **Initialize database**:
   ```bash
   docker-compose exec backend python scripts/init_database.py
   ```

## 📋 Pre-Deployment Checklist

### Security Configuration
- [ ] Change `SECRET_KEY` to a secure 32+ character string
- [ ] Change default admin password from `admin123!`
- [ ] Configure `ALLOWED_ORIGINS` for your frontend domain
- [ ] Set secure database password in `DB_PASSWORD`
- [ ] Review and configure `TrustedHostMiddleware` settings

### Database Setup
- [ ] PostgreSQL 12+ installed and running
- [ ] Database `face_tracking` created
- [ ] Database user has appropriate permissions
- [ ] Database connection tested

### Camera Configuration
- [ ] USB cameras connected and accessible (`/dev/video*`)
- [ ] Camera permissions configured (`video` group)
- [ ] IP cameras accessible over network
- [ ] Camera resolutions and FPS configured appropriately

### System Resources
- [ ] Minimum 4GB RAM available
- [ ] Sufficient storage for face embeddings and logs
- [ ] GPU drivers installed (if using GPU acceleration)
- [ ] Network bandwidth adequate for video streaming

## 🔧 Configuration Details

### Required Environment Variables

```bash
# Essential Settings
SECRET_KEY=your-super-secret-key-here  # MUST BE CHANGED
DB_PASSWORD=secure-database-password   # MUST BE CHANGED

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=face_tracking
DB_USER=postgres

# Server Settings
HOST=0.0.0.0
PORT=8000
WORKERS=2
LOG_LEVEL=info

# Frontend Integration
FRONTEND_URL=http://your-frontend-domain.com
ALLOWED_ORIGINS=http://localhost:3000,http://your-frontend-domain.com
```

### Optional Environment Variables

```bash
# Camera Settings
MAX_CAMERA_STREAMS=5
DEFAULT_CAMERA_RESOLUTION_WIDTH=1920
DEFAULT_CAMERA_RESOLUTION_HEIGHT=1080
DEFAULT_CAMERA_FPS=30

# Face Recognition Tuning
FACE_DETECTION_CONFIDENCE=0.7
FACE_RECOGNITION_THRESHOLD=0.6
GPU_DEVICE_ID=0

# File Storage
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760

# Feature Toggles
ENABLE_DOCS=true
DEBUG=false
RELOAD=false

# SSL (Production)
SSL_KEYFILE=/path/to/keyfile.pem
SSL_CERTFILE=/path/to/certfile.pem
```

## 🛡️ Security Hardening

### 1. Generate Secure SECRET_KEY

```python
# Generate a secure secret key
import secrets
secret_key = secrets.token_urlsafe(32)
print(f"SECRET_KEY={secret_key}")
```

### 2. Database Security

```sql
-- Create dedicated database user
CREATE USER fts_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE face_tracking TO fts_user;

-- Limit database connections
ALTER SYSTEM SET max_connections = '100';
```

### 3. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 8000/tcp  # API
sudo ufw allow 5432/tcp  # PostgreSQL (internal only)
sudo ufw enable
```

### 4. SSL/HTTPS Setup

```bash
# Generate self-signed certificate for testing
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Set environment variables
export SSL_KEYFILE=/path/to/key.pem
export SSL_CERTFILE=/path/to/cert.pem
```

## 📊 Monitoring Setup

### Health Checks

```bash
# System health endpoint
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "services": {
    "database": "healthy",
    "cameras": {
      "active_count": 2,
      "cameras": [0, 1]
    },
    "background_tasks": "running"
  }
}
```

### Log Monitoring

```bash
# Application logs
tail -f backend/logs/app.log

# Docker logs
docker-compose logs -f backend

# Database logs
docker-compose logs -f postgres
```

### Performance Monitoring

Monitor these key metrics:
- **CPU Usage**: Should be < 80% under normal load
- **Memory Usage**: Monitor for memory leaks in long-running tasks
- **Database Connections**: Monitor connection pool usage
- **Camera Streams**: Track active streams and frame rates
- **API Response Times**: Monitor endpoint performance

## 🔄 Backup and Recovery

### Database Backup

```bash
# Automated backup script
docker-compose exec postgres pg_dump -U postgres face_tracking > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker-compose exec -T postgres psql -U postgres face_tracking < backup_file.sql
```

### Configuration Backup

```bash
# Backup configuration files
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env docker-compose.yml backend/.env.example
```

## 🚀 Scaling Considerations

### Horizontal Scaling

```bash
# Scale backend workers
docker-compose up -d --scale backend=3

# Use load balancer
docker-compose --profile production up -d
```

### Database Optimization

```sql
-- PostgreSQL tuning for production
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
SELECT pg_reload_conf();
```

### Camera Load Distribution

- Distribute cameras across multiple backend instances
- Use dedicated streaming servers for high camera counts
- Implement camera load balancing based on CPU usage

## 🐛 Troubleshooting

### Common Deployment Issues

1. **Database Connection Failed**
   ```bash
   # Check PostgreSQL status
   systemctl status postgresql
   # Or for Docker
   docker-compose ps postgres
   ```

2. **Camera Access Denied**
   ```bash
   # Add user to video group
   sudo usermod -a -G video $USER
   # Set camera permissions
   sudo chmod 666 /dev/video0
   ```

3. **High Memory Usage**
   ```bash
   # Monitor memory usage
   docker stats
   # Adjust camera resolution/FPS
   # Reduce MAX_CAMERA_STREAMS
   ```

4. **Poor Face Recognition**
   - Check lighting conditions
   - Verify camera focus and positioning
   - Adjust detection thresholds
   - Ensure quality enrollment photos

### Performance Optimization

1. **Enable GPU Acceleration**
   ```bash
   # Install NVIDIA Docker support
   sudo apt install nvidia-docker2
   # Update docker-compose.yml to use GPU
   ```

2. **Optimize Database Queries**
   ```sql
   -- Create indexes for frequent queries
   CREATE INDEX idx_attendance_employee_id ON attendance_records(employee_id);
   CREATE INDEX idx_attendance_timestamp ON attendance_records(timestamp);
   ```

3. **Camera Stream Optimization**
   - Use hardware-accelerated encoding
   - Adjust compression quality vs. bandwidth
   - Implement adaptive bitrate streaming

## 📞 Support

For deployment issues:

1. **Check logs** for error messages
2. **Verify configuration** against this guide
3. **Test components** individually (database, cameras, API)
4. **Review resource usage** (CPU, memory, disk, network)

---

**Ready to deploy?** Follow the Quick Start section and refer back to this guide for detailed configuration options.