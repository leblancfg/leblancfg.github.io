# Notes to build blog
Once new content is written or edited, rebuild the blog to leblancfg.github.io with the following:

1. `git checkout dev`
2. `pelican content -s publishconf.py`
3. `git add .`
4. `git commit -m 'message here'`
5. `git push origin dev`
6. `ghp-import output -b master`
7. `git push origin master`
