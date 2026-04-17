set shell := ["bash", "-cu"]

port := env_var_or_default("PORT", "8910")
branch := env_var_or_default("GITHUB_PAGES_BRANCH", "master")

_ensure-submodules:
    if [ ! -d pelican-themes/Flex ]; then \
        echo "Initializing Pelican theme submodules..."; \
        git submodule sync --recursive; \
        git submodule update --init --recursive; \
    fi

serve: _ensure-submodules
    uv run pelican content -s devconf.py -lr --port {{port}}

publish: _ensure-submodules
    uv run pelican content -o output -s publishconf.py

refresh:
    rm -rf output
    git add .
    git commit -m "Updated content" --allow-empty
    git push origin dev

github: refresh publish
    git fetch origin {{branch}}
    uv run ghp-import -m "Generate Pelican site" -b {{branch}} output
    git push --force-with-lease origin {{branch}}
