"""
Authentication Utilities for VoiceSense
Handles session management, token validation, and auth middleware.
"""

import os
import json
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify, session, redirect, url_for
from supabase_utils import get_supabase_manager


class AuthManager:
    """Manager for authentication and session handling."""
    
    def __init__(self):
        """Initialize auth manager."""
        self.supabase = get_supabase_manager()
        self.session_timeout = 24 * 60 * 60  # 24 hours
    
    def set_session(self, user_data: dict, session_data: dict):
        """
        Set user session.
        
        Args:
            user_data: User information
            session_data: Session/token information
        """
        session['user_id'] = user_data.get('id')
        session['email'] = user_data.get('email')
        session['access_token'] = session_data.get('access_token') if session_data else None
        session['logged_in'] = True
        session.permanent = True
    
    def clear_session(self):
        """Clear user session."""
        session.clear()
    
    def get_current_user(self) -> dict:
        """
        Get current user from session.
        
        Returns:
            User data or None if not logged in
        """
        if 'user_id' in session:
            return {
                'id': session.get('user_id'),
                'email': session.get('email'),
            }
        return None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return session.get('logged_in', False)
    
    def get_token_from_request(self) -> str:
        """
        Extract JWT token from request headers.
        
        Returns:
            Token or None
        """
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        return None


def auth_required(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_manager = AuthManager()
        
        if not auth_manager.is_authenticated():
            # For API endpoints, return JSON error
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized'}), 401
            # For web pages, redirect to login
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def api_auth_required(f):
    """Decorator to require authentication for API endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_manager = AuthManager()
        token = auth_manager.get_token_from_request()
        
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        
        # Verify token with Supabase
        success, user_data = auth_manager.supabase.get_user_by_token(token)
        
        if not success:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Store user info in request context
        request.user = user_data
        
        return f(*args, **kwargs)
    
    return decorated_function


# Create singleton instance
_auth_manager = None


def get_auth_manager() -> AuthManager:
    """Get or create auth manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager
