# Ready to Publish! ✅

Your package is built and ready with your information:
- **Author**: Daniel Arantes (arantesdv@me.com)
- **GitHub**: https://github.com/arantesdv/essencia
- **Version**: 0.1.0

## Quick Steps:

### 1. Create PyPI Accounts
- [ ] https://test.pypi.org/account/register/
- [ ] https://pypi.org/account/register/

### 2. Generate API Tokens
After logging in to each site:
- [ ] Account Settings → API tokens → Add API token
- [ ] Save both tokens securely

### 3. Create ~/.pypirc
```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = # paste your PyPI token here

[testpypi]
username = __token__
password = # paste your Test PyPI token here
EOF

chmod 600 ~/.pypirc
```

### 4. Upload to Test PyPI
```bash
twine upload --repository testpypi dist/*
```

### 5. Test Installation
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ essencia
```

### 6. Upload to PyPI
```bash
twine upload dist/*
```

## Package Name Decision

Before uploading, check if "essencia" is available:
- https://pypi.org/project/essencia/

If taken and not yours, consider:
- `essencia-framework`
- `essencia-medical`
- `essencia-br`

To rename, update `name = "new-name"` in pyproject.toml and rebuild.

Good luck! 🚀