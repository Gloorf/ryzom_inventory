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

import os
import time
import base64
import phpserialize
import xml.etree.ElementTree as ET

import json
from functools import wraps
from flask import redirect, url_for, session, request, current_app

from ryzomapi import sas, Guild, Character


class Translator:
    def __init__(self, lang='en'):
        self.lang = lang
        self.translations = {}
        for lang in ('de', 'en', 'fr'):
            self.translations[lang] = {}
            with open("data/words/item_words_{}.txt".format(lang), "r", encoding="utf-16") as f:
                for line in f:
                    hash, id, name, hunk = tuple(line.split("\t", 3))
                    self.translations[lang][id] = name

    def translate(self, item):
        try:
            return self.translations[self.lang][item.sheet]
        except KeyError:
            return str(item)

    def set_lang(self, lang):
        self.lang = lang


def data_need_reload(apikey):
    cache_file = 'cache/{}.xml'.format(apikey)
    if not os.path.isfile(cache_file):
        return True
    else:
        return os.path.getmtime(cache_file) + 10 * 60 < time.time()


def load_data(apikey, sort_items):
    # Check if new data is needed
    # Get new data and save it
    if data_need_reload(apikey):
        if apikey.startswith('c'):
            d = sas.get('character', apikey=apikey)
        elif apikey.startswith('g'):
            d = sas.get('guild', apikey=apikey)
        # Save data
        tree = ET.ElementTree(d)
        cache_file = 'cache/{}.xml'.format(apikey)
        tree.write(cache_file)
    # Now we have the data, let's use it
    if apikey.startswith('g'):
        return Guild(from_file='cache/{}.xml'.format(apikey), sort_items=sort_items)
    elif apikey.startswith('c'):
        return Character(from_file='cache/{}.xml'.format(apikey), sort_items=sort_items)


def get_items(machin):
    if isinstance(machin, Guild):
        return machin.room
    if isinstance(machin, Character):
        out = machin.bag
        out += machin.room
        for p in machin.pets:
            out += p.inventory
        return out


def php_to_python(raw):
    try:
        php = base64.b64decode(raw)
        python_b = phpserialize.loads(php)
        out = {}
        # phpserialize gives us something with bytestring
        # put everything back in real strings
        for key, value in python_b.items():
            out[key.decode("utf-8")] = value.decode("utf-8")
    except ValueError:
        out = {}
    finally:
        return out


def error_response():
    return redirect(url_for('bad_auth'))


def required_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_app.auth.role() not in roles:
                return error_response()
            return f(*args, **kwargs)
        return wrapped
    return wrapper


class Authentificator:
    def __init__(self):
        with open("data/allowed_characters.json", 'r') as f:
            self._characters_ok = json.load(f)
        with open("data/allowed_guilds.json", 'r') as f:
            self._guilds_ok = json.load(f)

    def guilds(self):
        return self._guilds_ok

    def players(self):
        return self._characters_ok

    def role(self):
        try:
            if session['role'] == 'guest':
                self.check_role()
        except:
            self.check_role()
        finally:
            return session['role']

    def set_role(self, val):
        session['role'] = val

    def check_role(self):
        user = request.args.get('user', '')
        data = php_to_python(user)
        # We check guild and char_name in the base64 data
        role = 'guest'
        guild_name = data['guild_name'] if 'guild_name' in data else ''
        char_name = data['char_name'] if 'char_name' in data else ''
        allowed = guild_name in self._guilds_ok
        allowed = allowed or char_name in self._characters_ok
        role = 'user' if allowed else role
        self.set_role(role)
