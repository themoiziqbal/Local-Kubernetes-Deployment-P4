# Vercel Deployment Guide

## Quick Setup

### 1. Environment Variables (IMPORTANT!)

In Vercel dashboard, add this environment variable:

```
Name: OPENAI_API_KEY
Value: your-openai-api-key-here
```

**Without this, the chatbot will not work!**

### 2. Deploy

Push to GitHub and Vercel will automatically deploy.

## How It Works

### Serverless Architecture

This Vercel deployment uses a simplified, serverless-friendly version:

- **Lightweight**: Only essential dependencies (FastAPI, OpenAI)
- **No Audio**: Voice features removed (serverless doesn't support audio)
- **In-Memory Storage**: Todos stored in memory (no SQLite)
- **Stateless**: Each request is independent

### ⚠️ Important Limitations

**Data Persistence:**
- Todos are stored in memory
- Data resets on each deployment
- Not suitable for production use with persistent data

**Recommended Setup:**
- **Frontend**: GitHub Pages ✅
- **Backend**: Railway (not Vercel) ✅
  - Railway supports persistent storage
  - SQLite database works properly
  - All features available

## Files Structure

```
api/
  index.py          # Simplified serverless app
  __init__.py

requirements.txt    # Minimal deps for Vercel
requirements.full.txt  # Full deps for local/Railway
vercel.json        # Vercel configuration
.vercelignore      # Files to exclude from deployment
```

## Testing

After deployment, test these endpoints:

```bash
# Health check
https://your-app.vercel.app/

# Get todos
https://your-app.vercel.app/api/todos

# Chat (POST request)
https://your-app.vercel.app/api/chat
```

## Troubleshooting

### Build Fails

**Error**: "No fastapi entrypoint found"
- **Fix**: Make sure `api/index.py` exists

**Error**: "Module not found"
- **Fix**: Check `requirements.txt` has all needed packages

**Error**: "Deployment size exceeded"
- **Fix**: Make sure `.vercelignore` is properly excluding heavy files

### Runtime Errors

**Error**: "OpenAI API key not configured"
- **Fix**: Add `OPENAI_API_KEY` in Vercel environment variables

**Error**: "Todos not persisting"
- **This is expected**: Vercel is stateless. Use Railway for persistence.

## For Local Development

Use the full version with all features:

```bash
# Install full dependencies
pip install -r requirements.full.txt

# Run locally
python run_server.py
```

## Recommended Production Setup

**Best Architecture:**

1. **Frontend**: GitHub Pages
   - Serves HTML, CSS, JS
   - Free, fast CDN
   - URL: `https://yourusername.github.io/ChatbotTodoApp/`

2. **Backend**: Railway (NOT Vercel)
   - Full Python environment
   - Persistent SQLite database
   - All features work
   - URL: `https://your-app.railway.app`

3. **Update script.js**:
   ```javascript
   const BACKEND_URL = 'https://your-app.railway.app';
   ```

## Why Railway Over Vercel for Backend?

| Feature | Vercel | Railway |
|---------|--------|---------|
| Serverless | ✅ Yes | ❌ No |
| Persistent Storage | ❌ No | ✅ Yes |
| Audio Processing | ❌ No | ✅ Yes |
| Long-running Process | ❌ Limited | ✅ Yes |
| SQLite Database | ❌ No | ✅ Yes |
| **Recommendation** | Frontend only | ✅ Backend |

## Support

For issues:
1. Check environment variables are set
2. Review build logs in Vercel dashboard
3. Test endpoints individually
4. Consider Railway for full features
