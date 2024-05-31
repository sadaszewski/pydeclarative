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


from pydeclarative.htmlwidgets import Div, \
    elem_to_html, \
    get_engine, \
    get_node
import bs4
import datetime


class Toast(Div):
    title = "Bootstrap"
    message = "Toast message"
    autohide = True
    color = "primary"
    @property
    def html(scope):
        res = bs4.BeautifulSoup(f'''<div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
    <div class="toast-header">
      <div style="width: 20px; height: 20px;" class="bg-{scope.color} rounded me-2"> </div>
      <strong class="me-auto">{scope.title}</strong>
      <small>{datetime.datetime.now().isoformat(timespec='minutes', sep=' ')}</small>
      <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body">
      {scope.message}
    </div>
    <script type="text/javascript">
      $("#''' + get_node(scope).uuid + f'''").toast({{ autohide: { 'true' if scope.autohide else 'false' } }}).toast("show")
      $("#''' + get_node(scope).uuid + '''").on("hidden.bs.toast", function() { window.PYDECLARATIVE.nativeEvent($("#'''+ get_node(scope).uuid + '''")[0], "hidden.bs.toast") })
    </script>
  </div>''', 'xml').find()
        return elem_to_html(scope, res)

    def handle_dom_event(scope, event):
        if event['event'] == 'native_event' and event['event_name'] == 'hidden.bs.toast':
            get_engine(scope).unload(get_node(scope))


class ToastContainer(Div):
    css_class = [ 'toast-container', 'position-fixed', 'bottom-0', 'end-0', 'p-3' ]
    def add_toast(scope, title, message, autohide=True, color='primary', delegate=Toast):
        get_engine(scope).load(delegate, is_root=True, parent=get_node(scope),
            provided_values=dict(title=title, message=message, autohide=autohide, color=color))
