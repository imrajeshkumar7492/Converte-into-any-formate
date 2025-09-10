#!/bin/bash

# File Converter - Complete Deployment Setup Script
# Repository: imrajeshkumar7492/Converte-into-any-formate

set -e

echo "🚀 Setting up File Converter for deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_error "Not a git repository. Please run 'git init' first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    print_error "Please run this script from the root of the project directory."
    exit 1
fi

print_info "Checking project structure..."

# Verify all required files exist
required_files=(
    ".github/workflows/ci-cd.yml"
    ".github/dependabot.yml"
    ".github/workflows/security-scan.yml"
    "backend/Dockerfile"
    "frontend/Dockerfile"
    "docker-compose.yml"
    "sonar-project.properties"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "Found $file"
    else
        print_error "Missing required file: $file"
        exit 1
    fi
done

# Check if environment files exist
if [ ! -f ".env.example" ]; then
    print_warning "Missing .env.example file"
else
    print_status "Environment template found"
fi

# Install dependencies and test builds
print_info "Installing frontend dependencies..."
cd frontend
if command -v yarn &> /dev/null; then
    yarn install --frozen-lockfile
    print_status "Frontend dependencies installed"
else
    print_error "Yarn not found. Please install Yarn package manager."
    exit 1
fi

print_info "Testing frontend build..."
if yarn build; then
    print_status "Frontend build successful"
else
    print_error "Frontend build failed"
    exit 1
fi

cd ..

print_info "Installing backend dependencies..."
cd backend
if command -v python3 &> /dev/null; then
    python3 -m pip install -r requirements.txt
    print_status "Backend dependencies installed"
else
    print_error "Python 3 not found. Please install Python 3."
    exit 1
fi

cd ..

# Test Docker builds
print_info "Testing Docker builds..."
if command -v docker &> /dev/null; then
    print_info "Building backend Docker image..."
    if docker build -t fileconverter-backend ./backend; then
        print_status "Backend Docker build successful"
    else
        print_warning "Backend Docker build failed (this may be OK if dependencies are missing)"
    fi
    
    print_info "Building frontend Docker image..."
    if docker build -t fileconverter-frontend ./frontend; then
        print_status "Frontend Docker build successful"
    else
        print_warning "Frontend Docker build failed"
    fi
else
    print_warning "Docker not found. Docker builds will be tested in CI/CD pipeline."
fi

# Check git configuration
print_info "Checking git configuration..."
if git config user.name &> /dev/null && git config user.email &> /dev/null; then
    print_status "Git user configured"
else
    print_warning "Git user not configured. Please set up git config:"
    echo "  git config user.name 'Your Name'"
    echo "  git config user.email 'your.email@example.com'"
fi

# Create initial commit if needed
if [ -z "$(git log --oneline 2>/dev/null)" ]; then
    print_info "Creating initial commit..."
    git add .
    git commit -m "feat: initial deployment setup with complete CI/CD pipeline

- Add GitHub Actions workflows for CI/CD, security scanning, and performance monitoring
- Configure Dependabot for automated dependency updates
- Set up Docker containers for backend and frontend
- Add comprehensive security scanning (Bandit, Safety, Snyk, Trivy)
- Configure multi-environment deployment (staging/production)
- Add performance monitoring with Lighthouse and Artillery
- Set up auto-merge for Dependabot PRs
- Add health check endpoints and monitoring
- Configure Railway deployment
- Add GitHub Pages deployment for static demo"
    print_status "Initial commit created"
fi

# Display deployment checklist
echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Deployment Checklist:"
echo ""
echo "1. GitHub Repository Setup:"
echo "   - Push code to GitHub: git push origin main"
echo "   - Enable GitHub Pages in repository settings"
echo "   - Add required secrets in GitHub repository settings"
echo ""
echo "2. Required GitHub Secrets:"
echo "   - RAILWAY_TOKEN (for Railway deployment)"
echo "   - SONAR_TOKEN (for SonarCloud code quality)"
echo "   - SNYK_TOKEN (for security scanning)"
echo "   - SLACK_WEBHOOK_URL (optional, for notifications)"
echo ""
echo "3. External Services:"
echo "   - Sign up for Railway.app and connect your repository"
echo "   - Set up SonarCloud.io for code quality monitoring"
echo "   - Configure Snyk.io for security scanning"
echo ""
echo "4. Environment Setup:"
echo "   - Create staging and production environments in Railway"
echo "   - Configure environment variables from .env.example"
echo ""
echo "🌐 After deployment, your app will be available at:"
echo "   - Production: https://converter.imrajeshkumar7492.dev"
echo "   - Staging: https://staging-converter.imrajeshkumar7492.dev"
echo "   - GitHub Pages: https://imrajeshkumar7492.github.io/Converte-into-any-formate"
echo ""
echo "📚 For detailed setup instructions, see DEPLOYMENT_README.md"
echo ""
print_status "Ready for deployment! 🚀"