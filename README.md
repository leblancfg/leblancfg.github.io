# Notes to build blog
## Requirements
1. `git clone --recursive -j8 https://github.com/leblancfg/leblancfg.github.io`
  * If forgot `--recursive`:
    - `git submodule init`
    - `git submodule update`
2. `conda install -c conda-forge pelican ghp-import`
3. Fix Flex base template &mdash; add the following before the stylesheets:

      {% raw %}
      <!-- Plotly -->
      <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.5/require.min.js"></script>
      <script>requirejs.config({paths: { 'plotly': ['https://cdn.plot.ly/plotly-latest.min']},});if(!window.Plotly) {{require(['plotly'],function(plotly) {window.Plotly=plotly;});}}</script>
      {% endraw %}

## New article
Once new content is written or edited, rebuild the blog to leblancfg.github.io with the following:

1. `git checkout dev`
2. `pelican content -s publishconf.py`
3. `git add .`
4. `git commit -m 'message here'`
5. `git push origin dev`
6. `ghp-import output -b master`
7. `git push origin master`
