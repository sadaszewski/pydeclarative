from pydeclarative import *


class root(Item):
    class xInput(TextInput):
        placeholder = "Type X values"
        text = "0 1 2 3 4"

    class yInput(TextInput):
        placeholder = "Type Y values"
        text = "0 1 0.5 2.5 0.75"

    class _plot(PlotlyPlot):
        @property
        def data(scope):
            return [
                dict(x=list(map(float, scope.xInput.text.split())),
                   y=list(map(float, scope.yInput.text.split())),
                   mode='lines')
            ]
        layout = dict(title='Plotly example')
