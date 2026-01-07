# Deployment Guide: Chatbot Todo App

This guide provides step-by-step instructions for deploying the Chatbot Todo App with:
- Frontend on GitHub Pages
- Backend on Railway

## Architecture Overview

```
Internet → GitHub Pages (Frontend) → Railway (Backend) → OpenAI API
```

## Prerequisites

- GitHub account with admin access to the repository
- Railway account ([https://railway.app](https://railway.app))
- OpenAI API key
- Git and GitHub repository access

## Deployment Steps

### 1. Backend Deployment (Railway)

#### Step 1A: Prepare Railway Account
1. Go to [https://railway.app](https://railway.app)
2. Sign in with your GitHub account or create a new account
3. Verify your account if required

#### Step 1B: Deploy Backend
1. Click "New Project" in the Railway dashboard
2. Select "Deploy from GitHub"
3. Choose your repository: `Syedabanog-1/ChatbotTodoApp`
4. Click "Deploy"

#### Step 1C: Configure Environment Variables
1. In your Railway project, go to "Settings" → "Variables"
2. Add the following environment variable:
   - `OPENAI_API_KEY` = your OpenAI API key
3. Save the changes
4. The application will automatically redeploy with the new variables

#### Step 1D: Get Backend URL
1. In your Railway dashboard, note the "Railway URL" (e.g., `https://your-app-name.railway.app`)
2. This is the URL you'll need for the frontend configuration

### 2. Frontend Deployment (GitHub Pages)

#### Step 2A: Prepare GitHub Pages
1. Go to your repository: `https://github.com/Syedabanog-1/ChatbotTodoApp`
2. Click on the "Settings" tab
3. Scroll down to the "Pages" section

#### Step 2B: Configure GitHub Pages
1. Under "Source", select "Deploy from a branch"
2. Select your main branch (usually `main` or `001-multimodal-todo-chatbot`)
3. Select "/" as the folder
4. Click "Save"
5. GitHub will start building and deploying your frontend

### 3. Post-Deployment Configuration

#### Step 3A: Update Backend URL in Frontend
1. After getting your Railway URL, update the `script.js` file:
   ```javascript
   const BACKEND_URL = 'https://your-railway-app-name.railway.app'; // Replace with your actual Railway URL
   ```
2. Replace the placeholder URL with your actual Railway URL
3. Commit and push the change:

   ```bash
   git add script.js
   git commit -m "chore: update backend URL with Railway deployment"
   git push origin main
   ```

#### Step 3B: Verify GitHub Pages Build
1. Go back to your repository Settings → Pages
2. Verify that the frontend is deployed and note the GitHub Pages URL
3. The frontend will be available at: `https://Syedabanog-1.github.io/ChatbotTodoApp`

### 4. Final Verification

#### Step 4A: Test Backend API
1. Test the health endpoint: `https://your-railway-url.railway.app/`
2. Test API documentation: `https://your-railway-url.railway.app/docs`
3. Verify the following endpoints are accessible:
   - `GET /` - Health check
   - `POST /chat` - Chat endpoint
   - `GET /api/todos` - Get todos
   - `POST /api/chat` - Web chat endpoint

#### Step 4B: Test Frontend
1. Visit your frontend: `https://Syedabanog-1.github.io/ChatbotTodoApp`
2. Test basic functionality:
   - Type "Add a task to buy groceries" and verify it works
   - Check that the todo list updates
   - Test other commands like "Show my tasks", "Mark task 1 as completed"

## Troubleshooting

### Common Issues

**Issue**: Frontend shows "connection error" or "failed to fetch"
- **Solution**: Verify the `BACKEND_URL` in `script.js` is correct and the backend is deployed

**Issue**: Backend deployment fails on Railway
- **Solution**: Check that `OPENAI_API_KEY` is properly set as an environment variable

**Issue**: GitHub Pages shows "Page not found"
- **Solution**: Verify GitHub Pages is enabled in repository settings

**Issue**: API calls return 404 errors
- **Solution**: Check that the backend endpoints exist and are properly configured

### Verification Commands

You can run the following to verify functionality locally:

```bash
# Test backend functionality
python test_functionality.py

# Start backend server locally
python run_server.py
```

## API Endpoints Reference

### Backend Endpoints
- `GET /` - Health check
- `POST /chat` - Process chat message (CLI endpoint)
- `GET /api/todos` - Get all todos (for web interface)
- `POST /api/chat` - Web chat endpoint (returns response + todos)
- `GET /docs` - API documentation (Swagger UI)

### Data Format
- Todo items format: `{id: number, title: string, completed: boolean}`
- Chat response format: `{response: string, success: boolean, todos: array}`

## Maintenance

### Updating the Application
1. Make changes to the code
2. Commit and push to GitHub
3. Railway will automatically redeploy the backend
4. GitHub Pages will automatically update the frontend

### Monitoring
- Monitor backend logs in Railway dashboard
- Check GitHub Pages build status in repository settings

## Security Considerations

- Keep your OpenAI API key secure (only in Railway environment variables)
- The application uses SQLite for local persistence
- All API calls are stateless and secure

## Support

If you encounter issues:
1. Check the deployment logs in Railway
2. Verify all environment variables are set correctly
3. Confirm all required files are present in the repository
4. Run the test script to verify functionality: `python test_functionality.py`