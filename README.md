# Notes to build blog
## Requirements
1. Clone the repo:
   ```bash
   git clone https://github.com/leblancfg/leblancfg.github.io
   cd leblancfg.github.io
   ```
2. Install dependencies:
   ```bash
   uv sync --python 3.11
   ```

Notes:
- The Flex theme is vendored in this repo under `theme/Flex/`.
- No theme submodules are required anymore.
- GitHub Actions handles publishing to `master` automatically when `dev` is pushed.

## Creating a New Article

### Article Format
Create a new `.md` file in the `content/` directory with this header:
```markdown
Title: Your Article Title
Date: YYYY-MM-DD HH:MM
Category: category-name
Tags: tag1, tag2, tag3
Slug: url-slug-for-article
Author: François Leblanc
Summary: Brief description of the article

Your article content starts here...
```

### Available Categories
- data-engineering
- data-science
- crossfit
- other

## Publishing Workflow

1. **Work on `dev`:**
   ```bash
   git checkout dev
   git pull --rebase origin dev
   ```

2. **Create or edit content:**
   - Add new article to `content/`
   - Edit existing pages in `content/pages/`

3. **Test locally:**
   ```bash
   just serve
   ```
   Or on a custom port:
   ```bash
   PORT=12345 just serve
   ```

4. **Publish:**
   ```bash
   git add .
   git commit -m 'Add new article: [title]'
   git push origin dev
   ```

That push to `dev` triggers GitHub Actions, which builds the site and publishes `master`.

## Automated Deployment

The repository includes a GitHub Action that automatically deploys changes when:
- You push directly to the `dev` branch
- You merge a pull request into the `dev` branch

The action builds from `dev` and publishes to `master`.
It does **not** push commits back to `dev`.

## Troubleshooting

### Article not appearing?
- Check the date isn't in the future
- Ensure all metadata fields are present
- Verify the file is in the `content/` directory

### Build errors?
- The Jupyter notebook error can be safely ignored
- Use Python 3.11 via `uv sync --python 3.11`

### Theme issues?
- The Flex theme modifications for Plotly support must be maintained
- Theme is vendored at `theme/Flex/`
