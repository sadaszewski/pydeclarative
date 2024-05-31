from pydeclarative import *
from pydeclarative.transfer import *


class root(Item):
    class _dl(FileDownload):
        content = bytes([ i for i in range(256) ])
        size = 256
        mime_type = "application/octet-stream"

        def get_content(scope, start, count):
            return scope.content[start:(start + count)]
        
        def on_completed(scope):
            print('Download completed')
