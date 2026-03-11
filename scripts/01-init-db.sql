-- ================================================================================
-- VoiceSense Database Schema Initialization
-- ================================================================================
-- This script creates tables for user authentication, profiles, and voice clips
-- with Row Level Security (RLS) enabled for data privacy.

-- ================================================================================
-- 1. User Profiles Table
-- ================================================================================
-- Extends Supabase Auth with additional user information
CREATE TABLE IF NOT EXISTS public.user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username TEXT UNIQUE NOT NULL,
  display_name TEXT,
  bio TEXT,
  avatar_url TEXT,
  avatar_bucket TEXT DEFAULT 'avatars',
  theme TEXT DEFAULT 'dark',
  language TEXT DEFAULT 'en',
  notifications_enabled BOOLEAN DEFAULT TRUE,
  data_retention_days INTEGER DEFAULT 90,
  is_private BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster username lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_username ON public.user_profiles(username);

-- ================================================================================
-- 2. Voice Clips Table
-- ================================================================================
-- Stores metadata about analyzed voice clips
CREATE TABLE IF NOT EXISTS public.voice_clips (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  original_filename TEXT,
  file_size INTEGER,
  file_type TEXT DEFAULT 'wav',
  storage_path TEXT NOT NULL,
  duration_seconds FLOAT,
  
  -- Analysis Results
  transcription TEXT,
  sentiment TEXT,
  sentiment_score FLOAT,
  confidence_score FLOAT,
  emotions JSONB DEFAULT '{}',
  
  -- Metadata
  uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  analyzed_at TIMESTAMP WITH TIME ZONE,
  expires_at TIMESTAMP WITH TIME ZONE,
  is_deleted BOOLEAN DEFAULT FALSE,
  is_public BOOLEAN DEFAULT FALSE,
  
  -- Tags & Notes
  tags TEXT[] DEFAULT '{}',
  notes TEXT,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_voice_clips_user_id ON public.voice_clips(user_id);
CREATE INDEX IF NOT EXISTS idx_voice_clips_uploaded_at ON public.voice_clips(uploaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_voice_clips_sentiment ON public.voice_clips(sentiment);
CREATE INDEX IF NOT EXISTS idx_voice_clips_user_uploaded ON public.voice_clips(user_id, uploaded_at DESC);

-- ================================================================================
-- 3. User Statistics Table
-- ================================================================================
-- Stores aggregated stats for user profiles
CREATE TABLE IF NOT EXISTS public.user_statistics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  total_clips_analyzed INTEGER DEFAULT 0,
  total_duration_minutes FLOAT DEFAULT 0,
  positive_sentiment_count INTEGER DEFAULT 0,
  neutral_sentiment_count INTEGER DEFAULT 0,
  negative_sentiment_count INTEGER DEFAULT 0,
  average_confidence FLOAT DEFAULT 0,
  last_analysis_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_statistics_user_id ON public.user_statistics(user_id);

-- ================================================================================
-- 4. Row Level Security (RLS) Policies
-- ================================================================================

-- Enable RLS on all tables
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.voice_clips ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_statistics ENABLE ROW LEVEL SECURITY;

-- User Profiles Policies
CREATE POLICY "Users can read their own profile"
  ON public.user_profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can read public profiles"
  ON public.user_profiles FOR SELECT
  USING (id IS NOT NULL);

CREATE POLICY "Users can update their own profile"
  ON public.user_profiles FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can insert their own profile"
  ON public.user_profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

-- Voice Clips Policies
CREATE POLICY "Users can read their own voice clips"
  ON public.voice_clips FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own voice clips"
  ON public.voice_clips FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own voice clips"
  ON public.voice_clips FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own voice clips"
  ON public.voice_clips FOR DELETE
  USING (auth.uid() = user_id);

-- User Statistics Policies
CREATE POLICY "Users can read their own statistics"
  ON public.user_statistics FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own statistics"
  ON public.user_statistics FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can insert their own statistics"
  ON public.user_statistics FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- ================================================================================
-- 5. Functions & Triggers
-- ================================================================================

-- Function to update user_profiles timestamp
CREATE OR REPLACE FUNCTION public.update_user_profiles_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for user_profiles updated_at
DROP TRIGGER IF EXISTS user_profiles_update_timestamp ON public.user_profiles;
CREATE TRIGGER user_profiles_update_timestamp
  BEFORE UPDATE ON public.user_profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.update_user_profiles_timestamp();

-- Function to update voice_clips timestamp
CREATE OR REPLACE FUNCTION public.update_voice_clips_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for voice_clips updated_at
DROP TRIGGER IF EXISTS voice_clips_update_timestamp ON public.voice_clips;
CREATE TRIGGER voice_clips_update_timestamp
  BEFORE UPDATE ON public.voice_clips
  FOR EACH ROW
  EXECUTE FUNCTION public.update_voice_clips_timestamp();

-- Function to update user_statistics timestamp
CREATE OR REPLACE FUNCTION public.update_user_statistics_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for user_statistics updated_at
DROP TRIGGER IF EXISTS user_statistics_update_timestamp ON public.user_statistics;
CREATE TRIGGER user_statistics_update_timestamp
  BEFORE UPDATE ON public.user_statistics
  FOR EACH ROW
  EXECUTE FUNCTION public.update_user_statistics_timestamp();

-- Function to handle new user creation (creates profile and stats)
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (id, username, display_name)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'username', 'user_' || SUBSTRING(NEW.id::TEXT, 1, 8)),
    COALESCE(NEW.raw_user_meta_data->>'display_name', NEW.email)
  )
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO public.user_statistics (user_id)
  VALUES (NEW.id)
  ON CONFLICT (user_id) DO NOTHING;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile and stats on new user
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- ================================================================================
-- 6. Storage Buckets Configuration
-- ================================================================================
-- Create storage buckets for audio files and avatars
BEGIN
  INSERT INTO storage.buckets (id, name, public)
  VALUES ('voice-clips', 'voice-clips', false)
  ON CONFLICT DO NOTHING;
EXCEPTION WHEN OTHERS THEN
  NULL;
END;

BEGIN
  INSERT INTO storage.buckets (id, name, public)
  VALUES ('avatars', 'avatars', true)
  ON CONFLICT DO NOTHING;
EXCEPTION WHEN OTHERS THEN
  NULL;
END;

-- Policies for voice-clips bucket (private)
CREATE POLICY "Users can upload their own voice clips"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id = 'voice-clips' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can read their own voice clips"
  ON storage.objects FOR SELECT
  USING (
    bucket_id = 'voice-clips' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can delete their own voice clips"
  ON storage.objects FOR DELETE
  USING (
    bucket_id = 'voice-clips' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- Policies for avatars bucket (public)
CREATE POLICY "Users can upload their own avatar"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id = 'avatars' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Anyone can view avatars"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'avatars');

CREATE POLICY "Users can delete their own avatar"
  ON storage.objects FOR DELETE
  USING (
    bucket_id = 'avatars' AND
    auth.uid()::text = (storage.foldername(name))[1]
  );

-- ================================================================================
-- End of Schema Initialization
-- ================================================================================
