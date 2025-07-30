param(
    [Parameter(Mandatory=$true)]
    [string]$NewVersion
)

# Activate virtual environment if it exists
if (Test-Path ".venv") {
    .\.venv\Scripts\Activate.ps1
}

# Clean up previous builds
Remove-Item -Recurse -Force dist, build, src/*.egg-info -ErrorAction SilentlyContinue

# Update version in pyproject.toml
(Get-Content pyproject.toml) -replace 'version = ".*"', "version = `"$NewVersion`"" | Set-Content pyproject.toml

# Install/upgrade build tools
uv pip install --upgrade build twine

# Run tests
uv pip install -e ".[test]"
pytest

# Build the package
python -m build

# Upload to PyPI
python -m twine upload dist/*

Write-Host "Successfully published version $NewVersion to PyPI" 