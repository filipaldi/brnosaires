lsof -ti:8000 | xargs kill -9

build 
python3 -m venv venv 2>/dev/null || true && . venv/bin/activate && pelican content -s pelicanconf.py --autoreload --listen

access the pages with browser and review the results