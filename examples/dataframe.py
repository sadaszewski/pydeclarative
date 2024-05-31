from pydeclarative import *
import pandas as pd
import numpy as np


class root(Item):
    class df(PandasDataFrame):
        dataframe = pd.DataFrame(np.random.random((100, 15)), columns='a b c d e f g h i j k l m n o'.split()).set_index('a')
        use_datatables_net = True

    class _btn(Button):
        text = "Regenerate"
        def on_clicked(scope):
            scope.df.dataframe = pd.DataFrame(np.random.random((100, 15)), columns='a b c d e f g h i j k l m n o'.split()).set_index('a')
