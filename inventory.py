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


from flask import Blueprint, render_template, redirect, url_for, request
import flask_babel

from ryzomapi import APIKey
from ryzomapi.exceptions import InvalidAPIKeyException

from lib import load_data, Translator, data_need_reload
from inventory_filters import dummy_filter, filter_1, filter_2, filter_3, filter_4, filter_5, filter_6
# Gettext hack
_ = lambda x: x

MAX_APIKEY = 5


class InvalidPermissionException(Exception):
    pass


class Manager:
    def __init__(self, sort_items):
        self._translator = Translator('en')
        self._guilds = []
        self._filters = []
        self._sort_items = sort_items
        self.add_filter(dummy_filter)
        self.current_filter = self._filters[0]
        self.current_guilds = []

    def add_filter(self, f):
        self._filters.append(f)

    def add_guild(self, key):
        found = next((x for x in self._guilds if x.api_key == key), None)
        if found:
            return found.gid
        else:
            tmp = load_data(key, self._sort_items)
            if not hasattr(tmp, 'room'):
                raise InvalidPermissionException
            tmp.api_key = key
            self._guilds.append(tmp)
            return tmp.gid

    def refresh_guilds(self):
        for g in self._guilds:
            if data_need_reload(g.api_key):
                g = load_data(g.api_key, self._sort_items)

    def get_items(self):
        items = []
        pick_from = self.current_guilds

        for g in pick_from:
            for i in g.room:
                # Filter directly, quantity will be dealt later (after merge)
                if self.current_filter(i):
                    i.origins = [(g, i.stack)]
                    items.append(i)

        # We need to assume there's at least one item in our list of items
        # If not, just return directly
        if not items:
            return []
        # Sort our list, for a nice display (and faster merging)
        items.sort()
        origins = [items[0].origins[0]]
        previous = items[0]
        merged = []
        # List is already sorted, so we can fasten up
        for i in items:
            if i == previous:
                origins.append(i.origins[0])
            else:
                total_stack = sum(x[1] for x in origins)
                previous.origins = origins
                # Now that we merged our item, we can check quantity
                if self.current_filter.quantity() < total_stack:
                    merged.append(previous)
                origins = [i.origins[0]]
            previous = i
        return merged

    # Used by templates
    def filters(self):
        yield from enumerate(self._filters)

    # Used by templates
    def tooltip(self, item):
        out = self.translation(item)
        for guild, number in item.origins:
            out += " - {} ({})".format(guild.name, number)
        return out

    def set_current_guilds(self, gids):
        self.current_guilds = [x for x in self._guilds if x.gid in gids]

    def set_filter(self, id):
        try:
            self.current_filter = self._filters[id]
        except IndexError:
            self.current_filter = self._filters[0]

    def item_url(self, item):
        total_stack = sum(x[1] for x in item.origins)
        return 'http://api.ryzom.com/item_icon.php?q={0}&s={1}&sheetid={2}.sitem'.format(
            item.quality, total_stack, item.sheet)

    def translation(self, item):
        return self._translator.translate(item)

    def set_lang(self, lang):
        self._translator.set_lang(lang)


inventory = Blueprint('inventory', __name__)
m = Manager(sort_items=True)
m.add_filter(filter_1)
m.add_filter(filter_2)
m.add_filter(filter_3)
m.add_filter(filter_4)
m.add_filter(filter_5)
m.add_filter(filter_6)


@inventory.before_request
def adjust_locale_inv():
    m.set_lang(str(flask_babel.get_locale()))


@inventory.route('/')
def index():
    return render_template('index.html', manager=m, MAX_APIKEY=MAX_APIKEY)


@inventory.route('/error/<error_type>')
def error(error_type):
    if error_type == 'invalid_key':
        return render_template('error_invalid_key.html')
    if error_type == 'invalid_permission':
        return render_template('error_invalid_permission.html')


@inventory.route('/list/', methods=['POST'])
def list():
    guilds_id = []
    filter = request.form['filter']
    for i in range(MAX_APIKEY):
        try:
            key = request.form['api_key{}'.format(i)]
            if key:
                apikey = APIKey(key, 'Guild')
                # If we don't have a guild APIKey, InvalidAPIKey will be thrown
                # So no need to check the apikey type
                gid = m.add_guild(str(apikey))
                guilds_id.append(gid)
        except InvalidAPIKeyException:
                return redirect(url_for('.error', error_type='invalid_key'))
        except InvalidPermissionException:
            return redirect(url_for('.error', error_type='invalid_permission'))
    m.refresh_guilds()
    m.set_current_guilds(guilds_id)
    m.set_filter(int(filter))
    return render_template('list.html', manager=m)
