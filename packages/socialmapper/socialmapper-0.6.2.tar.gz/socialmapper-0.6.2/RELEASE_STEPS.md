# Step-by-Step Guide to Publish SocialMapper v0.6.2

## Prerequisites
- Ensure you have PyPI credentials configured
- Make sure you're on the main branch with the latest changes

## Steps to Publish

### 1. Switch to main branch (if using worktree)
```bash
cd ../socialmapper-main
# OR if not using worktree, ensure you're on main:
git checkout main
```

### 2. Merge the fix from test-suite branch
```bash
# Cherry-pick the specific fix commit
git cherry-pick 7c2a734

# OR merge the entire branch if you want all changes
git merge test-suite
```

### 3. Run tests to ensure everything works
```bash
# Run the test suite
uv run pytest

# Run linting
uv run ruff check socialmapper/

# Run type checking
uv run python scripts/type_check.py
```

### 4. Build the package
```bash
# Clean any previous builds
rm -rf dist/ build/ *.egg-info

# Build the package using hatch (as specified in pyproject.toml)
uv run hatch build
```

### 5. Check the built package
```bash
# Check the contents of the wheel and tarball
ls -la dist/

# Verify the package metadata
uv run twine check dist/*
```

### 6. Test installation locally (optional but recommended)
```bash
# Create a test virtual environment
cd /tmp
uv venv test-env
source test-env/bin/activate

# Install from the built wheel
uv pip install /path/to/socialmapper/dist/socialmapper-0.6.2-py3-none-any.whl

# Test that it works
python -c "import socialmapper; print(socialmapper.__version__)"

# Deactivate and clean up
deactivate
rm -rf test-env
```

### 7. Upload to TestPyPI first (optional but recommended)
```bash
# Upload to TestPyPI to test the release process
uv run twine upload --repository testpypi dist/*

# Test installation from TestPyPI
uv pip install --index-url https://test.pypi.org/simple/ socialmapper==0.6.2
```

### 8. Upload to PyPI
```bash
# Upload to the real PyPI
uv run twine upload dist/*

# You'll be prompted for your PyPI username and password
# OR use an API token (recommended):
# Username: __token__
# Password: your-pypi-api-token
```

### 9. Create a GitHub release
```bash
# Tag the release
git tag -a v0.6.2 -m "Release v0.6.2: Fix travel_time propagation in census data"

# Push the tag
git push origin v0.6.2

# Push the main branch
git push origin main
```

### 10. Create release on GitHub
1. Go to https://github.com/mihiarc/socialmapper/releases
2. Click "Draft a new release"
3. Choose the tag `v0.6.2`
4. Release title: "v0.6.2 - Travel Time Fix"
5. Description (use the CHANGELOG content):
   ```markdown
   ## 🐛 Bug Fixes

   ### Fixed Travel Time Propagation in Census Data Export
   - Fixed incorrect travel_time_minutes in exported census CSV files
   - Travel time now correctly propagates from pipeline configuration to census data
   - Previously defaulted to 15 minutes regardless of actual isochrone travel time
   - Now accurately reflects the travel time used for isochrone generation (e.g., 60, 120 minutes)

   ### 🔧 Technical Details
   - Added `travel_time` parameter to `integrate_census_data()` function
   - Updated `PipelineOrchestrator` to pass travel_time to census integration  
   - Modified `add_travel_distances()` to accept and use travel_time parameter
   - Maintains backward compatibility while fixing the metadata accuracy
   ```
6. Attach the wheel and tarball from `dist/`
7. Click "Publish release"

### 11. Verify the release
```bash
# Install from PyPI in a fresh environment
uv pip install socialmapper==0.6.2

# Verify the version
python -c "import socialmapper; print(socialmapper.__version__)"
```

### 12. Update documentation (if needed)
- Update any version references in documentation
- Add release notes to project website/docs if applicable

## Troubleshooting

### If you don't have twine installed:
```bash
uv pip install twine
```

### If you don't have PyPI credentials:
1. Create an account at https://pypi.org
2. Go to Account Settings → API tokens
3. Create a new API token for this project
4. Use `__token__` as username and the token as password

### If the build fails:
- Check that all dependencies are properly specified in pyproject.toml
- Ensure version number is updated correctly
- Run `uv run hatch clean` before rebuilding

## Post-Release Checklist
- [ ] Package uploaded to PyPI
- [ ] GitHub release created and tagged
- [ ] Installation tested from PyPI
- [ ] Documentation updated (if needed)
- [ ] Announcement made (if applicable)