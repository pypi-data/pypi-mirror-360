# PyPI Security Checklist

## Before Publishing

- [ ] No hardcoded secrets in code
- [ ] All sensitive examples use environment variables
- [ ] .env.example provided (no real values)
- [ ] SECURITY.md documented
- [ ] No personal information in logs
- [ ] Dependencies up to date
- [ ] Version bumped appropriately

## PyPI Account Security

- [ ] 2FA enabled on PyPI
- [ ] API token with minimal scope
- [ ] Recovery codes stored safely

## Package Protection

- [ ] Consider registering similar names:
  - essência (with accent)
  - esencia (without s)
  - essentia (Latin)

## Monitoring

- [ ] Watch for typosquatting attempts
- [ ] Monitor package downloads
- [ ] Check for unauthorized forks

## GitHub Actions for PyPI

```yaml
# Use Trusted Publishers instead of tokens
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    user: __token__
    password: ${{ secrets.PYPI_API_TOKEN }}
```