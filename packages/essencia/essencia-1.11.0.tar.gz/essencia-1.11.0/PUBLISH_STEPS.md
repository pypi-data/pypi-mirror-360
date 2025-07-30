# Publishing Essencia to PyPI - Step by Step

## Prerequisites

### 1. Create PyPI Accounts
If you don't have accounts yet, create them at:
- Production PyPI: https://pypi.org/account/register/
- Test PyPI: https://test.pypi.org/account/register/

### 2. Generate API Tokens
After creating accounts:
1. Go to Account Settings → API tokens
2. Create a new API token (scope: "Entire account" for first time)
3. Save the token securely (starts with `pypi-`)

### 3. Configure Authentication
Create `~/.pypirc` file:
```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE
EOF

# Set proper permissions
chmod 600 ~/.pypirc
```

## Publishing Process

### Step 1: Update Package Information

Edit `pyproject.toml` and update:
```toml
[project]
version = "1.0.0"  # or appropriate version
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]

[project.urls]
"Homepage" = "https://github.com/yourusername/essencia"
"Bug Tracker" = "https://github.com/yourusername/essencia/issues"
```

### Step 2: Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build
```

### Step 3: Check Package Quality

```bash
# Check if package is correctly formatted
twine check dist/*

# You should see:
# Checking dist/essencia-1.0.0-py3-none-any.whl: PASSED
# Checking dist/essencia-1.0.0.tar.gz: PASSED
```

### Step 4: Test Installation Locally

```bash
# Create a test virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from wheel
pip install dist/essencia-1.0.0-py3-none-any.whl

# Test import
python -c "import essencia; print(essencia.__version__)"

# Cleanup
deactivate
rm -rf test-env
```

### Step 5: Upload to Test PyPI (Recommended)

```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ essencia
```

### Step 6: Upload to Production PyPI

⚠️ **Warning**: This is permanent! Make sure everything works on Test PyPI first.

```bash
# Upload to PyPI
twine upload dist/*

# The package will be available at: https://pypi.org/project/essencia/
```

## Post-Publication

### 1. Test Installation
```bash
pip install essencia
pip install essencia[security]  # With optional dependencies
```

### 2. Create Git Tag
```bash
git add .
git commit -m "Release version 1.0.0"
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main --tags
```

### 3. Create GitHub Release
1. Go to your GitHub repo → Releases → Create new release
2. Choose tag `v1.0.0`
3. Upload the wheel and tar.gz from `dist/`
4. Add release notes

## Troubleshooting

### "Package already exists"
- If you own it: increment version in pyproject.toml
- If you don't: choose different name (essencia-framework, essencia-br, etc.)

### Authentication Failed
- Make sure you're using API tokens, not username/password
- Token must start with `pypi-`
- Check ~/.pypirc permissions (should be 600)

### Invalid Package
- Run `twine check dist/*` to identify issues
- Check all required fields in pyproject.toml

## Quick Commands Reference

```bash
# Full publishing workflow
rm -rf dist/ build/ *.egg-info
python -m build
twine check dist/*
twine upload --repository testpypi dist/*
# After testing...
twine upload dist/*
```