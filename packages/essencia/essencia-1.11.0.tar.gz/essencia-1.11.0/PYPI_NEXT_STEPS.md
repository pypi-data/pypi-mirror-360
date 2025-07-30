# Next Steps to Publish on PyPI

## Current Status ✅
- Package built successfully
- Quality checks passed
- Distribution files ready in `dist/` folder

## What You Need to Do

### 1. Update Package Information

Before publishing, you should update the author information in `pyproject.toml`:

```bash
# Edit the file and update these lines:
authors = [
    {name = "Daniel Arantes", email = "your-real-email@example.com"},
]

[project.urls]
"Homepage" = "https://github.com/your-github-username/essencia"
"Bug Tracker" = "https://github.com/your-github-username/essencia/issues"
```

After updating, rebuild:
```bash
rm -rf dist/
python -m build
```

### 2. Create PyPI Accounts

You need accounts on both:
1. **Test PyPI**: https://test.pypi.org/account/register/
2. **Production PyPI**: https://pypi.org/account/register/

### 3. Generate API Tokens

After creating accounts:
1. Log in to each site
2. Go to Account Settings → API tokens
3. Click "Add API token"
4. Name: "essencia-upload" (or any name)
5. Scope: "Entire account" (for now)
6. Copy the token (starts with `pypi-`)

### 4. Configure Authentication

Create the file `~/.pypirc`:

```bash
nano ~/.pypirc
```

Add this content (replace with your tokens):
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-PRODUCTION-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
```

Set proper permissions:
```bash
chmod 600 ~/.pypirc
```

### 5. Check Package Name Availability

Check if "essencia" is available:
- Test PyPI: https://test.pypi.org/project/essencia/
- Production PyPI: https://pypi.org/project/essencia/

If you own the existing package, you can replace it.
If not, consider names like:
- `essencia-framework`
- `essencia-medical`
- `essencia-br`

### 6. Upload to Test PyPI First (Recommended)

```bash
twine upload --repository testpypi dist/*
```

You'll see:
```
Uploading distributions to https://test.pypi.org/legacy/
Uploading essencia-0.1.0-py3-none-any.whl
Uploading essencia-0.1.0.tar.gz
```

### 7. Test Installation from Test PyPI

```bash
# Create a test environment
python -m venv test-install
source test-install/bin/activate  # On Windows: test-install\Scripts\activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ essencia

# Test it works
python -c "import essencia; print('Success!', essencia.__version__)"

# Clean up
deactivate
rm -rf test-install
```

### 8. Upload to Production PyPI

Only after testing on Test PyPI:

```bash
twine upload dist/*
```

### 9. Verify Installation

```bash
pip install essencia
python -c "import essencia; print(essencia.__version__)"
```

## Important Notes

1. **Version Strategy**: 
   - If replacing existing package: Consider using 2.0.0 to indicate major changes
   - If new name: Start with 0.1.0 or 1.0.0

2. **Can't Delete Releases**: Once uploaded to PyPI, you can't delete (only yank)

3. **Token Security**: Never commit `.pypirc` to git

## Quick Command Summary

```bash
# After updating pyproject.toml
rm -rf dist/
python -m build
twine check dist/*
twine upload --repository testpypi dist/*
# After testing...
twine upload dist/*
```

## Need Help?

If you encounter issues:
1. Package name taken: Choose alternative name
2. Authentication fails: Check token starts with `pypi-`
3. Upload fails: Check internet connection and PyPI status

Good luck with your publication! 🚀