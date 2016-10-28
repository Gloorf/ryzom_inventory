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
import xml.etree.ElementTree as ET

from flask import redirect, url_for

from ryzomapi import sas, Guild, Character


class Translator:
    def __init__(self, lang='en'):
        self.lang = lang
        self.translations = {}
        for lang in ('en', 'fr'):
            self.translations[lang] = {}
            with open("data/words/item_words_{}.txt".format(lang), "r") as f:
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


def error_response():
    return redirect(url_for('bad_auth'))

