import json
import os
from typing import Dict, Optional, List
from uuid import uuid4

from IPython import get_ipython
from IPython.core.display import HTML, display_html

# location of this file is required to load resource urls
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


# read and inject required files as soon as this class is loaded
def __init():
    if get_ipython() is None:
        return

    with open(os.path.join(__location__, 'resources', 'vue-3.4.24.js')) as vue_file:
        vue = vue_file.read()

    display_html(HTML(f'''
        <script type="text/javascript">
            {vue}
        </script>
    '''))

    with open(os.path.join(__location__, 'resources', 'style.css')) as css_file:
        css = css_file.read()

    display_html(HTML(f'''
        <style type="text/css">
            {css}
        </style>
    '''))


__init()


# main class
class JupyterAnimation(HTML):
    def __init__(self,
                 html: str, frames: Dict[str, Dict],
                 style: Optional[List[str] | str] = None, js: List[str] | str = None,
                 fast_forward: bool = False):
        self._html: str = html
        self._frames: Dict[str, Dict] = frames
        self._fast_forward: bool = fast_forward

        if isinstance(style, list):
            self._style: str = '\n'.join(style)
        else:
            self._style: str = style or ''

        if isinstance(js, list):
            self._js: str = '\n'.join(js)
        else:
            self._js: str = js or ''

        self._id: str = str(uuid4()).replace('-', '')

        super().__init__(self._construct())

    def _construct(self) -> str:
        # read templates from file
        if len(self._frames) > 1:
            if self._fast_forward:
                filename = 'controls-ff.html'
            else:
                filename = 'controls.html'

            with open(os.path.join(__location__, 'resources', filename)) as html_file:
                html = html_file.read()
        else:
            html = ''

        with open(os.path.join(__location__, 'resources', 'script.js')) as js_file:
            js = js_file.read()

        # inject additional javascript
        js = js.replace('// <injected js>', self._js)

        # convert frame data to json
        frames = json.dumps([{
            '__key': key,
            **frame
        } for key, frame in self._frames.items()], indent=4)

        # return string containing the content
        return f'''
            <style type="text/css">
                {self._style}
            </style>
            
            <div id="container_{self._id}">
                {self._html}
                {html}
            </div>
            
            <script type="text/javascript">
                (function() {{
                    {js}
                    
                    app.frames = {frames}
                    app.mount('#container_{self._id}')
                }})()
            </script>
        '''
