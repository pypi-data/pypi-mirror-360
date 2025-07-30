# GitHub Setup Instructions

## 1. Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `essencia`
3. Description: "A comprehensive Python framework for building secure medical and business applications"
4. Make it Public
5. DO NOT initialize with README, .gitignore, or license (we already have them)
6. Click "Create repository"

## 2. Connect Local Repository

After creating the repository on GitHub, run these commands:

```bash
# Add remote repository
git remote add origin https://github.com/arantesdv/essencia.git

# Push main branch and tags
git push -u origin master
git push origin --tags
```

## 3. Alternative: Using GitHub CLI

If you have GitHub CLI installed:

```bash
# Create repo and push in one command
gh repo create essencia --public --source=. --remote=origin --push
```

## 4. After Pushing

Your repository will be available at:
- https://github.com/arantesdv/essencia

The release will be at:
- https://github.com/arantesdv/essencia/releases/tag/v1.0.0

## 5. Create GitHub Release

After pushing, create a release:

```bash
gh release create v1.0.0 \
  --title "Essencia v1.0.0" \
  --notes "Initial release of Essencia framework

## Features
- Comprehensive Python framework for medical and business applications
- Sync and async MongoDB support
- Redis-based intelligent caching
- Field-level encryption
- Brazilian data validators
- Security features (XSS protection, CSRF, rate limiting)
- Flet UI integration

## Installation
\`\`\`bash
pip install essencia
\`\`\`

Published to PyPI: https://pypi.org/project/essencia/1.0.0/"
```

Or manually:
1. Go to https://github.com/arantesdv/essencia/releases/new
2. Choose tag: v1.0.0
3. Release title: "Essencia v1.0.0"
4. Add description
5. Publish release