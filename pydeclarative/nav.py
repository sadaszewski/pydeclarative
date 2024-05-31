#
# Copyright (C) Stanislaw Adaszewski <s DOT adaszewski AT gmail DOT com>, 2024.
#
# This file is part of PyDeclarative.
#
# PyDeclarative is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# PyDeclarative is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more 
# details.
#
# You should have received a copy of the GNU Lesser General Public License along 
# with PyDeclarative. If not, see <https://www.gnu.org/licenses/>.
#


from .htmlwidgets import Item, \
    elem_to_html, \
    get_node, \
    get_engine
import bs4


class TabPane(Item):
    first = False
    @property
    def html(scope):
        res = bs4.BeautifulSoup(f'''<div class="tab-pane fade{' show active' if scope.first else ''}" role="tabpanel" aria-labelledby="pills-{get_node(scope).uuid}" tabindex="0"><div data-content-item="data-content-item"></div></div>''', 'xml').find()
        return elem_to_html(scope, res)
    def make_current(scope):
        parent = get_node(scope.parent)
        index = parent.children.index(get_node(scope).real_self)
        get_engine(scope).execute_js(f'''$("#{parent.uuid} .nav-pills li:nth({index}) button").click()''')


class NavPills(Item):
    tab_names = []
    @property
    def html(scope):
        res = bs4.BeautifulSoup('''<div>
    <ul class="nav nav-pills" role="tablist">
    </ul>
    <div class="tab-content" data-content-item="data-content-item">
    </div>
</div>''', 'xml').find()
        for i, name in enumerate(scope.tab_names):
            uuid = get_node(scope).children[i].uuid
            res.find('ul').append(bs4.BeautifulSoup(f'''<li class="nav-item" role="presentation">
                <button class="nav-link{' active' if i == 0 else ''}" data-bs-toggle="pill" data-bs-target="#{uuid}" id="pills-{uuid}" type="button" role="tab" aria-controls="{uuid}" aria-selected="{'true' if i == 0 else 'false'}">{name}</button>
            </li>''', 'xml').find())
        return elem_to_html(scope, res)
