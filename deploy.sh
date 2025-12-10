#!/bin/bash

# Deployment script for Weather Prediction Chat App

echo "🚀 Preparing deployment..."

# Check if model files exist
if [ ! -f "backend/checkpoint_best.pt" ]; then
    echo "⚠️  Warning: checkpoint_best.pt not found in backend/"
    echo "   Make sure to upload your trained model files"
fi

if [ ! -f "backend/daily_transformer_global.pt" ]; then
    echo "⚠️  Warning: daily_transformer_global.pt not found in backend/"
    echo "   Daily predictions will not be available"
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env not found"
    echo "   Copy backend/.env.example to backend/.env and add your GEMINI_API_KEY"
fi

# Build frontend to test
echo "🔨 Building frontend..."
cd frontend
npm install
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful"
else
    echo "❌ Frontend build failed"
    exit 1
fi

cd ..

# Test backend dependencies
echo "🔨 Testing backend dependencies..."
cd backend
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Backend dependencies installed successfully"
else
    echo "❌ Backend dependency installation failed"
    exit 1
fi

cd ..

echo "✅ Pre-deployment checks complete!"
echo ""
echo "Next steps:"
echo "1. Commit and push your changes to GitHub"
echo "2. Deploy to Railway:"
echo "   - Go to https://railway.app"
echo "   - Create new project from GitHub repo"
echo "   - Set GEMINI_API_KEY environment variable"
echo "3. Your app will be available at the Railway-provided URL"
echo ""
echo "For other deployment options, see DEPLOYMENT.md"