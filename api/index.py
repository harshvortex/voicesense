"""Vercel serverless function entry point."""
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force demo mode on Vercel (ML deps are too large for serverless)
os.environ.setdefault('DEMO_MODE', 'true')

from app import app
