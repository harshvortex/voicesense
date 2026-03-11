# VoiceSense Quick Start Guide

## 5-Minute Setup

### 1. Get Supabase Credentials (2 min)
1. Sign up at supabase.com
2. Create a project
3. Go to Settings → API
4. Copy **Project URL** and **anon public** key

### 2. Create Database (1 min)
1. In Supabase, open SQL Editor
2. Copy-paste contents of `scripts/01-init-db.sql`
3. Click "Run"

### 3. Create Storage Buckets (1 min)
In Supabase Storage:
1. Create bucket named `avatars` (public)
2. Create bucket named `voice-clips` (public)

### 4. Set Environment Variables (1 min)
Create `.env` file in project root:
```
SUPABASE_URL=your_url_here
SUPABASE_ANON_KEY=your_key_here
FLASK_SECRET_KEY=any-random-string-here
DEMO_MODE=false
```

### 5. Install & Run (1 min)
```bash
pip install -r requirements.txt
python app.py
```

Visit: `http://localhost:8000`

---

## Key URLs

### User Pages
- **Register** → `/register`
- **Login** → `/login`
- **Dashboard** → `/dashboard` (requires login)
- **History** → `/history` (requires login)
- **Profile** → `/profile` (requires login)

### API Endpoints
- **Analyze Audio** → `POST /analyze`
- **Get Clips** → `GET /api/clips`
- **Delete Clip** → `DELETE /api/clips/{id}`
- **Get Profile** → `GET /api/profile`
- **Update Profile** → `PUT /api/profile`
- **Upload Avatar** → `POST /api/profile/avatar`
- **Get Stats** → `GET /api/statistics`

---

## Supported Audio Formats

- AAC (new!)
- MP3
- WAV
- M4A
- OGG
- FLAC
- WebM
- WMA

---

## User Features

### Register & Login
- Email/password authentication
- Profile creation
- Session management

### Dashboard
- Drag-and-drop audio upload
- Real-time analysis
- Sentiment visualization
- Transcription display

### History
- View all analyzed clips
- Search by filename/content
- Filter by sentiment
- Delete clips

### Profile
- Avatar upload
- Personal information
- Statistics (total clips, sentiment breakdown)
- Account preferences
- Privacy settings
- Data retention options

---

## Database Tables

### user_profiles
```
id, username, display_name, bio, avatar_url,
theme, language, notifications_enabled,
data_retention_days, is_private, created_at, updated_at
```

### voice_clips
```
id, user_id, filename, original_filename, file_size,
file_type, storage_path, duration_seconds,
transcription, sentiment, sentiment_score,
confidence_score, emotions, created_at
```

---

## Common Issues

### "Module not found: supabase"
```bash
pip install supabase
```

### "SUPABASE_URL not found"
1. Check `.env` file exists
2. File must be in project root
3. Restart Flask after editing

### "Storage bucket not found"
1. Create `avatars` bucket in Supabase
2. Create `voice-clips` bucket
3. Set both to public

### "Upload fails with 403"
Storage bucket policies might be missing. Use SQL editor to set:
```sql
CREATE POLICY "allow public insert"
ON storage.objects
FOR INSERT TO authenticated
WITH CHECK (true);
```

---

## Production Checklist

- [ ] Change `FLASK_SECRET_KEY` to secure random value
- [ ] Set `FLASK_DEBUG=false`
- [ ] Set `DEMO_MODE=false`
- [ ] Enable HTTPS
- [ ] Configure CORS origins
- [ ] Set up database backups
- [ ] Review Supabase RLS policies
- [ ] Test all features on mobile
- [ ] Set up error logging

---

## File Guide

| File | Purpose |
|------|---------|
| `app.py` | Main Flask app with routes |
| `auth_utils.py` | Authentication & session management |
| `supabase_utils.py` | Database operations |
| `templates/*.html` | User interface pages |
| `static/css/*.css` | Styling for all pages |
| `scripts/01-init-db.sql` | Database schema |
| `SETUP_GUIDE.md` | Detailed setup instructions |
| `IMPLEMENTATION_SUMMARY.md` | Technical overview |

---

## What You Get

✓ User registration & login  
✓ Voice clip analysis & history  
✓ Profile management with avatar  
✓ Statistics dashboard  
✓ AAC file support  
✓ Supabase integration  
✓ Progressive Web App  
✓ Mobile responsive design  
✓ Security best practices  

---

## Next: Deploy!

Ready to deploy? Check:
1. All environment variables set
2. Database tables created
3. Storage buckets created
4. Test locally first
5. Deploy to Vercel or your server

Enjoy VoiceSense!
