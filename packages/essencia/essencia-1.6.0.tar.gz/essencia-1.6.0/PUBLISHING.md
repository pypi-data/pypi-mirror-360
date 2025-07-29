# Publishing to PyPI - Checklist

## Pre-Publication Checklist

### 1. **Handle Existing Package**
- [ ] If you own the current "essencia" on PyPI:
  - [ ] Backup existing package users/downloads data
  - [ ] Consider renaming old package or creating essencia-legacy
  - [ ] Plan version strategy (recommend 1.0.0 for new architecture)
- [ ] If you don't own it:
  - [ ] Choose a different name (e.g., essencia-framework, essencia-medical, essencia-br)

### 2. **Security Preparation** ✅
- [x] No hardcoded secrets or credentials
- [x] Proper encryption implementation
- [x] Environment-based configuration
- [x] Security documentation (SECURITY.md)
- [x] Password hashing upgraded to bcrypt (with fallback)

### 3. **Code Quality**
- [ ] Update version in pyproject.toml
- [ ] Update author email in pyproject.toml
- [ ] Update GitHub URLs in pyproject.toml
- [ ] Run linting: `ruff check src/`
- [ ] Run type checking: `mypy src/essencia/`
- [ ] Run tests (when available)

### 4. **Documentation**
- [ ] Update README.md with:
  - [ ] Installation instructions
  - [ ] Quick start guide
  - [ ] Feature overview
  - [ ] Migration guide (if replacing existing package)
- [ ] Create CHANGELOG.md
- [ ] Update docstrings for public APIs

### 5. **Package Preparation**
- [ ] Create/update .gitignore for Python
- [ ] Add LICENSE file (MIT recommended)
- [ ] Test package build: `python -m build`
- [ ] Test installation: `pip install dist/essencia-*.whl`

### 6. **Final Security Check**
- [ ] Generate secure encryption key example:
  ```bash
  python -c "import secrets; import base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
  ```
- [ ] Verify no .env files will be included
- [ ] Check for any remaining TODOs related to security

## Publishing Commands

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check package
twine check dist/*

# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ essencia

# Upload to PyPI
twine upload dist/*
```

## Post-Publication

1. **Create GitHub Release**
   - Tag version (e.g., v1.0.0)
   - Include changelog
   - Attach wheel and source distribution

2. **Update Documentation**
   - Add PyPI badges to README
   - Update installation instructions
   - Create migration guide for existing users

3. **Monitor**
   - Watch for security issues
   - Monitor for installation problems
   - Be ready to yank version if critical issues found

## Version Strategy Recommendation

Since this is a complete rewrite:
- If current PyPI package < 1.0: Use 1.0.0
- If current PyPI package >= 1.0: Use next major version
- Consider using 1.0.0-alpha.1 for initial release

## Security Notes

- The package is secure for public release
- Bcrypt is optional but recommended (`pip install essencia[security]`)
- All sensitive operations use environment variables
- Field-level encryption is production-ready