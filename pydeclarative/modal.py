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


from .htmlwidgets import *
from .htmlwidgets import get_engine, \
    get_node, \
    elem_to_html
import bs4
from .engine import Binding
from .signal import Signal


class Modal(Item):
    @property
    def html(scope):
        elem = bs4.BeautifulSoup('''
                <div class="modal fade" tabindex="-1">
          <div class="modal-dialog">
            <div class="modal-content" data-content-item="data-content-item">
            </div>
          </div>
        </div>''', 'xml').find()
        return elem_to_html(scope, elem)
    def open(scope):
        get_engine(scope).execute_js('''$("#''' + get_node(scope).uuid + '''").modal({ backdrop: "static", keyboard: false }).modal("show")''')
    def close(scope):
        get_engine(scope).execute_js('''$("#''' + get_node(scope).uuid + '''").modal("hide")''')


class ModalHeader(Div):
    title = 'Dialog'
    close_button = True
    @property
    def html(scope):
      elem = bs4.BeautifulSoup('''
        <div class="modal-header">
          <h5 class="modal-title">Modal title</h5>
        </div>''', 'xml').find()
      if scope.close_button:
          elem.append(bs4.BeautifulSoup('''<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>''', 'xml').find())
      next(elem.find('h5').children).replace_with(scope.title)
      return elem_to_html(scope, elem)


class ModalBody(Div):
    @property
    def html(scope):
        elem = bs4.BeautifulSoup('''<div class="modal-body" data-content-item="data-content-item">
        </div>''', 'xml').find()
        return elem_to_html(scope, elem)


class ModalFooter(Div):
    @property
    def html(scope):
        elem = bs4.BeautifulSoup('''<div class="modal-footer" data-content-item="data-content-item">
        </div>''', 'xml').find()
        return elem_to_html(scope, elem)


class StandardModal(Modal):
    title = 'Standard Modal'
    message = 'Hello, world!'
    accept_button_text = 'OK'
    reject_button_text = 'Close'
    accepted = Signal()
    rejected = Signal()

    class _header(ModalHeader):
        title = Binding(lambda scope: scope.parent.title)
        close_button = False
    class _body(ModalBody):
        class _textOutput(TextOutput):
            text = Binding(lambda scope: scope.parent.parent.message)
    class _footer(ModalFooter):
        class _closeBtn(Button):
            display = Binding(lambda scope: scope.StandardModal.reject_button_text is not None)
            text = Binding(lambda scope: scope.StandardModal.reject_button_text or '')
            button_class = "secondary"
            def on_clicked(scope):
                scope.StandardModal.close()
                scope.StandardModal.rejected()
        class _okBtn(Button):
            display = Binding(lambda scope: scope.StandardModal.accept_button_text is not None)
            text = Binding(lambda scope: scope.StandardModal.accept_button_text or '')
            def on_clicked(scope):
                scope.StandardModal.close()
                scope.StandardModal.accepted()


class MessageBox(StandardModal):
    reject_button_text = None

    def show(scope, title, message, accept_button_text='OK'):
        scope.title = title
        scope.message = message
        scope.accept_button_text = accept_button_text
        scope.open()


class HTMLOutput(Item):
    content = '<p>HTMLOutput</p>'
    @property
    def html(scope):
        return scope.content
