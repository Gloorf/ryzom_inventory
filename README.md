# Installation

If you want to run your own, you'll need Python3, and some pip packages :
```
pip install flask flask_babel ryzomapi phpserialize
```

# Quick start

* Update data/allowed_characters.json, data/allowed_guilds.json with the name of players / guilds allowed (both are optionals, you don't need to put a player name in allowed_characters.json if his guild is already in allowed_guilds.json)


* Update guilds.json with your APIKey

* Launch it
```
python3 main.py
```
* Add a custom app with URL http://localhost:4975 and visit it
* Enjoy
