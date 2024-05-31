'''
renderHtmlAsync in shiny.js has to be modified as follows:

function renderHtmlAsync(_x3, _x4, _x5) {
    var res  = _renderHtmlAsync.apply(this, arguments);
    res = res.then(function(res) {
      //console.log('render html async done');
      $(document).trigger('shiny:renderhtmlasyncdone', _x4)
      return res;
    });
    return res;
  }
'''

from shiny import App, reactive, ui, render, Session, module
import pandas as pd
import numpy as np
import time
from collections import defaultdict
from examples.uibench import tests
from examples.uibench import Table, \
    Tree, \
    Anim, \
    CSS
import logging


@module.ui
def table_ui():
    return ui.div(
        ui.output_ui('tableHtml')
    )


@module.server
def table_server(input, output, session, rows=None, columns=None, sort_column=None, filter=None, activate=None):
    rows = rows or reactive.Value(2)
    columns = columns or reactive.Value(2)
    sort_column = sort_column or reactive.Value(None)
    filter = filter or reactive.Value(None)
    activate = activate or reactive.Value(None)

    @render.ui
    def tableHtml():
        scope = lambda: 0
        scope.rows = rows()
        scope.columns = columns()
        scope.sort_column = sort_column()
        scope.filter = filter()
        scope.activate = activate()
        return ui.HTML(Table.html.fget(scope))


@module.ui
def tree_ui():
    return ui.div(
        ui.output_ui('treeHtml')
    )


@module.server
def tree_server(input, output, session,
    nodes_per_level = None,
    reverse = None,
    insert_first = None,
    insert_last = None,
    remove_first = None,
    remove_last = None,
    move_from_end_to_start = None,
    move_from_start_to_end = None):

    nodes_per_level = nodes_per_level or reactive.Value([0])
    reverse = reverse or reactive.Value(False)
    insert_first = insert_first or reactive.Value(0)
    insert_last = insert_last or reactive.Value(0)
    remove_first = remove_first or reactive.Value(0)
    remove_last = remove_last or reactive.Value(0)
    move_from_end_to_start = move_from_end_to_start or reactive.Value(0)
    move_from_start_to_end = move_from_start_to_end or reactive.Value(0)

    @render.ui
    def treeHtml():
        scope = lambda: 0
        scope.nodes_per_level = nodes_per_level()
        scope.reverse = reverse()
        scope.insert_first = insert_first()
        scope.insert_last = insert_last()
        scope.remove_first = remove_first()
        scope.remove_last = remove_last()
        scope.move_from_end_to_start = move_from_end_to_start()
        scope.move_from_start_to_end = move_from_start_to_end()
        return ui.HTML(Tree.html.fget(scope))


@module.ui
def anim_ui():
    return ui.div(
        ui.output_ui('animHtml')
    )


@module.server
def anim_server(input, output, session, count=None, time=None, advance_every_nth=None):
    count = count or reactive.Value(100)
    time = time or reactive.Value(0)
    advance_every_nth = advance_every_nth or reactive.Value(None)

    @render.ui
    def animHtml():
        scope = lambda: 0
        scope.count = count()
        scope.time = time()
        scope.advance_every_nth = advance_every_nth()
        return ui.HTML(Anim.html.fget(scope))


app_ui = ui.page_fluid(
    ui.input_action_button('start_btn', 'Start benchmark'),
    ui.input_action_button('next_btn', 'Next'),
    ui.output_table('resultsTable'),
    table_ui('table'),
    tree_ui('tree'),
    anim_ui('anim'),
    ui.tags.style(CSS,
        type='text/css'),
    ui.tags.script('''
        $(function() {
            Shiny.addCustomMessageHandler('uibench_info', function(message) {
                // console.log('uibench_info: ' + JSON.stringify(message))
                // window.uibench_info = Object.assign({}, message)
                window.renderDoneCounter = message.number_of_components_about_to_be_updated
                if (window.renderDoneCounter === 0) {
                    window.requestAnimationFrame(function() { $('#next_btn').click() })
                }
            })
            $(document).on('shiny:renderhtmlasyncdone', function(ev, el) {
                console.log('shiny:renderhtmlasyncdone ' + el.id)
                if (!window.uibench_has_started)
                   return
                if (el.id === 'table-tableHtml' || el.id === 'tree-treeHtml' || el.id === 'anim-animHtml') {
                    window.renderDoneCounter -= 1
                    if (window.renderDoneCounter === 0) {
                        window.requestAnimationFrame(function() { $('#next_btn').click() })
                    }
                }
            })
            $('#start_btn').on('click', function() { console.log('start btn clicked'); window.uibench_has_started = true })
        })
''')
)

def server(input, output, session: Session):
    n_iterations = 5
    iter_counter = 0
    counter = 0
    timestamp = None
    results = defaultdict(lambda: [])
    df = reactive.Value(pd.DataFrame())

    table = dict(
        rows = reactive.Value(2),
        columns = reactive.Value(2),
        sort_column = reactive.Value(None),
        filter = reactive.Value(None),
        activate = reactive.Value(None))

    table_server('table', rows=table['rows'], columns=table['columns'], 
        sort_column=table['sort_column'], filter=table['filter'],
        activate=table['activate'])
    
    tree = dict(nodes_per_level = reactive.Value([0]),
        reverse = reactive.Value(False),
        insert_first = reactive.Value(0),
        insert_last = reactive.Value(0),
        remove_first = reactive.Value(0),
        remove_last = reactive.Value(0),
        move_from_end_to_start = reactive.Value(0),
        move_from_start_to_end = reactive.Value(0))
    
    tree_server('tree', nodes_per_level = tree['nodes_per_level'],
        reverse = tree['reverse'],
        insert_first = tree['insert_first'],
        insert_last = tree['insert_last'],
        remove_first = tree['remove_first'],
        remove_last = tree['remove_last'],
        move_from_end_to_start = tree['move_from_end_to_start'],
        move_from_start_to_end = tree['move_from_start_to_end'])
    
    anim = dict(count=reactive.Value(0),
        time=reactive.Value(0),
        advance_every_nth=reactive.Value(None))
    
    anim_server('anim', count=anim['count'],
        time=anim['time'],
        advance_every_nth=anim['advance_every_nth'])
    
    scope = dict(table=table, tree=tree, anim=anim)
    
    @render.table
    def resultsTable():
        return df()

    @reactive.effect
    @reactive.event(input.start_btn)
    async def _():
        await start()

    async def start():
        nonlocal iter_counter
        results.clear()
        iter_counter = 0
        await start_iter()
        
    async def start_iter():
        nonlocal counter
        nonlocal timestamp
        counter = -1
        timestamp = time.time()
        await execute_step()

    @reactive.effect
    @reactive.event(input.next_btn)
    async def _():
        await execute_step()

    async def execute_step():
        nonlocal iter_counter
        nonlocal counter
        nonlocal timestamp
        print('next_btn clicked')
        t = time.time()
        counter += 1
        if counter > 0 and counter % 2 == 0:
            test_name = tests[counter // 2 - 1][0]
            results[test_name].append(t - timestamp)
        logging.getLogger().warn(f'{counter} {(t - timestamp) * 1000 // 1}ms')
        if counter % 2 == 1:
            time.sleep(0.25)
        timestamp = time.time()

        if counter // 2 < len(tests):
            feed = tests[counter // 2][1 + counter % 2]
            await session.send_custom_message('uibench_info', dict(number_of_components_about_to_be_updated=len(feed)))
            logging.getLogger().warn(f'feed: {feed}')
            for el in feed:
                for k, v in el[1].items():
                    scope[el[0]][k].set(v)
        else:
            if iter_counter < n_iterations - 1:
                iter_counter += 1
                await start_iter()
            else:
                stop()

    def stop():
        res = []
        for name, measurements in results.items():
            res.append([ name, np.mean(measurements) * 1000, np.std(measurements) * 1000, ','.join(map(lambda r: '%.02f' % (r * 1000), measurements)), 'ms' ])
        res = pd.DataFrame(res, columns=['Test', 'Mean', 'Std', 'All', 'Units'])
        df.set(res)


app = App(app_ui, server)