# Converte Pro - All-in-One File Conversion Platform

![Converte Pro](https://img.shields.io/badge/Converte-Pro-blue?style=for-the-badge&logo=file-convert)
![Version](https://img.shields.io/badge/version-2.0.0-green?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)

A powerful, modern file conversion platform that supports images, PDFs, videos, audio, and documents with advanced processing capabilities, AI-powered features, and enterprise-grade reliability.

## 🚀 Features

### 🔧 Core Conversion Tools
- **Image Processing**: JPG, PNG, WEBP, HEIC conversion with advanced editing
- **PDF Suite**: Merge, split, compress, OCR, watermark, password protection
- **Video/Audio**: Format conversion, compression, resolution changes
- **Documents**: Office docs to PDF, batch processing
- **Batch Operations**: Process hundreds of files simultaneously

### 🎨 Advanced Features
- **Unified Settings Panel**: All conversion options in one place
- **Real-time Progress**: WebSocket-based live updates
- **Retry Mechanism**: Automatic retry with exponential backoff
- **Dark Mode**: Beautiful dark/light theme toggle
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Drag & Drop**: Intuitive file upload interface

### 🤖 AI-Powered Tools
- **Auto-translate**: Multi-language document translation
- **Document Summarization**: AI-powered content summarization
- **Data Extraction**: Extract tables, text, and metadata
- **Background Removal**: AI-based image background removal
- **Passport Photos**: Automatic passport-size photo generation

### 🏢 Enterprise Features
- **Queue System**: Redis-based job queue with priority handling
- **Observability**: Comprehensive logging and metrics
- **S3 Storage**: Cloud file storage with auto-expiry
- **Privacy Controls**: Auto-delete after download
- **Rate Limiting**: Quota management for free users
- **Docker Support**: Containerized deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Worker        │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Celery)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   MongoDB       │    │   Redis         │
│   (Reverse      │    │   (Database)    │    │   (Queue)       │
│    Proxy)       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Frontend
- **React 19** with modern hooks
- **Tailwind CSS** for styling
- **Radix UI** components
- **Lucide React** icons
- **Axios** for API calls
- **WebSocket** for real-time updates

### Backend
- **FastAPI** for high-performance API
- **MongoDB** with Motor async driver
- **Redis** for caching and queues
- **Celery** for background processing
- **PIL/Pillow** for image processing
- **PyPDF2** for PDF operations
- **FFmpeg** for video/audio processing
- **Tesseract** for OCR

### Infrastructure
- **Docker** containerization
- **Docker Compose** for local development
- **GitHub Actions** for CI/CD
- **Nginx** reverse proxy
- **AWS S3** for file storage (optional)

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/converte-pro.git
cd converte-pro
```

### 2. Environment Setup
```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit the environment file with your settings
nano backend/.env
```

### 3. Start with Docker Compose
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Development Setup

### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y imagemagick ghostscript libreoffice ffmpeg tesseract-ocr

# Start MongoDB and Redis
docker-compose up -d mongodb redis

# Run the development server
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend

# Install dependencies
yarn install

# Start development server
yarn start
```

### Running Tests
```bash
# Backend tests
cd backend
pytest tests/ -v --cov=.

# Frontend tests
cd frontend
yarn test

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📁 Project Structure

```
converte-pro/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   │   ├── ui/          # Base UI components
│   │   │   └── UnifiedSettingsPanel.jsx
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utility functions
│   │   └── App.js           # Main application component
│   ├── public/              # Static assets
│   ├── Dockerfile           # Production Docker image
│   └── Dockerfile.dev       # Development Docker image
├── backend/                 # FastAPI backend application
│   ├── server.py            # Main application file
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Docker image
│   ├── .env                 # Environment variables
│   └── tests/               # Test files
├── scripts/                 # Utility scripts
│   └── mongo-init.js        # MongoDB initialization
├── .github/                 # GitHub Actions workflows
│   └── workflows/
│       ├── frontend.yml     # Frontend CI/CD
│       ├── backend.yml      # Backend CI/CD
│       └── docker-compose.yml
├── docker-compose.yml       # Development environment
├── docker-compose.prod.yml  # Production environment
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=converte_pro

# Redis
REDIS_URL=redis://localhost:6379

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# File Storage
MAX_FILE_SIZE=52428800  # 50MB
UPLOAD_DIR=./uploads
PROCESSED_DIR=./processed

# Security
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret

# Processing
MAX_CONCURRENT_JOBS=10
JOB_TIMEOUT=3600
FILE_CLEANUP_HOURS=2

# Features
ENABLE_OCR=true
ENABLE_VIDEO_PROCESSING=true
ENABLE_AI_FEATURES=false
```

#### Frontend (.env)
```bash
REACT_APP_BACKEND_URL=http://localhost:8000
```

## 🚀 Deployment

### Production Deployment

#### 1. Using Docker Compose
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# With custom domain
docker-compose -f docker-compose.prod.yml -f docker-compose.override.yml up -d
```

#### 2. Using Kubernetes
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get services
```

#### 3. Using Cloud Providers

**AWS ECS:**
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t converte-pro .
docker tag converte-pro:latest <account>.dkr.ecr.us-east-1.amazonaws.com/converte-pro:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/converte-pro:latest
```

**Google Cloud Run:**
```bash
# Deploy to Cloud Run
gcloud run deploy converte-pro --source . --platform managed --region us-central1
```

## 📊 Monitoring and Observability

### Health Checks
- **Backend**: `GET /api/health`
- **Database**: MongoDB connection status
- **Queue**: Redis connection status
- **Storage**: File system health

### Metrics
- Job completion rates
- Processing times
- Error rates
- File sizes and types
- User activity

### Logging
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized log aggregation
- Error tracking and alerting

## 🔒 Security

### Data Protection
- File encryption at rest
- Secure file transfer (HTTPS)
- Auto-deletion of processed files
- No persistent storage of user data

### Authentication & Authorization
- JWT-based authentication
- Role-based access control
- API rate limiting
- CORS protection

### Privacy
- GDPR compliant
- No data mining
- User data anonymization
- Audit logging

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style
- **Python**: Black, isort, flake8
- **JavaScript**: ESLint, Prettier
- **Commits**: Conventional Commits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.converte-pro.com](https://docs.converte-pro.com)
- **Issues**: [GitHub Issues](https://github.com/yourusername/converte-pro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/converte-pro/discussions)
- **Email**: support@converte-pro.com

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - JavaScript library for building user interfaces
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Docker](https://www.docker.com/) - Containerization platform
- [MongoDB](https://www.mongodb.com/) - NoSQL database
- [Redis](https://redis.io/) - In-memory data structure store

---

**Made with ❤️ by the Converte Pro Team**