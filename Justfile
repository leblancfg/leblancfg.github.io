set shell := ["bash", "-cu"]

port := env_var_or_default("PORT", "8910")
branch := env_var_or_default("GITHUB_PAGES_BRANCH", "master")

serve:
    uv run pelican content -s devconf.py -lr --port {{port}}

publish:
    uv run pelican content -o output -s publishconf.py

refresh:
    rm -rf output
    git add .
    git commit -m "Updated content" --allow-empty
    git push origin dev

github: refresh publish
    uv run ghp-import -m "Generate Pelican site" -b {{branch}} output
    git push origin {{branch}}
