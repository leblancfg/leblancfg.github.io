# Notes to build blog
## Requirements
1. `git clone --recursive -j8 https://github.com/leblancfg/leblancfg.github.io`
  * If forgot `--recursive`:
    - `git submodule init`
    - `git submodule update`
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # or with conda:
   conda install -c conda-forge pelican ghp-import
   ```
3. Fix Flex base template &mdash; add the following before the stylesheets:

      {% raw %}
      <!-- Plotly -->
      <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.5/require.min.js"></script>
      <script>requirejs.config({paths: { 'plotly': ['https://cdn.plot.ly/plotly-latest.min']},});if(!window.Plotly) {{require(['plotly'],function(plotly) {window.Plotly=plotly;});}}</script>
      {% endraw %}

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

### Quick Method (using make)
```bash
# Ensure you're on dev branch
git checkout dev

# Create/edit your article in content/
# Then publish everything with one command:
make github
```

### Manual Method
If you need more control over the process:

1. **Ensure you're on dev branch:**
   ```bash
   git checkout dev
   ```

2. **Create or edit content:**
   - Add new article to `content/` directory
   - Edit existing pages in `content/pages/`

3. **Test locally (optional):**
   ```bash
   # Build with development config
   pelican content -s pelicanconf.py
   
   # Serve locally on port 8000
   make serve
   # or
   pelican -lr --port 8000
   ```

4. **Publish to production:**
   ```bash
   # Option 1: Use make command (recommended)
   make github
   
   # Option 2: Manual steps
   pelican content -s publishconf.py
   git add .
   git commit -m 'Add new article: [title]'
   git push origin dev
   ghp-import output -b master
   git push origin master
   ```

## Automated Deployment

The repository includes a GitHub Action that automatically deploys changes when:
- You push directly to the `dev` branch
- You merge a pull request into the `dev` branch

The action runs the equivalent of `make github` automatically.

## Troubleshooting

### Article not appearing?
- Check the date isn't in the future
- Ensure all metadata fields are present
- Verify the file is in the `content/` directory

### Build errors?
- The Jupyter notebook error can be safely ignored
- Ensure submodules are initialized: `git submodule update --init --recursive`

### Theme issues?
- The Flex theme modifications for Plotly support must be maintained
- Theme is in `pelican-themes/Flex/`
