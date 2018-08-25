# Notes to build blog
## Requirements
1. `git clone --recursive -j8 https://github.com/leblancfg/leblancfg.github.io`
  * If forgot `--recursive`:
    - `git submodule init`
    - `git submodule update`
2. `conda install -c conda-forge pelican ghp-import`

## New article
Once new content is written or edited, rebuild the blog to leblancfg.github.io with the following:

1. `git checkout dev`
2. `pelican content -s publishconf.py`
3. `git add .`
4. `git commit -m 'message here'`
5. `git push origin dev`
6. `ghp-import output -b master`
7. `git push origin master`
