# VoiceSense Deployment Guide

Complete guide to deploying VoiceSense to Vercel with Supabase integration.

## Prerequisites

- Vercel account with connected GitHub repository
- Supabase project created and configured
- Database tables set up (see SETUP_GUIDE.md)
- Supabase credentials (URL, Anon Key, Service Role Key)

## Environment Variables Setup

### 1. Add Environment Variables to Vercel

Go to your Vercel project settings → Environment Variables and add:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-jwt-secret-from-supabase
FLASK_SECRET_KEY=generate-a-secure-random-key-here
DEMO_MODE=true
FLASK_ENV=production
```

### 2. Generate FLASK_SECRET_KEY

Generate a secure random key using Python:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and add it as `FLASK_SECRET_KEY` in Vercel.

### 3. Get Supabase Credentials

1. Go to Supabase project dashboard
2. Settings → API → Copy:
   - `Project URL` → SUPABASE_URL
   - `anon public` key → SUPABASE_ANON_KEY
   - `service_role secret` key → SUPABASE_SERVICE_ROLE_KEY
3. Settings → Database → JWT secret → SUPABASE_JWT_SECRET

## Deployment Steps

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Add auth and PWA features for Vercel deployment"
git push origin main
```

### Step 2: Connect to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Import project from GitHub
3. Select `voicesense` repository
4. Vercel will auto-detect Flask configuration
5. Add environment variables (see above)
6. Deploy

### Step 3: Verify Deployment

1. Wait for build to complete
2. Visit your deployed site at `https://voicesense-xxx.vercel.app`
3. Test login/register functionality
4. Upload a test audio file

## Troubleshooting

### "SUPABASE_URL and SUPABASE_ANON_KEY not set"

**Solution:** Ensure environment variables are added to Vercel project settings, not just locally in .env file.

### Session/Authentication Issues

**Cause:** Flask uses secure cookies for sessions, which requires HTTPS in production.

**Solution:** Vercel provides HTTPS automatically. If testing locally, set `SESSION_COOKIE_SECURE=False` in development.

### Database Connection Errors

**Cause:** Database tables don't exist or Supabase credentials are wrong.

**Solution:** 
1. Run the SQL migration script in Supabase SQL Editor
2. Verify credentials in environment variables
3. Check Supabase project is in active status

### Cold Start Issues

**Cause:** First request to Vercel function takes longer to load dependencies.

**Solution:** This is normal for serverless. Subsequent requests are faster. Consider upgrading to Pro plan for faster cold starts.

### Static Files Not Loading

**Cause:** Static files route not configured correctly.

**Solution:** Vercel.json already handles this. If issues persist, clear Vercel cache and redeploy.

## Performance Optimization

### 1. Enable Caching

Static assets have 1-hour cache enabled in vercel.json. Update as needed:

```json
"Cache-Control": "public, max-age=3600, immutable"
```

### 2. Optimize Database Queries

- Use indexes on frequently queried columns
- Implement pagination for voice clip history
- Cache user profiles for 5-10 minutes

### 3. Image Optimization

- Store avatars in Supabase Storage
- Use WebP format when possible
- Compress images before upload

## Security Checklist

- [ ] Set strong `FLASK_SECRET_KEY`
- [ ] Enable HTTPS (automatic on Vercel)
- [ ] Set Supabase JWT secret
- [ ] Enable RLS policies in Supabase (already configured)
- [ ] Review CORS settings
- [ ] Monitor error logs in Vercel dashboard
- [ ] Set up email verification in Supabase Auth

## Database Backup

VoiceSense data is stored in Supabase. To backup:

1. Go to Supabase project dashboard
2. Settings → Backups
3. Enable automated daily backups
4. Download manual backups as needed

## Monitoring

### Vercel Analytics

1. Go to Vercel project dashboard
2. Analytics tab shows:
   - Request count
   - Response time
   - Error rate

### Supabase Monitoring

1. Go to Supabase project dashboard
2. Logs tab shows:
   - Database queries
   - Authentication events
   - API calls

## Scaling

As your app grows:

1. **Upgrade Vercel Plan:** Pro plan includes better cold start performance
2. **Upgrade Supabase Plan:** Increase database connection limits
3. **Add CDN:** Enable Vercel's CDN for faster asset delivery
4. **Database Indexes:** Add indexes to frequently queried columns

## Rollback Procedure

If deployment breaks:

1. Go to Vercel project dashboard
2. Deployments tab
3. Click previous stable deployment
4. Click "Promote to Production"

## Next Steps

1. Monitor error logs for first 24 hours
2. Gather user feedback
3. Plan feature improvements
4. Set up monitoring alerts

## Support

For issues:
- Check Vercel logs: Project → Deployments → Logs
- Check Supabase logs: Project → Logs
- Review error messages in application

## Additional Resources

- [Vercel Docs](https://vercel.com/docs)
- [Supabase Docs](https://supabase.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [VoiceSense GitHub](https://github.com/harshvortex/voicesense)
