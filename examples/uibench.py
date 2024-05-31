from pydeclarative import *
import bs4
import time
import pandas as pd
import numpy as np
import logging
from collections import defaultdict


alphabet = '72341523574132464597403259245'


'''
tests_hold3 = [
    ('tree/[10,10,10,10]/no_change/prerun',
        [ ('tree', dict(move_from_start_to_end=0, nodes_per_level=[10, 10, 10, 10])) ],
        [] ),
]


tests_hold2 = [
    ('tree/[10,10,10,10]/no_change/prerun',
        [ ('tree', dict(move_from_start_to_end=0, nodes_per_level=[10, 10, 10, 10])) ],
        [] ),
    ('tree/[10,10,10,10]/no_change',
        [ ('tree', dict(move_from_start_to_end=0, nodes_per_level=[10, 10, 10, 10])) ],
        [] ),
    ('tree/[2,2,2,2,2,2,2,2,2,2]/no_change/prerun',
        [ ('tree', dict(nodes_per_level=[2, 2, 2, 2, 2, 2, 2, 2, 2, 2])) ],
        [] ),
    ('tree/[2,2,2,2,2,2,2,2,2,2]/no_change',
        [ ('tree', dict(nodes_per_level=[2, 2, 2, 2, 2, 2, 2, 2, 2, 2])) ],
        [] ),
]
'''


tests = [
    ('table/[100,4]/render',
        [ ('table', dict(rows=0, columns=0)) ],
        [ ('table', dict(rows=100, columns=4)) ]),
    ('table/[50,4]/render',
        [ ('table', dict(rows=0, columns=0)) ],
        [ ('table', dict(rows=50, columns=4)) ]),
    ('table/[100,2]/render',
        [ ('table', dict(rows=0, columns=0)) ],
        [ ('table', dict(rows=100, columns=2)) ]),
    ('table/[50,2]/render',
        [ ('table', dict(rows=0, columns=0)) ],
        [ ('table', dict(rows=50, columns=2)) ]),

    ('table/[100,4]/removeAll',
        [ ('table', dict(rows=100, columns=4)) ],
        [ ('table', dict(rows=0, columns=0)) ]),
    ('table/[50,4]/removeAll',
        [ ('table', dict(rows=50, columns=4)) ],
        [ ('table', dict(rows=0, columns=0)) ]),
    ('table/[100,2]/removeAll',
        [ ('table', dict(rows=100, columns=2)) ],
        [ ('table', dict(rows=0, columns=0)) ]),
    ('table/[50,2]/removeAll',
        [ ('table', dict(rows=50, columns=2)) ],
        [ ('table', dict(rows=0, columns=0)) ]),

    ('table/[100,4]/sort/0',
        [ ('table', dict(rows=100, columns=4, sort_column=None)) ],
        [ ('table', dict(rows=100, columns=4, sort_column=0)) ]),
    ('table/[100,2]/sort/0',
        [ ('table', dict(rows=50, columns=4, sort_column=None)) ],
        [ ('table', dict(rows=50, columns=4, sort_column=0)) ]),
    ('table/[50,4]/sort/0',
        [ ('table', dict(rows=100, columns=2, sort_column=None)) ],
        [ ('table', dict(rows=100, columns=2, sort_column=0)) ]),
    ('table/[50,2]/sort/0',
        [ ('table', dict(rows=50, columns=2, sort_column=None)) ],
        [ ('table', dict(rows=50, columns=2, sort_column=0)) ]),

    ('table/[100,4]/sort/1',
        [ ('table', dict(rows=100, columns=4, sort_column=None)) ],
        [ ('table', dict(rows=100, columns=4, sort_column=1)) ]),
    ('table/[100,2]/sort/1',
        [ ('table', dict(rows=50, columns=4, sort_column=None)) ],
        [ ('table', dict(rows=50, columns=4, sort_column=1)) ]),
    ('table/[50,4]/sort/1',
        [ ('table', dict(rows=100, columns=2, sort_column=None)) ],
        [ ('table', dict(rows=100, columns=2, sort_column=1)) ]),
    ('table/[50,2]/sort/1',
        [ ('table', dict(rows=50, columns=2, sort_column=None)) ],
        [ ('table', dict(rows=50, columns=2, sort_column=1)) ]),

    ('table/[100,4]/filter/32',
        [ ('table', dict(rows=100, columns=4, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=100, columns=4, filter=32)) ]),
    ('table/[50,4]/filter/32',
        [ ('table', dict(rows=100, columns=2, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=100, columns=2, filter=32)) ]),
    ('table/[100,2]/filter/32',
        [ ('table', dict(rows=50, columns=4, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=50, columns=4, filter=32)) ]),
    ('table/[50,2]/filter/32',
        [ ('table', dict(rows=50, columns=2, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=50, columns=2, filter=32)) ]),

    ('table/[100,4]/filter/16',
        [ ('table', dict(rows=100, columns=4, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=100, columns=4, filter=16)) ]),
    ('table/[50,4]/filter/16',
        [ ('table', dict(rows=100, columns=2, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=100, columns=2, filter=16)) ]),
    ('table/[100,2]/filter/16',
        [ ('table', dict(rows=50, columns=4, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=50, columns=4, filter=16)) ]),
    ('table/[50,2]/filter/16',
        [ ('table', dict(rows=50, columns=2, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=50, columns=2, filter=16)) ]),

    ('table/[100,4]/filter/8',
        [ ('table', dict(rows=100, columns=4, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=100, columns=4, filter=8)) ]),
    ('table/[50,4]/filter/8',
        [ ('table', dict(rows=100, columns=2, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=100, columns=2, filter=8)) ]),
    ('table/[100,2]/filter/8',
        [ ('table', dict(rows=50, columns=4, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=50, columns=4, filter=8)) ]),
    ('table/[50,2]/filter/8',
        [ ('table', dict(rows=50, columns=2, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=50, columns=2, filter=8)) ]),

    ('table/[100,4]/filter/4',
        [ ('table', dict(rows=100, columns=4, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=100, columns=4, filter=4)) ]),
    ('table/[50,4]/filter/4',
        [ ('table', dict(rows=100, columns=2, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=100, columns=2, filter=4)) ]),
    ('table/[100,2]/filter/4',
        [ ('table', dict(rows=50, columns=4, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=50, columns=4, filter=4)) ]),
    ('table/[50,2]/filter/4',
        [ ('table', dict(rows=50, columns=2, sort_column=None, filter=None)) ],
        [ ('table', dict(rows=50, columns=2, filter=4)) ]),

     ('table/[100,4]/activate/32',
        [ ('table', dict(rows=100, columns=4, sort_column=None, filter=None, activate=None)) ],
        [ ('table', dict(rows=100, columns=4, activate=32)) ]),
    ('table/[50,4]/activate/32',
        [ ('table', dict(rows=100, columns=2, activate=None)) ],
        [ ('table', dict(rows=100, columns=2, activate=32)) ]),
    ('table/[100,2]/activate/32',
        [ ('table', dict(rows=50, columns=4, activate=None)) ],
        [ ('table', dict(rows=50, columns=4, activate=32)) ]),
    ('table/[50,2]/activate/32',
        [ ('table', dict(rows=50, columns=2, activate=None)) ],
        [ ('table', dict(rows=50, columns=2, activate=32)) ]),

    ('table/[100,4]/activate/16',
        [ ('table', dict(rows=100, columns=4, activate=None)) ],
        [ ('table', dict(rows=100, columns=4, activate=16)) ]),
    ('table/[50,4]/activate/16',
        [ ('table', dict(rows=100, columns=2, activate=None)) ],
        [ ('table', dict(rows=100, columns=2, activate=16)) ]),
    ('table/[100,2]/activate/16',
        [ ('table', dict(rows=50, columns=4, activate=None)) ],
        [ ('table', dict(rows=50, columns=4, activate=16)) ]),
    ('table/[50,2]/activate/16',
        [ ('table', dict(rows=50, columns=2, activate=None)) ],
        [ ('table', dict(rows=50, columns=2, activate=16)) ]),

    ('table/[100,4]/activate/8',
        [ ('table', dict(rows=100, columns=4, activate=None)) ],
        [ ('table', dict(rows=100, columns=4, activate=8)) ]),
    ('table/[50,4]/activate/8',
        [ ('table', dict(rows=100, columns=2, activate=None)) ],
        [ ('table', dict(rows=100, columns=2, activate=8)) ]),
    ('table/[100,2]/activate/8',
        [ ('table', dict(rows=50, columns=4, activate=None)) ],
        [ ('table', dict(rows=50, columns=4, activate=8)) ]),
    ('table/[50,2]/activate/8',
        [ ('table', dict(rows=50, columns=2, activate=None)) ],
        [ ('table', dict(rows=50, columns=2, activate=8)) ]),

    ('table/[100,4]/activate/4',
        [ ('table', dict(rows=100, columns=4, activate=None)) ],
        [ ('table', dict(rows=100, columns=4, activate=4)) ]),
    ('table/[50,4]/activate/4',
        [ ('table', dict(rows=100, columns=2, activate=None)) ],
        [ ('table', dict(rows=100, columns=2, activate=4)) ]),
    ('table/[100,2]/activate/4',
        [ ('table', dict(rows=50, columns=4, activate=None)) ],
        [ ('table', dict(rows=50, columns=4, activate=4)) ]),
    ('table/[50,2]/activate/4',
        [ ('table', dict(rows=50, columns=2, activate=None)) ],
        [ ('table', dict(rows=50, columns=2, activate=4)) ]),

    ('tree/[500]/render', 
        [ ('table', dict(rows=0, columns=0, sort_column=None, filter=None, activate=None)), ('tree', dict(nodes_per_level=[0])) ],
        [ ('tree', dict(nodes_per_level=[500])) ]),
    ('tree/[50,10]/render', 
        [ ('tree', dict(nodes_per_level=[0, 0]))],
        [ ('tree', dict(nodes_per_level=[50, 10])) ]),
    ('tree/[10,50]/render', 
        [ ('tree', dict(nodes_per_level=[0, 0]))],
        [ ('tree', dict(nodes_per_level=[10, 50])) ]),
    ('tree/[5,100]/render', 
        [ ('tree', dict(nodes_per_level=[0, 0]))],
        [ ('tree', dict(nodes_per_level=[5, 100])) ]),
    ('tree/[2,2,2,2,2,2,2,2,2,2]/render', 
        [ ('tree', dict(nodes_per_level=[0, 0]))],
        [ ('tree', dict(nodes_per_level=[2, 2, 2, 2, 2, 2, 2, 2, 2, 2])) ]),

    ('tree/[500]/removeAll', 
        [ ('tree', dict(nodes_per_level=[500])) ],
        [ ('tree', dict(nodes_per_level=[0])) ]),
    ('tree/[50,10]/removeAll', 
        [ ('tree', dict(nodes_per_level=[50, 10])) ],
        [ ('tree', dict(nodes_per_level=[0, 0])) ]),
    ('tree/[10,50]/removeAll', 
        [ ('tree', dict(nodes_per_level=[10, 50])) ],
        [ ('tree', dict(nodes_per_level=[0, 0])) ]),
    ('tree/[5,100]/removeAll', 
        [ ('tree', dict(nodes_per_level=[5, 100])) ],
        [ ('tree', dict(nodes_per_level=[0, 0]))]),
    ('tree/[2,2,2,2,2,2,2,2,2,2]/removeAll', 
        [ ('tree', dict(nodes_per_level=[2, 2, 2, 2, 2, 2, 2, 2, 2, 2])) ],
        [ ('tree', dict(nodes_per_level=[0, 0]))]),

    ('tree/[500]/reverse',
        [ ('tree', dict(nodes_per_level=[500], reverse=False)) ],
        [ ('tree', dict(nodes_per_level=[500], reverse=True)) ]),
    ('tree/[50,10]/reverse',
        [ ('tree', dict(nodes_per_level=[50, 10], reverse=False)) ],
        [ ('tree', dict(nodes_per_level=[50, 10], reverse=True)) ]),
    ('tree/[10,50]/reverse',
        [ ('tree', dict(nodes_per_level=[10, 50], reverse=False)) ],
       [ ('tree', dict(nodes_per_level=[10, 50], reverse=True)) ]),
    ('tree/[5,100]/reverse',
        [ ('tree', dict(nodes_per_level=[5, 100], reverse=False)) ],
        [ ('tree', dict(nodes_per_level=[5, 100], reverse=True)) ]),

    ('tree/[500]/[insertFirst(1)]',
        [ ('tree', dict(nodes_per_level=[500], reverse=False, insert_first=0)) ],
        [ ('tree', dict(nodes_per_level=[500], insert_first=1)) ]),
    ('tree/[50,10]/[insertFirst(1)]',
        [ ('tree', dict(nodes_per_level=[50, 10], insert_first=0)) ],
        [ ('tree', dict(nodes_per_level=[50, 10], insert_first=1)) ]),
    ('tree/[10,50]/[insertFirst(1)]',
        [ ('tree', dict(nodes_per_level=[10, 50], insert_first=0)) ],
       [ ('tree', dict(nodes_per_level=[10, 50], insert_first=1)) ]),
    ('tree/[5,100]/[insertFirst(1)]',
        [ ('tree', dict(nodes_per_level=[5, 100], insert_first=0)) ],
        [ ('tree', dict(nodes_per_level=[5, 100], insert_first=1)) ]),

    ('tree/[500]/[insertLast(1)]',
        [ ('tree', dict(nodes_per_level=[500], insert_first=0, insert_last=0)) ],
        [ ('tree', dict(nodes_per_level=[500], insert_last=1)) ]),
    ('tree/[50,10]/[insertLast(1)]',
        [ ('tree', dict(nodes_per_level=[50, 10], insert_last=0)) ],
        [ ('tree', dict(nodes_per_level=[50, 10], insert_last=1)) ]),
    ('tree/[10,50]/[insertLast(1)]',
        [ ('tree', dict(nodes_per_level=[10, 50], insert_last=0)) ],
       [ ('tree', dict(nodes_per_level=[10, 50], insert_last=1)) ]),
    ('tree/[5,100]/[insertLast(1)]',
        [ ('tree', dict(nodes_per_level=[5, 100], insert_last=0)) ],
        [ ('tree', dict(nodes_per_level=[5, 100], insert_last=1)) ]),

    ('tree/[500]/[removeFirst(1)]',
        [ ('tree', dict(nodes_per_level=[500], insert_last=0, remove_first=0)) ],
        [ ('tree', dict(nodes_per_level=[500], remove_first=1)) ]),
    ('tree/[50,10]/[removeFirst(1)]',
        [ ('tree', dict(nodes_per_level=[50, 10], remove_first=0)) ],
        [ ('tree', dict(nodes_per_level=[50, 10], remove_first=1)) ]),
    ('tree/[10,50]/[removeFirst(1)]',
        [ ('tree', dict(nodes_per_level=[10, 50], remove_first=0)) ],
       [ ('tree', dict(nodes_per_level=[10, 50], remove_first=1)) ]),
    ('tree/[5,100]/[removeFirst(1)]',
        [ ('tree', dict(nodes_per_level=[5, 100], remove_first=0)) ],
        [ ('tree', dict(nodes_per_level=[5, 100], remove_first=1)) ]),

    ('tree/[500]/[removeLast(1)]',
        [ ('tree', dict(nodes_per_level=[500], remove_first=0, remove_last=0)) ],
        [ ('tree', dict(nodes_per_level=[500], remove_last=1)) ]),
    ('tree/[50,10]/[removeLast(1)]',
        [ ('tree', dict(nodes_per_level=[50, 10], remove_last=0)) ],
        [ ('tree', dict(nodes_per_level=[50, 10], remove_last=1)) ]),
    ('tree/[10,50]/[removeLast(1)]',
        [ ('tree', dict(nodes_per_level=[10, 50], remove_last=0)) ],
       [ ('tree', dict(nodes_per_level=[10, 50], remove_last=1)) ]),
    ('tree/[5,100]/[removeLast(1)]',
        [ ('tree', dict(nodes_per_level=[5, 100], remove_last=0)) ],
        [ ('tree', dict(nodes_per_level=[5, 100], remove_last=1)) ]),

    ('tree/[500]/[moveFromEndToStart(1)]',
        [ ('tree', dict(nodes_per_level=[500], remove_last=0, move_from_end_to_start=0)) ],
        [ ('tree', dict(nodes_per_level=[500], move_from_end_to_start=1)) ]),
    ('tree/[50,10]/[moveFromEndToStart(1)]',
        [ ('tree', dict(nodes_per_level=[50, 10], move_from_end_to_start=0)) ],
        [ ('tree', dict(nodes_per_level=[50, 10], move_from_end_to_start=1)) ]),
    ('tree/[10,50]/[moveFromEndToStart(1)]',
        [ ('tree', dict(nodes_per_level=[10, 50], move_from_end_to_start=0)) ],
       [ ('tree', dict(nodes_per_level=[10, 50], move_from_end_to_start=1)) ]),
    ('tree/[5,100]/[moveFromEndToStart(1)]',
        [ ('tree', dict(nodes_per_level=[5, 100], move_from_end_to_start=0)) ],
        [ ('tree', dict(nodes_per_level=[5, 100], move_from_end_to_start=1)) ]),

    ('tree/[500]/[moveFromStartToEnd(1)]',
        [ ('tree', dict(nodes_per_level=[500], move_from_end_to_start=0, move_from_start_to_end=0)) ],
        [ ('tree', dict(nodes_per_level=[500], move_from_start_to_end=1)) ]),
    ('tree/[50,10]/[moveFromStartToEnd(1)]',
        [ ('tree', dict(nodes_per_level=[50, 10], move_from_start_to_end=0)) ],
        [ ('tree', dict(nodes_per_level=[50, 10], move_from_start_to_end=1)) ]),
    ('tree/[10,50]/[moveFromStartToEnd(1)]',
        [ ('tree', dict(nodes_per_level=[10, 50], move_from_start_to_end=0)) ],
       [ ('tree', dict(nodes_per_level=[10, 50], move_from_start_to_end=1)) ]),
    ('tree/[5,100]/[moveFromStartToEnd(1)]',
        [ ('tree', dict(nodes_per_level=[5, 100], move_from_start_to_end=0)) ],
        [ ('tree', dict(nodes_per_level=[5, 100], move_from_start_to_end=1)) ]),

    ('tree/[10,10,10,10]/no_change/prerun',
        [ ('tree', dict(move_from_start_to_end=0, nodes_per_level=[10, 10, 10, 10])) ],
        [] ),
    ('tree/[10,10,10,10]/no_change',
        [ ('tree', dict(move_from_start_to_end=0, nodes_per_level=[10, 10, 10, 10])) ],
        [] ),
    ('tree/[2,2,2,2,2,2,2,2,2,2]/no_change/prerun',
        [ ('tree', dict(nodes_per_level=[2, 2, 2, 2, 2, 2, 2, 2, 2, 2])) ],
        [] ),
    ('tree/[2,2,2,2,2,2,2,2,2,2]/no_change',
        [ ('tree', dict(nodes_per_level=[2, 2, 2, 2, 2, 2, 2, 2, 2, 2])) ],
        [] ),

    ('anim/100/32',
        [ ('tree', dict(nodes_per_level=[0], move_from_start_to_end=0)),
          ('anim', dict(count=100, advance_every_nth=None)) ],
        [ ('anim', dict(advance_every_nth=32)) ]),
    ('anim/100/16',
        [ ('anim', dict(advance_every_nth=None)) ],
        [ ('anim', dict(advance_every_nth=16)) ]),
    ('anim/100/8',
        [ ('anim', dict(advance_every_nth=None)) ],
       [ ('anim', dict(advance_every_nth=8)) ]),
    ('anim/100/4',
        [ ('anim', dict(advance_every_nth=None)) ],
        [ ('anim', dict(advance_every_nth=4)) ]),
    ('anim/finalize', [ ('anim', dict(count=0)), ('table', dict(rows=2, columns=2)) ], [])
]


def make_pandas_table(rows, cols):
    return pd.DataFrame(np.array(list(map(int, alphabet * (rows * cols // len(alphabet) + 1)))[:rows*cols]).reshape((rows, cols)))


class Table(Item):
    rows = 2
    columns = 2
    sort_column = None
    filter = None
    activate = None

    @property
    def html(scope):
        res = '<table class="table" style="width: 100%;"><tbody>'
        i = scope.rows * scope.columns
        if scope.activate is not None:
            for k in range(scope.rows):
                res += '<tr class="table-active">' if k % scope.activate == 0 else '<tr>'
                for m in range(scope.columns):
                    res += '<td>' + alphabet[(i + k * scope.columns + m + 1) % len(alphabet)] + '</td>'
                res += '</tr>'
        elif scope.filter is not None:
            for k in range(scope.rows):
                if k % scope.filter == 0:
                    continue
                res += '<tr>'
                for m in range(scope.columns):
                    res += '<td>' + alphabet[(i + k * scope.columns + m + 1) % len(alphabet)] + '</td>'
                res += '</tr>'
        elif scope.sort_column is not None and scope.rows * scope.columns > 0:
            table = []
            for _ in range(scope.rows):
                row = []
                for _ in range(scope.columns):
                    i += 1
                    row.append(alphabet[i % len(alphabet)])
                table.append(row)
            # pdb.set_trace()
            table = pd.DataFrame(table).sort_values(by=scope.sort_column)
            for k in range(scope.rows):
                res += '<tr>'
                for m in range(scope.columns):
                    res += '<td>' + table.iloc[k, m] + '</td>'
                res += '</tr>'
        else:
            for _ in range(scope.rows):
                res += '<tr>'
                for _ in range(scope.columns):
                    i += 1
                    res += '<td>' + alphabet[i % len(alphabet)] + '</td>'
                res += '</tr>'
        res += '</tbody></table>'
        return res


class Tree(Item):
    nodes_per_level = [0]
    reverse = False
    insert_first = 0
    insert_last = 0
    remove_first = 0
    remove_last = 0
    move_from_end_to_start = 0
    move_from_start_to_end = 0

    @property
    def html(scope):
        counter = 0
        def inner(counts, *, reverse=False, insert_first=0, insert_last=0,
            remove_first=0, remove_last=0,
            move_from_end_to_start=0, move_from_start_to_end=0):

            nonlocal counter
            res = ''
            if len(counts) == 0:
                res += alphabet[counter % len(alphabet)]
                counter += 1
            else:
                res += '<table class="Tree"><tbody>'
                content = []
                for _ in range(counts[0]):
                    content.append(inner(counts[1:]))
                if reverse:
                    content = list(reversed(content))
                for _ in range(insert_first):
                    content.insert(0, inner(counts[1:]))
                for _ in range(insert_last):
                    content.append(inner(counts[1:]))
                if remove_first > 0:
                    content = content[remove_first:]
                if remove_last > 0:
                    content = content[:-remove_last]
                if move_from_end_to_start > 0:
                    content = content[-move_from_end_to_start:] + content[:-move_from_end_to_start]
                if move_from_start_to_end > 0:
                    content = content[move_from_start_to_end:] + content[:move_from_start_to_end]
                res += ''.join([ '<tr><td>' + c + '</td></tr>' for c in content ])
                #res += ''.join(content)
                #res += '</td></tr>'
                res += '</tbody></table>'
            return res
        res = inner(scope.nodes_per_level,
            reverse=scope.reverse,
            insert_first=scope.insert_first,
            insert_last=scope.insert_last,
            remove_first=scope.remove_first,
            remove_last=scope.remove_last,
            move_from_end_to_start=scope.move_from_end_to_start,
            move_from_start_to_end=scope.move_from_start_to_end)
        return res


class Anim(Item):
    count = 100
    time = 0
    advance_every_nth = None
    
    @property
    def html(scope):
        t = scope.time
        n = scope.advance_every_nth
        res = '<div>'
        for i in range(scope.count):
            t_i = (t + 1) if n is not None and i % n == 0 else t
            res += f'<div style="float: left; margin: 4px; width: 40px; height: 40px; border-radius: {t_i % 10}px; background-color: rgba(0, 0, 0, {0.5+(t_i % 10)/10})"></div>'
        res += '</div>'
        return res


CSS = r'''
    .Tree td { padding: 10px; background-color: rgba(200, 200, 200, 1); }
    .Tree td .Tree td { background-color: rgba(190, 190, 190, 1); }
    .Tree td .Tree td .Tree td { background-color: rgba(180, 180, 180, 1); }
    .Tree td .Tree td .Tree td .Tree td { background-color: rgba(170, 170, 170, 1); }
    .Tree td .Tree td .Tree td .Tree td .Tree td { background-color: rgba(160, 160, 160, 1); }
    .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td { background-color: rgba(150, 150, 150, 1); }
    .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td { background-color: rgba(140, 140, 140, 1); }
    .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td { background-color: rgba(130, 130, 130, 1); }
    .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td { background-color: rgba(120, 120, 120, 1); }
    .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td { background-color: rgba(110, 110, 110, 1); }
    .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td .Tree td { background-color: rgba(100, 100, 100, 1); }
'''


class MyCSS(Item):
    @property
    def html(scope):
        res = f'<style type="text/css">{CSS}</style>'
        # print('res:', res)
        return res


class root(Item):
    counter = 0
    is_running = False
    timestamp = None
    results = defaultdict(lambda: [])
    iterations = 5
    iter_counter = 0

    class my_css(MyCSS):
        pass

    class _btn(Button):
        text = "Start benchmark"
        
        @property
        def disabled(scope):
            return scope.root.is_running

        def on_clicked(scope):
            scope.root.start()

    class result(TextOutput):
        text = "Result will appear here when the benchmark is finished"

    class results_table(PandasDataFrame):
        dataframe = pd.DataFrame()

    class table(Table):
        rows = 0
        columns = 0

    class tree(Tree):
        nodes_per_level = [0]

    class anim(Anim):
        count = 0
        time = 0
        advance_every_nth = None

    class pandasTable(PandasDataFrame):
        dataframe = pd.DataFrame()

    def start_iter(scope):
        scope.counter = -1
        scope.timestamp = time.time()
        scope.execute_step()

    def start(scope):
        scope.results = defaultdict(lambda: [])
        scope.iter_counter = 0
        scope.is_running = True
        scope.start_iter()

    def stop(scope):
        scope.is_running = False
        res = []
        for name, results in scope.results.items():
            res.append([ name, np.mean(results) * 1000, np.std(results) * 1000, ','.join(map(lambda r: '%.02f' % (r * 1000), results)), 'ms' ])
        res = pd.DataFrame(res, columns=['Test', 'Mean', 'Std', 'All', 'Units'])
        scope.result.text = 'Here are the results:'
        scope.results_table.dataframe = res

    def send_continue_msg(scope):
        get_engine(scope).execute_js(f'''window.requestAnimationFrame(function() {{ window.PYDECLARATIVE.customEvent({{ event: "custom_message", message_type: "uibench.continue", uuid: "{get_node(scope).uuid}" }}) }})''')
            
    def execute_step(scope):
        t = time.time()
        scope.counter += 1
        if scope.counter > 0 and scope.counter % 2 == 0:
            test_name = tests[scope.counter // 2 - 1][0]
            scope.results[test_name].append(t - scope.timestamp)
        logging.getLogger().warn(f'{scope.counter} {(t - scope.timestamp) * 1000 // 1}ms')
        if scope.counter % 2 == 1:
            time.sleep(0.25)
        scope.timestamp = time.time()
    
        if scope.counter // 2 < len(tests):
            feed = tests[scope.counter // 2][1 + scope.counter % 2]
            # logging.getLogger().warn(f'feed: {feed}')
            for el in feed:
                for k, v in el[1].items():
                    scope[el[0]][k] = v
            scope.send_continue_msg()
        else:
            if scope.iter_counter < scope.iterations - 1:
                scope.iter_counter += 1
                scope.start_iter()
            else:
                scope.stop()

        # if scope.counter < 16:
        #     feed = tests[scope.counter // 2][1 + scope.counter % 2]
        #     scope.table.rows, scope.table.columns = feed
        # elif scope.counter < 24:
        #     feed = tests[scope.counter - 8][1:]
        #     print(scope.counter, scope.counter - 8, feed)
        #     df = make_pandas_table(*feed[0])
        #     df = df.sort_values(by=feed[1])
        #     scope.pandasTable.dataframe = df
        # elif scope.iter_counter < scope.iterations - 1:
        #     scope.iter_counter += 1
        #     scope.iter_results.append(scope.elapsed)
        #     scope.start()
        # else:
        #     scope.stop()

        # if scope.is_running:
        #     scope.send_continue_msg()

    def handle_dom_event(scope, ev):
        if ev['event'] == 'custom_message' and ev['message_type'] == 'uibench.continue':
            scope.execute_step()