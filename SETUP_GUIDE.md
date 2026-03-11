# VoiceSense Setup Guide

## Features Added

This guide covers the new features added to VoiceSense:

### 1. **User Authentication**
- Email/password registration and login
- Supabase Auth integration
- Secure session management
- Protected routes with automatic redirect

### 2. **Voice Clip History**
- Upload and analyze audio files (MP3, WAV, AAC, M4A, OGG, FLAC, WebM, WMA)
- Store clips in Supabase Storage
- Search and filter clips by sentiment
- Delete clips from history
- View detailed clip information

### 3. **User Profiles**
- Customizable profile with avatar upload
- Personal statistics dashboard
- Account settings and preferences
- Privacy controls
- Data retention options

### 4. **Progressive Web App (PWA)**
- Install as native app on phones, tablets, and desktops
- Offline support with service worker
- App icons and splash screens

## Prerequisites

- Python 3.8+
- Supabase account (free tier available at supabase.com)
- Flask and dependencies (see requirements.txt)

## Setup Instructions

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create an account
2. Click "New Project"
3. Enter project name and password
4. Select a region close to you
5. Wait for project to initialize

### Step 2: Get Supabase Credentials

1. In your Supabase project, go to Settings → API
2. Copy the following values:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_ANON_KEY`
   - **service_role** secret → `SUPABASE_SERVICE_KEY` (for migrations, if needed)

### Step 3: Create Database Tables

Copy and paste the SQL from `/scripts/01-init-db.sql` into Supabase SQL Editor:

1. In Supabase dashboard, go to SQL Editor
2. Click "New Query"
3. Paste the entire content of `scripts/01-init-db.sql`
4. Click "Run"

This creates:
- `user_profiles` - Extended user information
- `voice_clips` - Analyzed audio metadata
- `user_statistics` - Aggregated user stats

### Step 4: Create Storage Buckets

In Supabase, go to Storage and create two public buckets:

#### Bucket 1: `avatars`
- Policy: Allow authenticated users to upload to their own folder
```sql
-- Upload policy
CREATE POLICY "Users can upload their own avatars"
ON storage.objects
FOR INSERT
WITH CHECK (
  auth.uid()::text = (storage.foldername(name))[1]
);

-- Download policy
CREATE POLICY "Avatars are publicly accessible"
ON storage.objects
FOR SELECT
USING (bucket_id = 'avatars');
```

#### Bucket 2: `voice-clips`
- Policy: Allow authenticated users to upload and access their clips
```sql
-- Upload policy
CREATE POLICY "Users can upload their own clips"
ON storage.objects
FOR INSERT
WITH CHECK (
  auth.uid()::text = (storage.foldername(name))[1]
);

-- Download policy
CREATE POLICY "Users can download their own clips"
ON storage.objects
FOR SELECT
USING (
  auth.uid()::text = (storage.foldername(name))[1]
);
```

### Step 5: Set Environment Variables

Create a `.env` file in the project root:

```bash
# Supabase
SUPABASE_URL=your_project_url
SUPABASE_ANON_KEY=your_anon_key

# Flask
FLASK_SECRET_KEY=your-random-secret-key-change-in-production
FLASK_DEBUG=false

# Models (optional)
WHISPER_MODEL=base
SENTIMENT_MODEL=distilbert-base-uncased-finetuned-sst-2-english

# Demo Mode (set to false for production)
DEMO_MODE=false
```

### Step 6: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 7: Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

## File Structure

```
voicesense/
├── app.py                           # Main Flask application
├── auth_utils.py                    # Authentication utilities
├── supabase_utils.py               # Supabase database operations
├── config.py                        # Configuration settings
├── requirements.txt                 # Python dependencies
│
├── templates/
│   ├── index.html                  # Original landing page
│   ├── login.html                  # Login page
│   ├── register.html               # Registration page
│   ├── dashboard.html              # Audio analysis dashboard
│   ├── history.html                # Voice clip history
│   └── profile.html                # User profile & settings
│
├── static/
│   ├── css/
│   │   ├── style.css              # Base styles
│   │   ├── auth.css               # Authentication pages
│   │   ├── dashboard.css          # Dashboard & navbar
│   │   ├── history.css            # History page
│   │   └── profile.css            # Profile page
│   ├── js/
│   │   └── service-worker.js      # PWA offline support
│   ├── icons/
│   │   ├── icon-192.png           # App icon (192x192)
│   │   ├── icon-512.png           # App icon (512x512)
│   │   ├── icon-192-maskable.png  # Maskable icon
│   │   └── icon-512-maskable.png  # Maskable icon
│   └── screenshots/
│       ├── screenshot-540.png     # Mobile screenshot
│       └── screenshot-1280.png    # Desktop screenshot
│
└── scripts/
    └── 01-init-db.sql             # Database initialization
```

## Database Schema

### user_profiles
```
id (UUID, PRIMARY KEY)
username (TEXT, UNIQUE)
display_name (TEXT)
bio (TEXT)
avatar_url (TEXT)
theme (TEXT, default: 'dark')
language (TEXT, default: 'en')
notifications_enabled (BOOLEAN, default: true)
data_retention_days (INTEGER, default: 90)
is_private (BOOLEAN, default: false)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### voice_clips
```
id (UUID, PRIMARY KEY)
user_id (UUID, FOREIGN KEY)
filename (TEXT)
original_filename (TEXT)
file_size (INTEGER)
file_type (TEXT)
storage_path (TEXT)
duration_seconds (FLOAT)
transcription (TEXT)
sentiment (TEXT)
sentiment_score (FLOAT)
confidence_score (FLOAT)
emotions (JSONB)
created_at (TIMESTAMP)
```

## API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login user
- `POST /logout` - Logout user

### Voice Analysis
- `POST /analyze` - Analyze audio file (authenticated)
- `GET /api/clips` - Get user's voice clips
- `DELETE /api/clips/<clip_id>` - Delete a clip

### Profile
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update profile
- `POST /api/profile/avatar` - Upload avatar
- `GET /api/statistics` - Get user statistics

## Security Features

1. **Authentication**
   - Supabase Auth with email verification
   - Session-based authentication
   - Secure password hashing

2. **Authorization**
   - Row Level Security (RLS) on all tables
   - Users can only access their own data
   - Protected API endpoints

3. **Data Protection**
   - HTTPS in production
   - Secure cookies (HTTP-only)
   - CORS protection
   - Input validation

## AAC File Support

The application now supports AAC audio files in addition to:
- MP3
- WAV
- M4A
- OGG
- FLAC
- WebM
- WMA

This is automatically handled by OpenAI Whisper's transcription pipeline.

## Troubleshooting

### "SUPABASE_URL is not set"
Make sure your `.env` file has the correct Supabase URL and the file is in the project root directory.

### "Failed to create table"
The SQL migration might have failed. Check the error message and ensure:
1. You're using the correct Supabase project
2. The SQL syntax is correct
3. You have permission to create tables

### "Upload failed"
Make sure:
1. Storage buckets exist (`avatars` and `voice-clips`)
2. Bucket policies are configured correctly
3. File size is within limits

### PWA not installing
Make sure:
1. You're accessing over HTTPS (or localhost)
2. manifest.json is being served correctly
3. Service worker is registered in browser DevTools

## Production Deployment

### Environment Variables
Set these in your production environment:
```
SUPABASE_URL=your_production_url
SUPABASE_ANON_KEY=your_production_key
FLASK_SECRET_KEY=your-secure-random-key
FLASK_DEBUG=false
DEMO_MODE=false
```

### Security Checklist
- [ ] Change `FLASK_SECRET_KEY` to a secure random value
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS appropriately
- [ ] Set up regular database backups
- [ ] Enable RLS on all tables
- [ ] Review Supabase security policies
- [ ] Set up monitoring and logging

## Support

For issues with:
- **Supabase**: https://supabase.com/docs
- **Flask**: https://flask.palletsprojects.com
- **OpenAI Whisper**: https://github.com/openai/whisper

## License

This project uses:
- OpenAI Whisper (MIT License)
- HuggingFace Transformers (Apache 2.0)
- Flask (BSD License)
- Supabase (Apache 2.0)
