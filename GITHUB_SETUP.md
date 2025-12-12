# GitHub Setup Guide

## Step 1: Initialize Git Repository

Open PowerShell in your project directory and run:

```powershell
cd C:\Users\Asus\project_2\sm_backend
git init
```

## Step 2: Add All Files

```powershell
git add .
```

## Step 3: Create Initial Commit

```powershell
git commit -m "Initial commit: Django social media backend with JWT authentication"
```

## Step 4: Create Repository on GitHub

1. Go to https://github.com
2. Click the "+" icon in top right corner
3. Click "New repository"
4. Repository name: `social-media-backend` (or your preferred name)
5. Description: "Django REST API backend for social media app with JWT authentication"
6. Choose "Public" or "Private"
7. **DO NOT** check "Initialize this repository with a README" (you already have one)
8. Click "Create repository"

## Step 5: Connect Local Repository to GitHub

Copy the commands from GitHub (they will look like this, but with your username):

```powershell
git remote add origin https://github.com/Nozima-Rustamova/social-media-backend.git
git branch -M master
git push -u origin master
```

Or if you want to use `main` as branch name:

```powershell
git remote add origin https://github.com/Nozima-Rustamova/social-media-backend.git
git branch -M main
git push -u origin main
```

## Step 6: Verify Upload

Go to your GitHub repository URL and verify that all files are uploaded.

## Common Git Commands for Future Updates

### Check Status
```powershell
git status
```

### Add Changes
```powershell
# Add all changes
git add .

# Add specific file
git add filename.py
```

### Commit Changes
```powershell
git commit -m "Description of changes"
```

### Push to GitHub
```powershell
git push
```

### Pull Latest Changes
```powershell
git pull
```

### View Commit History
```powershell
git log
```

## Creating a New Branch

```powershell
# Create and switch to new branch
git checkout -b feature/new-feature

# Push new branch to GitHub
git push -u origin feature/new-feature
```

## Typical Workflow

```powershell
# 1. Check current status
git status

# 2. Add changes
git add .

# 3. Commit with message
git commit -m "Add user profile API"

# 4. Push to GitHub
git push
```

## What Gets Pushed to GitHub?

Based on your .gitignore file, these will **NOT** be uploaded:
- ❌ Virtual environment (venv/)
- ❌ Database file (db.sqlite3)
- ❌ Python cache files (__pycache__/)
- ❌ Media files (/media)
- ❌ Environment variables (.env)
- ❌ IDE settings (.vscode/, .idea/)

These **WILL** be uploaded:
- ✅ Source code (.py files)
- ✅ Requirements (requirements.txt)
- ✅ Documentation (.md files)
- ✅ Configuration (settings.py, urls.py)
- ✅ Models, Views, Serializers
- ✅ README, API docs, Testing guide

## Troubleshooting

### Issue: "remote origin already exists"
**Solution:**
```powershell
git remote remove origin
git remote add origin https://github.com/Nozima-Rustamova/social-media-backend.git
```

### Issue: Authentication failed
**Solution:** 
- Use Personal Access Token instead of password
- Go to GitHub Settings → Developer settings → Personal access tokens
- Generate new token with "repo" permissions
- Use token as password when pushing

### Issue: Large files rejected
**Solution:**
Make sure .gitignore is properly set up and you're not pushing:
- Database files
- Media files
- Virtual environment

### Issue: Want to undo last commit
**Solution:**
```powershell
# Undo commit but keep changes
git reset --soft HEAD~1

# Undo commit and discard changes
git reset --hard HEAD~1
```

## Adding Collaborators

1. Go to repository on GitHub
2. Click "Settings"
3. Click "Collaborators"
4. Click "Add people"
5. Enter their GitHub username
6. Click "Add [username] to this repository"

## Creating Releases

1. Go to your repository on GitHub
2. Click "Releases" (right sidebar)
3. Click "Create a new release"
4. Tag version: `v1.0.0`
5. Release title: "Social Media Backend v1.0"
6. Description: List of features
7. Click "Publish release"

## Repository README on GitHub

Your repository will display README.md on the main page, showing:
- Project description
- Features
- Installation instructions
- API endpoints
- Quick start guide

## Badges (Optional)

Add these to the top of your README.md for a professional look:

```markdown
![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![Django](https://img.shields.io/badge/django-6.0-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.14-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
```

## Next Steps After Pushing

1. ✅ Verify all files are on GitHub
2. ✅ Check that README displays correctly
3. ✅ Ensure .gitignore is working (no venv/ or db.sqlite3)
4. ✅ Add topics/tags to repository (django, rest-api, jwt, python)
5. ✅ Add description to repository
6. ✅ Share repository link

## Repository URL Structure

Your repository will be at:
```
https://github.com/Nozima-Rustamova/social-media-backend
```

API documentation will be at:
```
https://github.com/Nozima-Rustamova/social-media-backend/blob/master/API_DOCUMENTATION.md
```

## Important Notes

- **Never commit sensitive data** (passwords, API keys, SECRET_KEY)
- **Always use .gitignore** before first commit
- **Write meaningful commit messages**
- **Commit frequently** with small, logical changes
- **Pull before pushing** if working with others
- **Review changes** before committing (git diff)

## Example Commit Messages

Good ✅:
- "Add user authentication with JWT"
- "Implement post CRUD operations"
- "Fix like toggle functionality"
- "Update API documentation"

Bad ❌:
- "Update"
- "Fix"
- "Changes"
- "asdfgh"

## Viewing Your Project Online

After pushing, anyone can:
1. View your code
2. Clone your repository
3. Report issues
4. Contribute (if you allow)
5. Star your repository

Share your repository link to showcase your work!
