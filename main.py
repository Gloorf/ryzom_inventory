#!/usr/bin/python3
# Copyright (C) 2016 Guillaume Dupuy
# Author: Guillaume Dupuy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from flask_babel import Babel

from flask import Flask, render_template, request

# from public_inventory import public_inventory
from inventory import inventory
from lib import Authentificator, required_roles

# Configure app
app = Flask(__name__)
babel = Babel(app)
app.config.update(LANGUAGES=['en', 'fr', 'de'])

# app.register_blueprint(public_inventory, url_prefix='/public_inventory')
app.register_blueprint(inventory, url_prefix='/inventory')
app.secret_key = 'dummy1'
app.auth = Authentificator()


@babel.localeselector
def get_locale():
    if request.args.get('lang', None):
        return request.args.get('lang')
    if request.form.get('lang', None):
        return request.form['lang']
    if request.headers.get('Accept-Language'):
        langs = request.headers.get('Accept-Language').split(',')
        if len(langs) > 0 and 'fr' in langs[0]:
            if 'fr' in langs[0]:
                return 'fr'
            if 'de' in langs[0]:
                return 'de'
            if 'en' in langs[0]:
                return 'en'
        else:
            return 'en'
    return 'en'


@app.route('/')
@required_roles('user')
def index():
    return render_template('index.html', app=app)


@app.route('/bad_auth/')
def bad_auth():
    return render_template('error_auth.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4975)
