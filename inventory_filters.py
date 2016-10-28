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

# Gettext hack
_ = lambda x: x


class Filter:
    def __init__(self, filter, description="", quantity=0):
        self.func = filter
        self.description = lambda: description
        self.quantity = lambda: quantity

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def is_material(item):
    return "material" in item.tags
dummy_filter = Filter(lambda item: True,
                      _("Display everything"),
                      0)

filter_1 = Filter(is_material,
                  _("All materials"),
                  0)

filter_2 = Filter(lambda item: any(x in item.tags for x in ["base", "fine", "choice"]) and is_material(item),
                  _("Materials to level-up craft"),
                  0)

filter_3 = Filter(lambda item: is_material(item) and "supreme" in item.tags,
                  _("Excess Supreme materials"),
                  50)

filter_4 = Filter(lambda item: is_material(item) and all(x in item.tags for x in ["supreme", "harvested"]),
                  _('Harvested Supreme materials'),
                  0)

filter_5 = Filter(lambda item: item.sheet == 'm0155dxapf01' and item.quality == 250,
                  _("Zun sup !!"),
                  0)


def is_armor_supreme(item):
    grade = all(x in item.tags for x in ["material", "supreme", "harvested"])
    part = any(x in item.tags for x in ["armor_shell", "armor_clip", "lining", "stuffing"])
    return grade and part

filter_6 = Filter(is_armor_supreme,
                  _("Supreme HA harvested armor materials"),
                  0)
