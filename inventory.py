#!/usr/bin/python3
import json

from flask import Blueprint, render_template

import flask_babel

from lib import load_data, Translator, required_roles, data_need_reload
from inventory_filters import dummy_filter, filter_3, filter_4, filter_6
# Gettext hack
_ = lambda x: x


class Manager:
    def __init__(self, sort_items):
        self._translator = Translator('en')
        self._guilds = []
        self._filters = []
        self._sort_items = sort_items
        with open("data/guilds.json", "r") as f:
            keys = json.load(f)
            for k in keys:
                tmp = load_data(k, self._sort_items)
                tmp.api_key = k
                self._guilds.append(tmp)
        self.add_filter(dummy_filter)
        self.current_filter = self._filters[0]
        self.current_guild = None

    def add_filter(self, f):
        self._filters.append(f)

    def refresh_guilds(self):
        for g in self._guilds:
            if data_need_reload(g.api_key):
                g = load_data(g.api_key, self._sort_items)

    def get_items(self):
        items = []
        pick_from = []
        if self.current_guild:
            pick_from = [self.current_guild]
        else:
            pick_from = self._guilds

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
    def guilds(self):
        dummy = {"gid": "all", "name": _('All guilds')}
        yield dummy
        yield from self._guilds

    # Used by templates
    def filters(self):
        yield from enumerate(self._filters)

    # Used by templates
    def tooltip(self, item):
        out = self.translation(item)
        for guild, number in item.origins:
            out += " - {} ({})".format(guild.name, number)
        return out

    # Used by templates
    def title(self):
        if self.current_guild:
            out = _('{} - {}'.format(self.current_guild.name, self.current_filter.description()))
        else:
            out = _('{} - {}'.format(_('All guilds'), self.current_filter.description()))
        return out

    def set_guild(self, id):
        if id == 'all':
            self.id = id
            self.current_guild = None
        else:
            self.id = int(id)
            self.current_guild = next(x for x in self._guilds if x.gid == self.id)

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


def first_filter(item):
    return all(x in item.tags for x in ["material", "supreme"])

inventory = Blueprint('inventory', __name__)
m = Manager(sort_items=True)
m.add_filter(filter_3)
m.add_filter(filter_4)
m.add_filter(filter_6)


@inventory.before_request
def adjust_locale_inv():
    m.set_lang(str(flask_babel.get_locale()))


@inventory.route('/')
@required_roles('user')
def index():
    return render_template('inventory/index.html', manager=m)


@inventory.route('/list/<guild>/<filter>/')
@required_roles('user')
def list_inventory(guild, filter):
    m.refresh_guilds()
    m.set_guild(guild)
    m.set_filter(int(filter))
    return render_template('inventory/list.html', manager=m)
