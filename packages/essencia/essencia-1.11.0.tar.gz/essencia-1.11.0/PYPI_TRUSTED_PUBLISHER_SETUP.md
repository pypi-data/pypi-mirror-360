# PyPI Trusted Publisher Setup

This guide helps you configure PyPI's Trusted Publisher feature for the essencia package.

## Prerequisites

1. You must have maintainer access to the essencia package on PyPI
2. You must have admin access to the GitHub repository

## Setup Steps

### 1. Configure PyPI

1. Go to https://pypi.org/manage/project/essencia/settings/publishing/
2. Scroll down to "Trusted Publishers"
3. Click "Add a new publisher"
4. Fill in the following information:
   - **Owner**: `arantesdv`
   - **Repository name**: `essencia`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi` (optional but recommended)
5. Click "Add"

### 2. Create GitHub Environment (Optional but Recommended)

1. Go to https://github.com/arantesdv/essencia/settings/environments
2. Click "New environment"
3. Name it `pypi`
4. Click "Configure environment"
5. You can add protection rules if desired (e.g., require reviews)

### 3. Test the Workflow

The workflow will automatically run when you create a new release on GitHub.

To test it manually:
1. Go to https://github.com/arantesdv/essencia/actions
2. Click on "Publish to PyPI" workflow
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

## How It Works

1. When you create a release on GitHub, the workflow automatically triggers
2. It builds the package (wheel and source distribution)
3. Using GitHub's OIDC token, it authenticates with PyPI
4. Publishes the package without needing any stored secrets

## Advantages

- No API tokens to manage or rotate
- More secure - uses GitHub's identity
- Automatic publishing on releases
- No secrets stored in GitHub

## Publishing Version 1.1.0

Once you've configured the trusted publisher:

1. The workflow can be triggered manually from the Actions tab
2. Or it will run automatically for future releases

## Troubleshooting

If the workflow fails:
1. Check that the trusted publisher is configured correctly on PyPI
2. Ensure the workflow file path matches what you configured
3. Check the GitHub Actions logs for specific errors