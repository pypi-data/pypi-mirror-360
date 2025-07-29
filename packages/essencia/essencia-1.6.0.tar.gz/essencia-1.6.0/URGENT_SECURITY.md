# ⚠️ URGENT: Security Action Required

## Your PyPI token has been exposed!

### Immediate Actions:

1. **Revoke the token NOW**:
   - Go to https://pypi.org/manage/account/token/
   - Find the token that starts with `pypi-AgEIcHlwaS5vcmcCJDllOTBi...`
   - Click "Remove" or "Revoke"

2. **Generate a new token**:
   - Click "Add API token"
   - Name: "essencia-upload"
   - Scope: "Project: essencia" (if available) or "Entire account"
   - Copy the new token

3. **Keep the new token secure**:
   - Never paste it in chat or commit it to git
   - Only put it in ~/.pypirc file

## Safe Way to Configure

Create ~/.pypirc file:
```bash
nano ~/.pypirc
```

Add this (with your NEW token):
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-NEW-TOKEN-HERE

[testpypi]
username = __token__
password = # your test pypi token if you have one
```

Set permissions:
```bash
chmod 600 ~/.pypirc
```

## Important Security Notes

- PyPI tokens are like passwords - keep them secret!
- Anyone with your token can upload packages to your account
- Always revoke exposed tokens immediately
- Use project-scoped tokens when possible

Please revoke that token right now before proceeding!