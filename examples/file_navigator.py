from pydeclarative import *
import os
from pathlib import Path


class root(Item):
    current_dir = Path(os.path.abspath(os.sep))

    listingModel = ListModel()

    class listingView(Repeater):
        @property
        def model(scope):
            return scope.root.listingModel
        @delegate
        class delegate(Div):
            css_class = ['card', 'm-1', 'float-start', 'p-1']
            css_style = dict(width='18rem')
            index = None
            model_data = None
            class _name(Link):
                @property
                def text(scope):
                    return scope.parent.model_data
                @property
                def href(scope):
                    return '#' if scope.root.current_dir.joinpath(scope.parent.model_data).is_dir() else ''
                def on_clicked(scope):
                    scope.root.current_dir = scope.root.current_dir.joinpath(scope.parent.model_data).resolve()
                    scope.root.update_listing_model()
            
    def update_listing_model(scope):
        scope.listingModel.clear()
        scope.listingModel.append('..')
        for name in sorted(os.listdir(scope.current_dir)):
            scope.listingModel.append(name)
            
    def on_loaded(scope):
        scope.update_listing_model()
