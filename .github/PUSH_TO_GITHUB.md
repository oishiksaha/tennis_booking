# Push to GitHub - Quick Guide

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (e.g., `tennis-booking-bot`)
3. **Don't** initialize with README, .gitignore, or license (we already have these)
4. Copy the repository URL (e.g., `https://github.com/yourusername/tennis-booking-bot.git`)

## Step 2: Initialize Git (if not already done)

```bash
cd /Users/oishiksaha/Documents/Personal/Tennis/Bots/tennis-booking-bot
git init
```

## Step 3: Add All Files

```bash
git add .
```

## Step 4: Create Initial Commit

```bash
git commit -m "Initial commit: Tennis booking bot with Playwright"
```

## Step 5: Add Remote and Push

```bash
# Replace with your actual GitHub repository URL
git remote add origin https://github.com/yourusername/tennis-booking-bot.git
git branch -M main
git push -u origin main
```

## Alternative: Using SSH

If you prefer SSH:

```bash
git remote add origin git@github.com:yourusername/tennis-booking-bot.git
git push -u origin main
```

## What Gets Pushed

✅ All source code (`src/`)
✅ All scripts (`scripts/`)
✅ Configuration template (`config/config.yaml`)
✅ Documentation (`docs/`)
✅ Requirements files
✅ README and other docs

❌ Virtual environment (`venv/`) - excluded
❌ Browser state (`data/browser_state/`) - excluded (contains auth)
❌ Log files (`logs/`) - excluded
❌ Environment files (`.env`) - excluded

## Troubleshooting

**If you get authentication errors:**
- Use GitHub Personal Access Token instead of password
- Or set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

**If repository already exists:**
```bash
git remote set-url origin https://github.com/yourusername/tennis-booking-bot.git
git push -u origin main
```

