set shell := ["bash", "-cu"]

port := env_var_or_default("PORT", "8910")
branch := env_var_or_default("GITHUB_PAGES_BRANCH", "master")

serve:
    uv run pelican content -s devconf.py -lr --port {{port}}

open:
    open http://localhost:{{port}}

publish:
    uv run pelican content -o output -s publishconf.py

refresh:
    rm -rf output
    git add .
    git commit -m "Updated content" --allow-empty
    git push origin dev

github:
    @echo "GitHub deployment is handled by the GitHub Action now."
    @echo "Commit your changes on 'dev' and push that branch instead:"
    @echo "  git push origin dev"
