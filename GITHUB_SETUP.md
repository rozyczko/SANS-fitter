# GitHub Repository Setup Guide

Complete step-by-step guide to create and upload this project to GitHub.

## Prerequisites

- Git installed on your system
- GitHub account created
- Command line / terminal access

## Step 1: Create GitHub Repository

### Option A: Via GitHub Website
1. Go to https://github.com
2. Click "+" in top right corner
3. Select "New repository"
4. Fill in details:
   - **Repository name**: `SANS-fitter`
   - **Description**: "Web application for SANS data analysis with AI-assisted model selection"
   - **Visibility**: Public
   - **Initialize**: Uncheck all boxes (we have existing code)
5. Click "Create repository"

### Option B: Via GitHub CLI
```bash
gh repo create SANS-fitter --public --description "Web application for SANS data analysis"
```

## Step 2: Initialize Local Repository

If not already initialized:
```bash
cd /path/to/SANS-fitter
git init
```

## Step 3: Stage All Files

```bash
# Add all files to staging
git add .

# Verify what will be committed
git status
```

Expected files to be added:
- Core application: `app.py`
- Dependencies: `requirements.txt`
- Documentation: `README.md`, `WEBAPP_README.md`, `QUICKSTART.md`, `PROJECT_STRUCTURE.md`
- Tests: `test_app.py`, `demo_app.py`
- Deployment: `Dockerfile`, `Procfile`, `setup.sh`
- Data: `example_sans_data.dat`, `simulated_sans_data.csv`
- Configuration: `.gitignore`
- Source: `src/sans_fitter/`
- Tests: `tests/`
- Examples: `examples/`
- Other: `pyproject.toml`, `LICENSE`, `mkdocs.yml`, etc.

## Step 4: Create Initial Commit

```bash
git commit -m "Initial commit: SANS data analysis web application

- Add Streamlit web interface for SANS data fitting
- Implement manual and AI-assisted model selection
- Add interactive Plotly visualizations
- Include comprehensive documentation
- Support Docker, Heroku, and Streamlit Cloud deployment
- All tests passing (48/48 core + app tests)
"
```

## Step 5: Connect to GitHub

```bash
# Add remote (replace USERNAME with your GitHub username)
git remote add origin https://github.com/USERNAME/SANS-fitter.git

# Verify remote
git remote -v
```

## Step 6: Push to GitHub

```bash
# Push main branch
git push -u origin main
```

If your default branch is `master`:
```bash
git push -u origin master
```

## Step 7: Verify Upload

1. Go to `https://github.com/USERNAME/SANS-fitter`
2. Check that all files are present
3. Verify README.md displays correctly
4. Check that GitHub shows the license

## Step 8: Set Up GitHub Pages (Optional)

For documentation hosting:

1. Go to repository Settings
2. Navigate to "Pages" section
3. Select source: "Deploy from a branch"
4. Choose branch: `main` or `gh-pages`
5. Save

Documentation will be available at:
`https://USERNAME.github.io/SANS-fitter/`

## Step 9: Configure Repository Settings

### Topics/Tags
Add relevant topics to help others find your repository:
1. Go to repository main page
2. Click ⚙️ next to "About"
3. Add topics:
   - `sans`
   - `neutron-scattering`
   - `streamlit`
   - `data-analysis`
   - `machine-learning`
   - `python`
   - `scientific-computing`
   - `plotly`
   - `materials-science`

### Description
Update repository description:
"🔬 Web application for Small Angle Neutron Scattering (SANS) data analysis with AI-assisted model selection, interactive visualization, and fitting"

### Website
Add website URL (if deployed):
- Streamlit Cloud: `https://your-app.streamlit.app`
- Heroku: `https://your-app.herokuapp.com`
- Custom domain: `https://your-domain.com`

## Step 10: Add Badges to README (Optional)

Add at the top of README.md:

```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
```

## Step 11: Create GitHub Actions Workflow (Optional)

For automated testing on push:

Create `.github/workflows/app-tests.yml`:

```yaml
name: Web App Tests

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -e .
        pip install -r requirements.txt
        pip install pytest
    
    - name: Run core tests
      run: pytest tests/ -v
    
    - name: Run app tests
      run: python test_app.py
```

Commit and push:
```bash
git add .github/workflows/app-tests.yml
git commit -m "Add GitHub Actions workflow for automated testing"
git push
```

## Step 12: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click "New app"
3. Connect GitHub account (if not already)
4. Select repository: `USERNAME/SANS-fitter`
5. Branch: `main`
6. Main file path: `app.py`
7. Click "Deploy!"

App will be live at: `https://USERNAME-sans-fitter.streamlit.app`

### Environment Variables (for AI features)
In Streamlit Cloud settings:
1. Click "Settings" → "Secrets"
2. Add:
   ```toml
   ANTHROPIC_API_KEY = "your-key-here"
   ```

## Step 13: Create Release (Optional)

For version tagging:

```bash
# Tag the release
git tag -a v1.0.0 -m "Version 1.0.0: Initial web application release"

# Push tags
git push origin v1.0.0
```

On GitHub:
1. Go to "Releases" tab
2. Click "Create a new release"
3. Select tag: `v1.0.0`
4. Title: "Version 1.0.0 - Web Application Launch"
5. Description: Features, improvements, etc.
6. Click "Publish release"

## Troubleshooting

### Large Files Warning
If you get warnings about large files:
```bash
# Check file sizes
find . -type f -size +50M

# Remove large files from git
git rm --cached path/to/large/file
echo "path/to/large/file" >> .gitignore
git commit -m "Remove large file"
```

### Authentication Failed
Use GitHub Personal Access Token:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo`
4. Copy token
5. Use as password when pushing:
   ```bash
   Username: your-username
   Password: <paste-token-here>
   ```

### Permission Denied (SSH)
If using SSH and getting permission denied:
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
```

Then change remote to SSH:
```bash
git remote set-url origin git@github.com:USERNAME/SANS-fitter.git
```

## File Checklist

Ensure these files are in your repository:

Core Application:
- [x] app.py
- [x] requirements.txt
- [x] test_app.py
- [x] demo_app.py

Documentation:
- [x] README.md
- [x] WEBAPP_README.md
- [x] QUICKSTART.md
- [x] PROJECT_STRUCTURE.md
- [x] This file (GITHUB_SETUP.md)

Deployment:
- [x] Dockerfile
- [x] Procfile
- [x] setup.sh

Data:
- [x] example_sans_data.dat
- [x] simulated_sans_data.csv

Configuration:
- [x] .gitignore
- [x] pyproject.toml

Source Code:
- [x] src/sans_fitter/__init__.py
- [x] src/sans_fitter/sans_fitter.py

Tests:
- [x] tests/test_sans_fitter.py

Examples:
- [x] examples/ (directory with examples)

Other:
- [x] LICENSE
- [x] mkdocs.yml (if present)

## Next Steps

After successful upload:

1. ✓ Repository is live on GitHub
2. → Share link with collaborators
3. → Deploy to Streamlit Cloud
4. → Add comprehensive examples
5. → Write blog post or tutorial
6. → Submit to awesome lists
7. → Announce on social media

## Support

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions, share ideas
- **Wiki**: Add detailed guides and tutorials
- **Pull Requests**: Contribute improvements

## Success Indicators

✓ Repository accessible at `https://github.com/USERNAME/SANS-fitter`
✓ README displays properly with badges
✓ All files visible in file browser
✓ Code syntax highlighting works
✓ Issues and Discussions enabled
✓ License file recognized by GitHub
✓ Topics/tags added for discoverability

Your SANS-fitter web application is now live on GitHub! 🎉
