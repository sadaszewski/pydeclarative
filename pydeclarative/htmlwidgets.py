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


import bs4
import logging
import pdb
import asyncio
import json
import copy
from .signal import Signal


__all__ = [ 'Item', 'Div', 'TextInput', 'PasswordInput', 'TextOutput', 'Button',
    'Image', 'Timer', 'Terminal', 'Repeater', 'Delegate', 'delegate', 'Link',
    'PandasDataFrame', 'PlotlyPlot', 'Connections' ]


def get_node(scope):
    return scope.__dict__['node']


def get_engine(scope):
    return scope.__dict__['node'].engine


def has_property(node, name):
    return (name in node.properties)


def add_standard_attributes(scope, elem):
    node = get_node(scope)
    if has_property(node, 'css_class'):
        css_class = scope.css_class
        if isinstance(css_class, str):
            # pdb.set_trace()
            css_class = css_class.split()
        elem.attrs['class'] = ' '.join(elem.attrs.get('class', '').split() + css_class)
    css_style = scope.css_style \
        if has_property(node, 'css_style') else {}
    if not isinstance(css_style, str):
        css_style = ' '.join(f'{k}: {v};' for k, v in css_style.items())
    if has_property(node, 'display') and scope.display != True:
        css_style = ' '.join([ css_style, f'display: {"none" if scope.display == False else scope.display};' ]).strip()
    elem.attrs['style'] = ' '.join([ elem.attrs.get('style', ''),
        css_style ]).strip()
    if has_property(node, 'disabled'):
        if scope.disabled:
            elem.attrs['disabled'] = 'disabled'
        elif 'disabled' in elem.attrs:
            del elem.attrs['disabled']
    return elem


def elem_to_html(scope, elem):
    add_standard_attributes(scope, elem)
    return str(elem)


class Delegate:
    def __init__(self, delegate):
        self.delegate = delegate


def delegate(cls):
    return Delegate(cls)


class Item:
    loaded = Signal()
    unloaded = Signal()

    @property
    def html(scope):
        res = bs4.BeautifulSoup('<div data-content-item="data-content-item"></div>', 'xml').find()
        return elem_to_html(scope, res)
    def handle_dom_event(scope):
        pass


class Div(Item):
    @property
    def html(scope):
        res = bs4.BeautifulSoup('''<div data-content-item="data-content-item"></div>''', 'xml').find()
        return elem_to_html(scope, res)


class TextInput(Item):
    text = ''
    placeholder = ''
    input_type = 'text'

    @property
    def html(scope):
        res = bs4.BeautifulSoup(f'''<input type="{scope.input_type}" class="form-control" oninput="PYDECLARATIVE.valueChanged(this, 'value', 'text')" />''', 'xml')
        res = res.find()
        res['value'] = scope.text or ''
        res['placeholder'] = scope.placeholder or ''
        return elem_to_html(scope, res)

    def handle_dom_event(scope, event):
        logger = logging.getLogger()
        logger.info('TextInput.handle_dom_event() ' + str(event))
        if event['event'] == 'value_changed' and event['property_name'] == 'text':
            scope.text = str(event['new_value'])
        else:
            raise ValueError('Unrecognized event: ' + event['event'])


class PasswordInput(TextInput):
    input_type = 'password'


class TextOutput(Item):
    text = ""

    @property
    def html(scope):
        res = bs4.BeautifulSoup('<div></div>', 'xml')
        res = res.find()
        # pdb.set_trace()
        res.append(bs4.NavigableString(scope.text or ''))
        return elem_to_html(scope, res)


class Button(Item):
    text = 'Button'
    button_class = 'primary'
    is_outline_button = False
    clicked = Signal()

    @property
    def html(scope):
        res = bs4.BeautifulSoup('''<button type="button" onclick="PYDECLARATIVE.nativeEvent(this, 'clicked')" />''', 'xml').find()
        res['class'] = 'btn ' + '-'.join([ 'btn' ] + \
            ([ 'outline'] if scope.is_outline_button else []) + [ scope.button_class ])
        res.append(scope.text)
        return elem_to_html(scope, res)

    def handle_dom_event(scope, event):
        if event['event'] == 'native_event' and event['event_name'] == 'clicked':
            scope.clicked()


class Image(Item):
    source = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH6AMYECc4Ci+fZAAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAAAaklEQVQoz7VSQQ6AIAzbDM9B5v8/IeqDyoE4cVECGnoazQq0GwOgHkzUCUdEyywlFY8tFyWvJAEQH3BCfNCj4XNhv3TddMe6x/xgqwdm/mjaCkwAzym9BlIR1Jt+DW6YQE26xj41ycO3NQHYVD6rKqdMoAAAAABJRU5ErkJggg=='
    text = 'Image'
    format = 'png'

    @property
    def html(scope):
        from PIL import Image
        from io import BytesIO
        from base64 import b64encode
        source = scope.source
        if isinstance(source, Image.Image):
            buf = BytesIO()
            source.save(buf, scope.format)
            source = 'data:image/' + scope.format.lower() + ';base64,' + \
                b64encode(buf.getvalue()).decode('latin-1')
        res = bs4.BeautifulSoup('<img />', 'xml').find()
        res['src'] = source
        res['alt'] = scope.text
        return elem_to_html(scope, res)


class Timer(Item):
    interval = 1
    task = None
    running = True
    triggered = Signal()

    async def timer(scope):
        while True:
            await asyncio.sleep(scope.interval)
            try:
                scope.triggered()
            except Exception as e:
                get_node(scope).engine.send_global_message('backend_exception', dict(exception=str(e)))

    def on_loaded(scope):
        from .engine import get_engine
        logger = logging.getLogger()
        if scope.running:
            scope.task = get_engine(scope).create_task(scope.timer())
        logger.info('Created timer')

    def on_unloaded(scope):
        if scope.task:
            scope.task.cancel()

    def on_triggered(scope):
        logger = logging.getLogger()
        logger.info('Timer triggered')

    def on_running_changed(scope):
        if scope.running:
            scope.task = get_engine(scope).create_task(scope.timer())
        else:
            scope.task.cancel()
            scope.task = None


class Terminal(Item):
    @property
    def html(scope):
        res = '''
<div data-content-item="data-content-item">
<script type="text/javascript">
console.log("Here!")
PYDECLARATIVE.addCustomMessageHandler($('#''' + get_node(scope).uuid + ''''), 'append', function(ev) {
    $(this).find('pre')[0].innerText += ev.text
})
</script>
<pre></pre>
</div>
        '''
        return res


class Repeater(Item):
    delegate = None
    model = None

    @property
    def html(scope):
        res = bs4.BeautifulSoup('<div data-content-item="data-content-item"></div>', 'xml').find()
        return elem_to_html(scope, res)

    def on_loaded(scope):
        # pdb.set_trace()
        if not (scope.delegate is not None and scope.model is not None):
            return
        for i in range(len(scope.model)):
            model_data = scope.model.get(i)
            get_engine(scope).load(scope.delegate.delegate, is_root=True,
                parent=get_node(scope), provided_values=dict(index=i, model_data=model_data))
        scope.model.item_added.connect(scope.item_added_cb)
        scope.model.item_removed.connect(scope.item_removed_cb)
        scope.model.item_updated.connect(scope.item_updated_cb)
        scope.model.model_reseted.connect(scope.model_reseted_cb)

    def item_added_cb(scope, index):
        from .engine import Scope
        model_data = scope.model.get(index)
        get_engine(scope).load(scope.delegate.delegate, is_root=True,
            parent=get_node(scope), provided_values=dict(index=index, model_data=model_data),
            index=index)
        for i in range(index + 1, len(scope.model)):
            Scope(get_node(scope).children[i]).index = i

    def item_removed_cb(scope, index):
        from .engine import Scope
        node = get_node(scope).children[index]
        get_engine(scope).unload(node)
        for i in range(index, len(scope.model)):
            Scope(get_node(scope).children[i]).index = i

    def item_updated_cb(scope, index):
        from .engine import Scope
        model_data = scope.model.get(index)
        Scope(get_node(scope).children[index]).model_data = model_data

    def model_reseted_cb(scope):
        for node in list(get_node(scope).children):
            get_engine(scope).unload(node)


class Link(Item):
    text = 'Link'
    href = '#'
    clicked = Signal()

    @property
    def html(scope):
        res = bs4.BeautifulSoup('''<a onclick="PYDECLARATIVE.nativeEvent(this, 'clicked'); return false;" />''', 'xml').find()
        if scope.href:
            res.attrs['href'] = scope.href
        res.append(bs4.NavigableString(scope.text or ''))
        return elem_to_html(scope, res)

    def handle_dom_event(scope, event):
        if event['event'] == 'native_event' and event['event_name'] == 'clicked':
            scope.clicked()


class ConstPandasDataFrame(Item):
    dataframe = None
    css_class = [ 'table', 'table-striped', 'table-hover' ]
    css_style = { 'width': '100%' }
    use_datatables_net = False

    @property
    def html(scope):
        if scope.dataframe is not None:
            if scope.dataframe.index is not None and scope.dataframe.index.name:
                scope.dataframe.columns.name = scope.dataframe.index.name
                scope.dataframe.index.name = None
            res = bs4.BeautifulSoup(scope.dataframe.to_html(), 'xml').find()
            res.find('tbody').attrs['class'] = 'table-group-divider'
            del res.find('thead').find('tr').attrs['style']
            if scope.use_datatables_net:
                res.append(bs4.BeautifulSoup('''<script>new DataTable("#''' + get_node(scope).uuid + '''")</script>''', 'xml').find())
        else:
            res = bs4.BeautifulSoup('<div data-content-item="data-content-item" />').find()
        return elem_to_html(scope, res)


class PandasDataFrame(Item):
    dataframe = None
    css_class = [ 'table', 'table-striped', 'table-hover' ]
    css_style = { 'width': '100%' }
    use_datatables_net = False
    _table = None

    @property
    def html(scope):
        res = bs4.BeautifulSoup('<div data-content-item="data-content-item" />', 'xml').find()
        return elem_to_html(scope, res)
    
    def update_table(scope):
        if scope._table is not None:
            get_engine(scope).execute_js('''$("#''' + scope._table.uuid + '''").DataTable().destroy()''')
            get_engine(scope).unload(scope._table)
            scope._table = None
        class table(ConstPandasDataFrame):
            dataframe = copy.deepcopy(scope.dataframe)
            css_class = copy.deepcopy(scope.css_class)
            css_style = copy.deepcopy(scope.css_style)
            use_datatables_net = scope.use_datatables_net
        scope._table = get_engine(scope).load(table, is_root=True, parent=get_node(scope))

    def on_loaded(scope):
        print('PandasDataFrame.on_loaded()')
        scope.update_table()

    def on_dataframe_changed(scope):
        print('PandasDataFrame.on_dataframe_changed()')
        scope.update_table()

    def on_css_class_changed(scope):
        print('PlotlyPlot.on_css_class_changed()')
        scope.update_table()

    def on_css_style_changed(scope):
        print('PlotlyPlot.on_css_style_changed()')
        scope.update_table()

    def on_use_datatables_net_changed(scope):
        print('PlotlyPlot.on_use_datatables_net_changed()')
        scope.update_table()


class ConstPlotlyPlot(Item):
    data = []
    layout = {}

    @property
    def html(scope):
        res = bs4.BeautifulSoup('<div />', 'xml').find()
        res.append(bs4.BeautifulSoup('''
<script type="text/javascript">
    var data = ''' + json.dumps(scope.data) + '''
    var layout = ''' + json.dumps(scope.layout) + '''
    Plotly.newPlot("''' + get_node(scope).uuid + '''", data, layout)
</script>''', 'xml').find())
        return elem_to_html(scope, res)


class PlotlyPlot(Item):
    data = []
    layout = {}
    _plot = None

    @property
    def html(scope):
        res = bs4.BeautifulSoup('<div data-content-item="data-content-item" />', 'xml').find()
        return elem_to_html(scope, res)
    
    def update_plot(scope):
        if scope._plot is not None:
            get_engine(scope).unload(scope._plot)
            scope._plot = None
        class plot(ConstPlotlyPlot):
            data = copy.deepcopy(scope.data)
            layout = copy.deepcopy(scope.layout)
        scope._plot = get_engine(scope).load(plot, is_root=True, parent=get_node(scope))

    def on_loaded(scope):
        print('PlotlyPlot.on_loaded()')
        scope.update_plot()

    def on_data_changed(scope):
        print('PlotlyPlot.on_data_changed()')
        scope.update_plot()

    def on_layout_changed(scope):
        print('PlotlyPlot.on_layout_changed()')
        scope.update_plot()


class Connections(Item):
    target = None

    def on_loaded(scope):
        target = get_node(scope.target)
        node = get_node(scope)
        for k in node.functions.keys():
            if k.startswith('on_') and k.endswith('_changed'):
                name = k[3:-8]
                target.properties[name].change_signal.connect(scope[k])
            elif k.startswith('on_') and k not in [ 'on_loaded' ]:
                name = k[3:]
                target.properties[name].value.connect(scope[k])
