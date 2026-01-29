kill the server:
```
lsof -ti:8000 | xargs kill -9
```

build with autoreload:
```
python3 -m venv venv 2>/dev/null || true && . venv/bin/activate && pelican content -s pelicanconf.py --debug --autoreload --listen
```
Check the terminal for any errors.