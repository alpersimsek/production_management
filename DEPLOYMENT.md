# Demo Kimya ERP - OCI Deployment Guide

## 🚀 Quick Deployment

### Prerequisites
- Docker and Docker Compose installed on your OCI server
- Git (to clone the repository)
- At least 2GB RAM and 10GB disk space

### Step 1: Upload Files to OCI Server

You can either:
1. **Upload via SCP/SFTP**: Upload the entire project folder to your OCI server
2. **Clone from Git**: If you have the code in a Git repository
3. **Direct Transfer**: Use any file transfer method

### Step 2: Connect to Your OCI Server

```bash
ssh -i your-key.pem ubuntu@145.241.236.172
```

### Step 3: Install Docker (if not already installed)

```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again to apply group changes
exit
```
```

### Step 4: Deploy the Application

**Option A: Using the upload script (Recommended)**
```bash
# From your local machine, upload files using the script
./upload-to-oci.sh -k your-key.pem
```

**Option B: Manual upload**
```bash
# Upload files manually
scp -r -i your-key.pem ./ ubuntu@145.241.236.172:/home/ubuntu/demo-erp/
```

**Then deploy on the server:**
```bash
# Navigate to your project directory
cd /home/ubuntu/demo-erp

# Run the deployment script
./deploy.sh
```

### Step 5: Access the Application

Once deployment is complete, you can access:

- **Main Application**: http://145.241.236.172
- **API Documentation**: http://145.241.236.172/api/docs
- **Flower Monitoring**: http://145.241.236.172/flower/
- **Health Check**: http://145.241.236.172/health

## 🔐 Default Login Credentials

- **Admin**: admin@demo.com / admin123
- **Manager**: manager@demo.com / manager123
- **Operator**: operator@demo.com / operator123

## 🛠️ Manual Deployment (Alternative)

If you prefer manual deployment:

```bash
# Build frontend
cd frontend
npm install
npm run build
cd ..

# Start services
docker-compose -f docker-compose.prod.yml up --build -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# Seed data
docker-compose -f docker-compose.prod.yml exec api python seed_data.py
docker-compose -f docker-compose.prod.yml exec api python seed_demo_users.py
```

## 🔧 Management Commands

### View Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### Restart Services
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Stop Services
```bash
docker-compose -f docker-compose.prod.yml down
```

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up --build -d
```

## 🔒 Security Considerations

### Before Going Live:

1. **Change Default Passwords**
   - Update all default user passwords
   - Use strong, unique passwords

2. **Update Secret Key**
   - Change `SECRET_KEY` in `docker-compose.prod.yml`
   - Use a strong, random secret key

3. **Configure SSL/HTTPS**
   - Obtain SSL certificates
   - Update nginx configuration for HTTPS

4. **Firewall Configuration**
   - Only open necessary ports (80, 443)
   - Block direct access to database ports

5. **Database Security**
   - Change default database credentials
   - Enable database encryption

6. **Backup Strategy**
   - Set up regular database backups
   - Test backup restoration process

## 📊 Monitoring

### Health Checks
- Application: http://145.241.236.172/health
- Flower: http://145.241.236.172/flower/

### Log Monitoring
```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f worker
```

## 🆘 Troubleshooting

### Common Issues:

1. **Port Conflicts**
   - Check if ports 80, 5432, 6379 are available
   - Modify ports in docker-compose.prod.yml if needed

2. **Permission Issues**
   - Ensure Docker is properly installed
   - Check file permissions

3. **Database Connection Issues**
   - Verify database is running: `docker-compose -f docker-compose.prod.yml ps`
   - Check database logs: `docker-compose -f docker-compose.prod.yml logs db`

4. **Frontend Not Loading**
   - Check nginx logs: `docker-compose -f docker-compose.prod.yml logs nginx`
   - Verify frontend build: `ls -la frontend/dist/`

### Getting Help:
- Check application logs
- Verify all services are running
- Ensure all ports are accessible
- Check firewall settings

## 📈 Performance Optimization

### For Production:
1. **Database Optimization**
   - Configure PostgreSQL for production
   - Set up connection pooling
   - Enable query optimization

2. **Caching**
   - Configure Redis for better performance
   - Enable application-level caching

3. **Load Balancing**
   - Set up multiple API instances
   - Configure load balancer

4. **Monitoring**
   - Set up application monitoring
   - Configure alerting
   - Monitor resource usage
