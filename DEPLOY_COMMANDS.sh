#!/bin/bash
# VoiceSense Deployment Commands Guide
# Run these commands to deploy to Vercel

set -e  # Exit on error

echo "🚀 VoiceSense Deployment Helper"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: vercel.json not found. Make sure you're in the project root."
    exit 1
fi

echo "✅ Project structure verified"
echo ""

# Check if git is configured
if [ ! -d ".git" ]; then
    echo "⚠️  No git repository found. Initialize with: git init"
    exit 1
fi

echo "✅ Git repository found"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required tools
echo "Checking dependencies..."
echo ""

if ! command_exists git; then
    echo "❌ Git is not installed"
    exit 1
fi
echo "✅ git installed"

if ! command_exists python3; then
    echo "❌ Python 3 is not installed"
    exit 1
fi
echo "✅ python3 installed"

echo ""
echo "================================"
echo "Pre-Deployment Checklist"
echo "================================"
echo ""

# Checklist
echo "Before deploying, verify:"
echo "  [ ] .env file is in .gitignore"
echo "  [ ] .env.example has placeholder values"
echo "  [ ] vercel.json is properly configured"
echo "  [ ] requirements.txt is up to date"
echo "  [ ] All features work locally"
echo "  [ ] Code is committed to git"
echo ""

read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

echo ""
echo "================================"
echo "Step 1: Verify Git Status"
echo "================================"
echo ""

git status

echo ""
echo "================================"
echo "Step 2: Check Environment Setup"
echo "================================"
echo ""

if [ -f ".env" ]; then
    echo "✅ .env file exists (make sure it's in .gitignore)"
    echo "  Checking .gitignore..."
    if grep -q "^\.env$" .gitignore; then
        echo "  ✅ .env is in .gitignore"
    else
        echo "  ⚠️  .env might not be in .gitignore. Run: echo '.env' >> .gitignore"
    fi
else
    echo "⚠️  .env file not found. Copy from .env.example:"
    echo "  cp .env.example .env"
fi

echo ""
echo "================================"
echo "Step 3: Push to GitHub"
echo "================================"
echo ""

read -p "Push changes to GitHub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add .
    git commit -m "Prepare VoiceSense for Vercel deployment"
    git push origin main
    echo "✅ Changes pushed to GitHub"
else
    echo "⚠️  Please push changes manually before deploying to Vercel"
fi

echo ""
echo "================================"
echo "Step 4: Deploy to Vercel"
echo "================================"
echo ""

echo "Next steps:"
echo ""
echo "1. Go to https://vercel.com"
echo "2. Click 'Import Project'"
echo "3. Select 'harshvortex/voicesense' from GitHub"
echo "4. Add environment variables:"
echo "   - SUPABASE_URL"
echo "   - SUPABASE_ANON_KEY"
echo "   - SUPABASE_SERVICE_ROLE_KEY"
echo "   - SUPABASE_JWT_SECRET"
echo "   - FLASK_SECRET_KEY"
echo "5. Click 'Deploy'"
echo ""

echo "================================"
echo "Local Testing (Optional)"
echo "================================"
echo ""

read -p "Test locally before deploying? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Setting up local environment..."
    echo ""
    
    # Create venv if doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate venv
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo "⚠️  Could not activate venv. Try manually:"
        echo "  source venv/bin/activate"
        exit 1
    fi
    
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    
    echo ""
    echo "✅ Setup complete! Run locally with:"
    echo "  python app.py"
    echo ""
    echo "Then visit: http://localhost:5000"
    echo ""
fi

echo ""
echo "================================"
echo "✅ Ready for Deployment!"
echo "================================"
echo ""
echo "Visit https://vercel.com to deploy."
echo ""
echo "Need help? Read DEPLOYMENT.md for detailed instructions."
echo ""
