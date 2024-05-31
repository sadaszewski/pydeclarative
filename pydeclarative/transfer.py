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


from pydeclarative import *
import base64
import bs4
from pydeclarative.htmlwidgets import elem_to_html


class FileUpload(Item):
    pass


class FileDownload(Item):
    text = 'Download'
    size = 4
    filename = 'test.txt'
    mime_type = 'text/plain'
    in_progress = False
    completed = Signal()

    def get_content(scope, start, count):
        return b'test'[start:(start + count)]

    def handle_dom_event(scope, event):
        if event['event'] == 'custom_message' and event['message_type'] == 'file_download.more':
            start, count = event['start'], event['count']
            content = scope.get_content(start, count)
            content = base64.b64encode(content).decode('latin-1')
            get_engine(scope).send_custom_message(get_node(scope), 'file_download.chunk', dict(start=start, count=count, content=content))
        elif event['event'] == 'custom_message' and event['message_type'] == 'file_download.completed':
            scope.in_progress = False
            scope.completed()

    def clicked_cb(scope):
        if scope.in_progress:
            return
        scope.in_progress = True
        get_engine(scope).send_custom_message(get_node(scope),
            'file_download.start', dict(size=scope.size, filename=scope.filename, mime_type=scope.mime_type))

    @property
    def html(scope):
        res = bs4.BeautifulSoup(f'''<div data-content-item="data-content-item">
                <script type="text/javascript">
                    window.PYDECLARATIVE.addCustomMessageHandler("#{get_node(scope).uuid}", "file_download.start", function(msg) {{
                        console.log("file_download.start received")
                        $("#{get_node(scope).uuid}").data("file_download.filename", msg.filename)
                        $("#{get_node(scope).uuid}").data("file_download.size", msg.size)
                        $("#{get_node(scope).uuid}").data("file_download.mime_type", msg.mime_type)
                        $("#{get_node(scope).uuid}").data("file_download.content", [])
                        var ev = {{
                            event: "custom_message",
                            message_type: "file_download.more",
                            uuid: "{get_node(scope).uuid}",
                            start: 0,
                            count: 64 * 1024
                        }}
                        window.PYDECLARATIVE.customEvent(ev)
                    }})
                    window.PYDECLARATIVE.addCustomMessageHandler("#{get_node(scope).uuid}", "file_download.chunk", function (msg) {{
                        console.log("file_download.chunk received")
                        var data = $("#{get_node(scope).uuid}").data("file_download.content") || []
                        data.push(Base64.toUint8Array(msg.content))
                        $("#{get_node(scope).uuid}").data("file_download.content", data)
                        if (msg.content.length === 0) {{
                            var ev = {{
                                event: "custom_message",
                                message_type: "file_download.completed",
                                uuid: "{get_node(scope).uuid}"
                            }}
                            window.PYDECLARATIVE.customEvent(ev)
                            if (data.map(function(a) {{ return a.length }}).reduce(function(a, b) {{ return a + b }}, 0) !== $("#{get_node(scope).uuid}").data("file_download.size")) {{
                                console.log("file size mismatch")
                                return
                            }} else {{
                                console.log("file size OK")
                            }}
                            var bb = new Blob(data, {{ type: $("#{get_node(scope).uuid}").data("file_download.mime_type") }})
                            var a = document.createElement('a')
                            a.download = $("#{get_node(scope).uuid}").data("file_download.filename")
                            a.href = window.URL.createObjectURL(bb)
                            a.click()
                        }} else {{
                            var ev = {{
                                event: "custom_message",
                                message_type: "file_download.more",
                                start: data.map(function(a) {{ return a.length }}).reduce(function(a, b) {{ return a + b }}, 0),
                                count: 64 * 1024,
                                uuid: "{get_node(scope).uuid}"
                            }}
                            window.PYDECLARATIVE.customEvent(ev)
                        }}
                    }})
                </script>
            </div>''', 'xml').find()
        return elem_to_html(scope, res)
    
    class _btn(Button):
        text = Binding(lambda scope: scope.FileDownload.text)

        @property
        def disabled(scope):
            return scope.FileDownload.in_progress

        def on_clicked(scope):
            scope.FileDownload.clicked_cb()
