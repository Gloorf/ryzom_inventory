#!/usr/bin/python3
from flask import Flask, request
from flask_babel import Babel

from inventory import inventory

# Configure app
app = Flask(__name__)
babel = Babel(app)
app.config.update(LANGUAGES=['en', 'fr'])

app.register_blueprint(inventory, url_prefix='/public_inventory')


@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        return request.args.get('lang')
    if request.headers.get('Accept-Language'):
        langs = request.headers.get('Accept-Language').split(',')
        if len(langs) > 0 and 'fr' in langs[0]:
            return 'fr'
        else:
            return 'en'
    return 'fr'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4975)
