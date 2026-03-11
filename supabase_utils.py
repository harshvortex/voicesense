"""
Supabase Database Utilities for VoiceSense
Handles all database operations including authentication, profiles, and voice clips.
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from supabase import create_client, Client
from gotrue.errors import AuthApiError


class SupabaseManager:
    """Manager for Supabase database and storage operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables required")
        
        self.client: Client = create_client(self.url, self.key)
    
    # ────────────────────────────────────────────────────────────────────
    # Authentication Methods
    # ────────────────────────────────────────────────────────────────────
    
    def register_user(self, email: str, password: str, username: str, display_name: str = None) -> Tuple[bool, str]:
        """
        Register a new user with email and password.
        
        Args:
            email: User email address
            password: User password
            username: Unique username
            display_name: User's display name (optional)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Sign up user
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
            })
            
            user_id = response.user.id
            
            # Create user profile
            profile_data = {
                "id": user_id,
                "username": username,
                "display_name": display_name or username,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            self.client.table("user_profiles").insert(profile_data).execute()
            
            return True, f"User registered successfully. Check email to confirm."
            
        except AuthApiError as e:
            return False, f"Registration failed: {str(e)}"
        except Exception as e:
            return False, f"Error creating profile: {str(e)}"
    
    def login_user(self, email: str, password: str) -> Tuple[bool, Dict]:
        """
        Login user with email and password.
        
        Args:
            email: User email
            password: User password
        
        Returns:
            Tuple of (success: bool, data: dict with user/session info)
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            
            return True, {
                "user": response.user.model_dump(),
                "session": response.session.model_dump() if response.session else None
            }
        except AuthApiError as e:
            return False, {"error": str(e)}
        except Exception as e:
            return False, {"error": f"Login failed: {str(e)}"}
    
    def get_user_by_token(self, token: str) -> Tuple[bool, Dict]:
        """
        Get user info from access token.
        
        Args:
            token: JWT access token
        
        Returns:
            Tuple of (success: bool, user_data: dict)
        """
        try:
            response = self.client.auth.get_user(token)
            return True, response.user.model_dump()
        except Exception as e:
            return False, {"error": str(e)}
    
    def logout_user(self, token: str) -> Tuple[bool, str]:
        """
        Logout user by signing out.
        
        Args:
            token: Access token
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            self.client.auth.sign_out()
            return True, "Logged out successfully"
        except Exception as e:
            return False, f"Logout failed: {str(e)}"
    
    # ────────────────────────────────────────────────────────────────────
    # User Profile Methods
    # ────────────────────────────────────────────────────────────────────
    
    def get_user_profile(self, user_id: str) -> Tuple[bool, Dict]:
        """
        Get user profile by ID.
        
        Args:
            user_id: User ID (UUID)
        
        Returns:
            Tuple of (success: bool, profile: dict)
        """
        try:
            response = self.client.table("user_profiles").select("*").eq("id", user_id).single().execute()
            return True, response.data
        except Exception as e:
            return False, {"error": str(e)}
    
    def update_user_profile(self, user_id: str, updates: Dict) -> Tuple[bool, str]:
        """
        Update user profile.
        
        Args:
            user_id: User ID
            updates: Dictionary of fields to update
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            self.client.table("user_profiles").update(updates).eq("id", user_id).execute()
            return True, "Profile updated successfully"
        except Exception as e:
            return False, f"Failed to update profile: {str(e)}"
    
    def upload_avatar(self, user_id: str, file_content: bytes, filename: str) -> Tuple[bool, str]:
        """
        Upload user avatar to Supabase Storage.
        
        Args:
            user_id: User ID
            file_content: File bytes
            filename: Original filename
        
        Returns:
            Tuple of (success: bool, url_or_error: str)
        """
        try:
            bucket_name = "avatars"
            file_path = f"{user_id}/{filename}"
            
            # Upload file
            self.client.storage.from_(bucket_name).upload(file_path, file_content)
            
            # Get public URL
            url = self.client.storage.from_(bucket_name).get_public_url(file_path)
            
            # Update profile
            self.update_user_profile(user_id, {"avatar_url": url})
            
            return True, url
        except Exception as e:
            return False, f"Avatar upload failed: {str(e)}"
    
    # ────────────────────────────────────────────────────────────────────
    # Voice Clip Methods
    # ────────────────────────────────────────────────────────────────────
    
    def save_voice_clip(self, user_id: str, filename: str, original_filename: str, 
                       file_size: int, file_type: str, storage_path: str,
                       transcription: str = None, sentiment: str = None,
                       sentiment_score: float = None, confidence_score: float = None,
                       emotions: Dict = None) -> Tuple[bool, str]:
        """
        Save voice clip metadata to database.
        
        Args:
            user_id: User ID
            filename: Generated filename
            original_filename: Original filename
            file_size: File size in bytes
            file_type: Audio format (wav, mp3, aac, etc.)
            storage_path: Path in Supabase Storage
            transcription: Transcribed text (optional)
            sentiment: Sentiment label (positive, negative, neutral)
            sentiment_score: Sentiment score (-1 to 1)
            confidence_score: Confidence of analysis
            emotions: JSON object with emotion scores
        
        Returns:
            Tuple of (success: bool, clip_id_or_error: str)
        """
        try:
            clip_data = {
                "user_id": user_id,
                "filename": filename,
                "original_filename": original_filename,
                "file_size": file_size,
                "file_type": file_type,
                "storage_path": storage_path,
                "transcription": transcription,
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "confidence_score": confidence_score,
                "emotions": emotions or {},
                "created_at": datetime.utcnow().isoformat(),
            }
            
            response = self.client.table("voice_clips").insert(clip_data).execute()
            clip_id = response.data[0]["id"]
            
            return True, clip_id
        except Exception as e:
            return False, f"Failed to save clip metadata: {str(e)}"
    
    def get_user_voice_clips(self, user_id: str, limit: int = 50, offset: int = 0) -> Tuple[bool, List[Dict]]:
        """
        Get user's voice clips with pagination.
        
        Args:
            user_id: User ID
            limit: Number of clips to fetch
            offset: Pagination offset
        
        Returns:
            Tuple of (success: bool, clips: list)
        """
        try:
            response = (self.client.table("voice_clips")
                       .select("*")
                       .eq("user_id", user_id)
                       .order("created_at", desc=True)
                       .range(offset, offset + limit - 1)
                       .execute())
            return True, response.data
        except Exception as e:
            return False, []
    
    def delete_voice_clip(self, clip_id: str, user_id: str) -> Tuple[bool, str]:
        """
        Delete a voice clip and associated file.
        
        Args:
            clip_id: Clip ID
            user_id: User ID (for verification)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Get clip info
            response = self.client.table("voice_clips").select("storage_path").eq("id", clip_id).single().execute()
            storage_path = response.data["storage_path"]
            
            # Delete from storage
            self.client.storage.from_("voice-clips").remove([storage_path])
            
            # Delete from database
            self.client.table("voice_clips").delete().eq("id", clip_id).eq("user_id", user_id).execute()
            
            return True, "Clip deleted successfully"
        except Exception as e:
            return False, f"Failed to delete clip: {str(e)}"
    
    def get_user_statistics(self, user_id: str) -> Tuple[bool, Dict]:
        """
        Get user's statistics.
        
        Args:
            user_id: User ID
        
        Returns:
            Tuple of (success: bool, stats: dict)
        """
        try:
            # Get clips
            response = self.client.table("voice_clips").select("*").eq("user_id", user_id).execute()
            clips = response.data
            
            # Calculate statistics
            total_clips = len(clips)
            total_duration = sum(c.get("duration_seconds", 0) for c in clips if c.get("duration_seconds"))
            
            sentiments = {}
            for clip in clips:
                sentiment = clip.get("sentiment", "unknown")
                sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
            
            stats = {
                "total_clips_analyzed": total_clips,
                "total_duration_seconds": total_duration,
                "sentiment_distribution": sentiments,
                "recent_clips": clips[:5],
            }
            
            return True, stats
        except Exception as e:
            return False, {"error": str(e)}
    
    # ────────────────────────────────────────────────────────────────────
    # Storage Methods
    # ────────────────────────────────────────────────────────────────────
    
    def upload_voice_clip(self, user_id: str, file_content: bytes, filename: str) -> Tuple[bool, str]:
        """
        Upload voice clip to Supabase Storage.
        
        Args:
            user_id: User ID
            file_content: File bytes
            filename: Filename
        
        Returns:
            Tuple of (success: bool, storage_path_or_error: str)
        """
        try:
            bucket_name = "voice-clips"
            file_path = f"{user_id}/{filename}"
            
            self.client.storage.from_(bucket_name).upload(file_path, file_content)
            
            return True, file_path
        except Exception as e:
            return False, f"Upload failed: {str(e)}"
    
    def get_clip_download_url(self, storage_path: str) -> Tuple[bool, str]:
        """
        Get signed download URL for a voice clip.
        
        Args:
            storage_path: Path in storage
        
        Returns:
            Tuple of (success: bool, url_or_error: str)
        """
        try:
            url = self.client.storage.from_("voice-clips").create_signed_url(storage_path, 3600)
            return True, url
        except Exception as e:
            return False, str(e)


# Create singleton instance
_supabase_manager = None


def get_supabase_manager() -> SupabaseManager:
    """Get or create Supabase manager instance."""
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseManager()
    return _supabase_manager
