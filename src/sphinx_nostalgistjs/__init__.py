from docutils import nodes
from docutils.parsers.rst import directives

from sphinx.application import Sphinx
from sphinx.locale import _
from sphinx.util.docutils import SphinxDirective

import json
import logging
import random

# Thanks to sphinxnotes-isso for a working example on how to do something similar to this

__title__= 'sphinx-nostalgistjs'
__license__ = 'GPLv3',
__version__ = '1.0'
__author__ = 'Lucas Pires Camargo'
__url__ = 'https://camargo.eng.br'
__description__ = 'Sphinx extension for embedding NostalgistJS emulation in HTML documents'
__keywords__ = 'documentation, sphinx, extension, nostalgistjs, emulation, games'

CONFIG_ITEMS = ['nostalgistjs_script_url']

logger = logging.getLogger(__name__)

def js_bool( val ):
    return "true" if bool(val) else "false"

class NostalgistJSNode(nodes.General, nodes.Element):

    @staticmethod
    def visit(self, node):
        id = node['unique_id']
        canvas_style = "aspect-ratio: 4 / 3; width: 100%; background: black; radius: 10px"
        txt_btn_start = "Start"

        options_extender = ""
        if 'extra_nostalgist_options' in node:
            options_extender = f"""
                let extra_opts = {{
                    {node['extra_nostalgist_options']}
                }};
                Object.assign(opts, extra_opts);
            """

        attribution = """
            <p><em>
                Powered by <a class="reference external" href="https://github.com/lucaspcamargo/sphinx-nostalgistjs">sphinx_nostalgistjs</a> and 
                <a class="reference external" href="https://nostalgist.js.org/">Nostalgist.js</a>.
            </em></p>
            """ if not node.get('omit_attribution', False) else ""

        self.body.append(f"""
                        <section id="sph_njs_container_{id}" class="text-center" style="display: none">
                            <div class="btn-group p-1" role="group" aria-label="Emulator controls">
                                <button id="sph_njs_btn_stop_{id}" type="button" class="btn btn-danger">
                                    <i class="fa fa-stop"></i> Stop
                                </button>
                                <button id="sph_njs_btn_reset_{id}" type="button" class="btn btn-warning">
                                    <i class="fa fa-arrow-rotate-left"></i> Reset
                                </button>
                                <button id="sph_njs_btn_fullscreen_{id}" type="button" class="btn btn-secondary">
                                    <i class="fa fa-expand"></i> Fullscreen
                                </button>
                            </div>
                            <div id="sph_njs_canvas_wrap_{id}" class="text-left position-relative">
                                <canvas class="sph_njs_canvas_{id}" style="{canvas_style}">
                                    <p>This browser does not seem to support the canvas element.</p>
                                </canvas>
                                <div id="sph_njs_overlay_{id}" class="position-absolute top-0 start-0 w-100 h-100 user-select-none pe-none" style="background: #00000080">
                                    <div class="position-absolute top-50 start-50 translate-middle">
                                        <div class="spinner-border text-light" role="status">
                                            <span class="visually-hidden">Loading...</span>
                                        </div>
                                    </div>
                                </div>
                                <style> 
                                    canvas.sph_njs_canvas_{id}:focus {{  
                                        box-shadow: 0px 0px 0px 3px var(--pst-color-primary, blue);
                                    }} 
                                    canvas.sph_njs_canvas_{id} {{  
                                        transition: box-shadow .3s ease-in;
                                    }} 
                                </style>
                            </div>
                            {attribution}
                        </section>

                        <button id="sph_njs_btn_start_{id}" type="button" class="btn btn-success">
                            <i class="fa fa-play"></i> {txt_btn_start}
                        </button>

                        <script>
                            function sph_njs_launch() {{
                                BLACKLISTED_KEY_CONTROL_ELEMENTS.add("CANVAS"); // suppress docutils.js arrow keys navigation
                                let opts = {json.dumps(node['base_opts'])};
                                {options_extender}
                                let functions = {{
                                    beforeLaunch: function (nostalgist) {{
                                        {node.get('before_launch_preamble', '')};
                                        document.querySelector("#sph_njs_container_{id}").nostalgist = nostalgist;
                                        {node.get('before_launch_epilogue', '')};
                                    }},
                                    onLaunch: function (nostalgist) {{
                                        {node.get('on_launch_preamble', '')};
                                        let overlay = document.querySelector("#sph_njs_overlay_{id}");
                                        overlay.style.visibility = "hidden";
                                        {node.get('on_launch_epilogue', '')};
                                    }},
                                }};
                                Object.assign(opts, functions);

                                document.querySelector("#sph_njs_container_{id}").style.display = "";
                                document.querySelector("#sph_njs_btn_start_{id}").style.display = "none";

                                Nostalgist.launch(opts).then(function (nostalgist) {{
                                    // save original canvas size for later restore (eg. left fullscreen)
                                    let canvas = document.querySelector(".sph_njs_canvas_{id}");
                                    canvas.originalWidth = canvas.width;
                                    canvas.originalHeight =  canvas.height;
                                    document.getElementById("sph_njs_container_{id}").scrollIntoView();
                                    canvas.focus();
                                    console.log("NostalgistJS launch complete, dimensions are "+canvas.width+"x"+canvas.height);
                                }});
                            }}

                            function sph_njs_stop() {{
                                document.querySelector("#sph_njs_container_{id}").nostalgist.exit({{ removeCanvas: false }});
                                document.querySelector("#sph_njs_container_{id}").style.display = "none";
                                document.querySelector("#sph_njs_btn_start_{id}").style.display = "";
                                document.querySelector("#sph_njs_overlay_{id}").style.visibility = "visible";
                                console.log("NostalgistJS exited.");
                            }}

                            function sph_njs_reset() {{
                                document.querySelector("#sph_njs_container_{id}").nostalgist.restart();
                                
                            }}

                            function sph_njs_fullscreen() {{
                                let elem = document.querySelector(".sph_njs_canvas_{id}");
                                if (!document.fullscreenElement) {{
                                    elem.requestFullscreen().then(() => {{
                                        console.log('Fullscreen mode started.');
                                    }}, (err) => {{
                                        console.log(`Error attempting to enable fullscreen mode: ${{err.message}} (${{err.name}})`);
                                    }});
                                }} else {{
                                    document.exitFullscreen();
                                }}
                            }}

                            document.querySelector("#sph_njs_btn_start_{id}").onclick = sph_njs_launch;
                            document.querySelector("#sph_njs_btn_stop_{id}").onclick = sph_njs_stop;
                            document.querySelector("#sph_njs_btn_reset_{id}").onclick = sph_njs_reset;
                            document.querySelector("#sph_njs_btn_fullscreen_{id}").onclick = sph_njs_fullscreen;
                            document.querySelector(".sph_njs_canvas_{id}").addEventListener("fullscreenchange", (event) => {{
                                if(!document.fullscreenElement)
                                {{
                                    // When leaving fullscreen, restore original canvas size
                                    let nostalgist = document.querySelector("#sph_njs_container_{id}").nostalgist;
                                    let canvas = document.querySelector(".sph_njs_canvas_{id}");
                                    nostalgist.resize({{ 
                                        width: canvas.originalWidth,
                                        height: canvas.originalHeight
                                    }});
                                    console.log("Left fullscreen, resized to "+canvas.originalWidth+"x"+canvas.originalHeight);
                                }}
                                else
                                    console.log("Entered fullscreen, resizing happens automatically.");
                            }});
                        </script>

                        """)
        

    @staticmethod
    def depart(self, _):
        pass


class NostalgistJSDirective(SphinxDirective):
    
    option_spec = {
        'rom_url': str,
        'core_id': str 
    }

    has_content = True

    def run(self):
        content = '\n'.join(self.content or [])
        content = content.strip()
        print("CONTENT IS "+repr(content))
        conf = json.loads(content) if content else {}

        unique_id = ''.join(random.choice('0123456789ABCDEF') for _ in range(8))
        opts = {
            'rom': self.options.get("rom_url"),
            'core': self.options.get("core_id"),
            'element': '.sph_njs_canvas_'+unique_id,  # we use class because the js lib changes the element's id for some cursed reason
            'respondToGlobalEvents': False,
        }
        opts.update(conf.get('nostalgist_options', {}))

        node = NostalgistJSNode()
        node['unique_id'] = unique_id
        node['base_opts'] = opts
        node['omit_attribution'] = conf.get('omit_attribution', False)
        node['extra_nostalgist_options'] = conf.get('extra_nostalgist_options', '')
        node['before_launch_preamble'] = conf.get('before_launch_preamble', '')
        node['before_launch_epilogue'] = conf.get('before_launch_epilogue', '')
        node['on_launch_preamble'] = conf.get('on_launch_preamble', '')
        node['on_launch_epilogue'] = conf.get('on_launch_epilogue', '')

        return [node]


def on_html_page_context(app:Sphinx, pagename:str, templatename:str, context,
                         doctree:nodes.document) -> None:
    """Called when the HTML builder has created a context dictionary to render a template with.

    We may add the necessary JS if NostalgistJS is used in the page.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param str pagename: Name of the page being rendered (without .html or any file extension).
    :param str templatename: Page name with .html.
    :param dict context: Jinja2 HTML context.
    :param docutils.nodes.document doctree: Tree of docutils nodes.
    """
    # Only embed comments for documents
    if not doctree:
        return
    # We supports embed mulitple comments box in same document
    for node in doctree.traverse(NostalgistJSNode):
        kwargs = {
        }
        # TODO setup kwargs according to config IF script needs it
        js_url = app.config.nostalgistjs_script_url
        app.add_js_file(js_url, **kwargs)
        logger.warning("Using NostalgistJS from "+js_url)

def setup(app):
    for cfg in CONFIG_ITEMS:
        app.add_config_value(cfg, None, {})
    app.add_node(NostalgistJSNode, html=(NostalgistJSNode.visit, NostalgistJSNode.depart))
    app.add_directive('nostalgistjs', NostalgistJSDirective)
    app.connect('html-page-context', on_html_page_context)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }