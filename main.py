#!/usr/bin/python3
from flask import Flask, request
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
