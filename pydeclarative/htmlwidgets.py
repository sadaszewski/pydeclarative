class Item:
    pass

class Div(Item):
    def to_html(scope):
        return '<div data-content-item="data-content-item"></div>'

class TextInput(Item):
    def to_html(scope):
        return '<input type="text" />'

class Paragraph(Item):
    def to_html(scope):
        return '<p data-content-item="data-content-item"></p>'
