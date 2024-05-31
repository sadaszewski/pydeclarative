from pydeclarative.htmldiff import htmldiff
import bs4
import json


alphabet = '72341523574132464597403259245'


class Tree:
    nodes_per_level = [0]
    reverse = False
    insert_first = 0
    insert_last = 0

    def html(scope):
        counter = 0
        def inner(counts, *, reverse=False, insert_first=0, insert_last=0):
            nonlocal counter
            res = ''
            if len(counts) == 0:
                res += alphabet[counter % len(alphabet)]
                counter += 1
            else:
                res += '<table>'
                content = []
                for _ in range(counts[0]):
                    content.append(inner(counts[1:]))
                if reverse:
                    content = list(reversed(content))
                for _ in range(insert_first):
                    content.insert(0, inner(counts[1:]))
                for _ in range(insert_last):
                    content.append(inner(counts[1:]))
                res += ''.join([ '<tr><td>' + c + '</td></tr>' for c in content ])
                #res += ''.join(content)
                #res += '</td></tr>'
                res += '</table>'
            return res
        res = inner(scope.nodes_per_level,
            reverse=scope.reverse,
            insert_first=scope.insert_first,
            insert_last=scope.insert_last)
        return res
    

def dbg_htmldiff(elem_new, elem_old):
    elem_new = bs4.BeautifulSoup(elem_new, 'xml').find()
    print(f'elem_new: {elem_new}')
    elem_old = bs4.BeautifulSoup(elem_old, 'xml').find()
    print(f'elem_old: {elem_old}')
    return json.dumps(    
        htmldiff(elem_new, elem_old), indent=1)


def test_00_reshape():
    scope = lambda: 0
    scope.nodes_per_level = [ 3 ]
    scope.reverse = False

    html_1 = Tree.html(scope)
    scope.nodes_per_level = [ 3, 1 ]
    html_2 = Tree.html(scope)
    scope.nodes_per_level = [ 1, 3 ]
    html_3 = Tree.html(scope)

    print(f'html_1:\n{html_1}\n')
    print(f'html_2:\n{html_2}\n')
    print(f'html_3:\n{html_3}\n')

    print(f'html_1 --> html_2: {dbg_htmldiff(html_2, html_1)}\n')
    print(f'html_2 --> html_3: {dbg_htmldiff(html_3, html_2)}\n')
    print(f'html_3 --> html_1: {dbg_htmldiff(html_1, html_3)}\n')