# Publishing to PyPI Guide

This guide explains how to publish the Financial MCP package to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both [Test PyPI](https://test.pypi.org/) and [PyPI](https://pypi.org/)
2. **API Tokens**: Generate API tokens for both platforms
3. **Required Tools**: Install build and upload tools

```bash
pip install build twine
```

## Method 1: Automated Publishing (Recommended)

### Setup GitHub Secrets

1. Go to your repository settings > Secrets and variables > Actions
2. Add the following secrets:
   - `PYPI_API_TOKEN`: Your PyPI API token
   - `TEST_PYPI_API_TOKEN`: Your Test PyPI API token

### Create a Release

1. **Option A: Using the release script**
   ```bash
   python scripts/release.py
   ```

2. **Option B: Manual tag creation**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

The GitHub Actions workflow will automatically:
- Run tests across multiple Python versions
- Build the package
- Publish to PyPI when a version tag is pushed

## Method 2: Manual Publishing

### 1. Prepare the Package

```bash
# Clean previous builds
rm -rf build dist *.egg-info

# Install build dependencies
pip install --upgrade build twine
```

### 2. Build the Package

```bash
# Build source and wheel distributions
python -m build
```

This creates:
- `dist/financial-mcp-1.0.0.tar.gz` (source distribution)
- `dist/financial_mcp-1.0.0-py3-none-any.whl` (wheel distribution)

### 3. Check the Package

```bash
# Validate the package
twine check dist/*
```

### 4. Test Upload (Optional but Recommended)

```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ financial-mcp
```

### 5. Upload to Production PyPI

```bash
# Upload to PyPI
twine upload dist/*
```

## Method 3: Using the Build Script

```bash
# Run the interactive build and upload script
python scripts/build_and_upload.py
```

This script will:
1. Clean previous builds
2. Run tests
3. Build the package
4. Validate the build
5. Offer options to upload to Test PyPI or production PyPI

## Verification

After publishing, verify the package:

1. **Check PyPI page**: Visit https://pypi.org/project/financial-mcp/
2. **Test installation**:
   ```bash
   pip install financial-mcp
   ```
3. **Test CLI commands**:
   ```bash
   financial-mcp-fetch --help
   financial-mcp-analyze --help
   financial-mcp-visualize --help
   ```

## Version Management

### Updating Versions

The package version is defined in multiple files:
- `financial_mcp/__init__.py`
- `setup.py`
- `pyproject.toml`

Use the release script to automatically update all version references:

```bash
python scripts/release.py
```

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backwards compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```
   Error: Invalid or expired API token
   ```
   - Verify your API token is correct
   - Check token permissions and expiration

2. **File Already Exists**
   ```
   Error: File already exists
   ```
   - Version already published - increment version number
   - Cannot overwrite existing versions on PyPI

3. **Package Validation Errors**
   ```
   Error: Package validation failed
   ```
   - Run `twine check dist/*` for details
   - Fix issues in setup.py or pyproject.toml

4. **Import Errors After Installation**
   - Check package structure in MANIFEST.in
   - Verify all required files are included

### Getting Help

- **PyPI Help**: https://pypi.org/help/
- **Twine Documentation**: https://twine.readthedocs.io/
- **Packaging Guide**: https://packaging.python.org/

## Security Best Practices

1. **Use API Tokens**: Never use username/password for uploads
2. **Scope Tokens**: Create project-specific tokens when possible
3. **Secure Storage**: Store tokens in GitHub Secrets, not in code
4. **Regular Rotation**: Rotate API tokens periodically

## Post-Publication Checklist

- [ ] Verify package appears on PyPI
- [ ] Test installation in clean environment
- [ ] Update documentation with new version
- [ ] Create GitHub release with changelog
- [ ] Announce release if applicable
- [ ] Monitor for issues or feedback

---

**Note**: Always test with Test PyPI before publishing to production PyPI!