bump type="" tag="false" dry="true":
    git add .
    BUMPVERSION_TAG={{ tag }} uv tool run bump-my-version bump {{ type }} --verbose {{ if dry == "true" { "--dry-run" } else { "" } }}

show-bump from-version="":
    uv tool run bump-my-version show-bump {{ from-version }}

get-version:
    uv tool run bump-my-version show current_version

build:
    @echo "Building package..."
    uv build

check-package:
    @echo "Checking package..."
    uv tool run twine check dist/*

upload-test:
    @echo "Uploading to test PyPI..."
    uv tool run twine upload --repository testpypi dist/*

upload-pypi:
    @echo "Uploading to PyPI..."
    uv tool run twine upload dist/*

release version="" dry="true":
    #!/usr/bin/env bash
    set -euo pipefail
    
    if [ "{{ version }}" = "" ]; then
        echo "Error: version parameter is required"
        echo "Usage: just release <version> [dry=false]"
        exit 1
    fi
    
    echo "Starting release process for version {{ version }}..."
    
    echo "Updating version to {{ version }}..."
    {{ if dry == "true" { "echo '[DRY RUN] Would run: '" } else { "" } }}just bump {{ version }} tag=true dry={{ dry }}
    
    if [ "{{ dry }}" = "false" ]; then
        
        echo "Building package..."
        just build
        
        echo "Checking package..."
        just check-package
                
        echo "Pushing tag v{{ version }}..."
        git push origin "v{{ version }}"
        
        echo "✅ Release process started!"
        echo "GitHub Actions will handle:"
        echo "  - Building the package"
        echo "  - Publishing to PyPI" 
        echo "  - Creating GitHub Release"
        echo ""
        echo "Check the Actions tab: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
    else
        echo "[DRY RUN] Would push tag v{{ version }} to trigger release workflow"
    fi

release-patch dry="true":
    #!/usr/bin/env bash
    @echo "Releasing patch version..."
    just bump patch tag=true {{ dry }}
    if [ "{{ dry }}" = "false" ]; then
        new_version=$(just get-version | tail -1)
        git push origin "v$new_version"
        echo "✅ Release process started!"
        echo "GitHub Actions will handle:"
        echo "  - Building the package"
        echo "  - Publishing to PyPI" 
        echo "  - Creating GitHub Release"
    fi

release-minor dry="true":
    #!/usr/bin/env bash
    @echo "Releasing minor version..."
    just bump minor tag=true {{ dry }}
    if [ "{{ dry }}" = "false" ]; then
        new_version=$(just get-version | tail -1)
        git push origin "v$new_version"
        echo "✅ Release process started!"
        echo "GitHub Actions will handle:"
        echo "  - Building the package"
        echo "  - Publishing to PyPI" 
        echo "  - Creating GitHub Release"
    fi

release-major dry="true":
    #!/usr/bin/env bash
    @echo "Releasing major version..."
    just bump major tag=true {{ dry }}
    if [ "{{ dry }}" = "false" ]; then
        new_version=$(just get-version | tail -1)
        git push origin "v$new_version"
        echo "✅ Release process started!"
        echo "GitHub Actions will handle:"
        echo "  - Building the package"
        echo "  - Publishing to PyPI" 
        echo "  - Creating GitHub Release"
    fi

clean:
    @echo "Cleaning build artifacts..."
    rm -rf dist/
    rm -rf build/
    rm -rf *.egg-info/
