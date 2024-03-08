from docutils import nodes
from docutils.parsers.rst import directives

from sphinx.application import Sphinx
from sphinx.locale import _
from sphinx.util.docutils import SphinxDirective

import json
import logging

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
        options_extender = ""
        if 'extra_nostalgist_options' in node:
            options_extender = f"""
                let extra_opts = {{
                    {node['extra_nostalgist_options']}
                }};
                Object.assign(opts, extra_opts);
            """

        self.body.append(f"""
                         <canvas id="nostalgistjs_canvas" style="aspect-ratio: 4 / 3; width: 100%; background: black; radius: 10px;">
                            <p>This browser does not seem to support the canvas element.</p>
                         </canvas> 
                         <script>
                            BLACKLISTED_KEY_CONTROL_ELEMENTS.add("CANVAS"); // suppress docutils.js arrow keys navigation
                            let opts = {json.dumps(node['base_opts'])};
                            {options_extender}
                            let functions = {{
                                beforeLaunch: function (nostalgist) {{
                                    {node.get('before_launch_preamble', '')}
                                    // TODO begin loading spinner 
                                    {node.get('before_launch_epilogue', '')}
                                }},
                                onLaunch: function (nostalgist) {{
                                    {node.get('on_launch_preamble', '')}
                                    // TODO end loading spinner 
                                    {node.get('on_launch_epilogue', '')}
                                }},
                            }};
                            Object.assign(opts, functions);
                            Nostalgist.launch(opts).then(function () {{
                                console.log("NostalgistJS launch complete.");
                            }});
                         </script>
                         """)
        
        # TODO use button to show canvas and launch

        # TODO add bootstrap controls

        if not node.get('omit_attribution', False):
            self.body.append("""
                <p><em>
                    Powered by <a class="reference external" href="https://github.com/lucaspcamargo/sphinx-nostalgistjs">sphinx_nostalgistjs</a> and 
                    <a class="reference external" href="https://nostalgist.js.org/">Nostalgist.js</a>.
                </em></p>
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
        conf = json.loads(content) if content else {}

        # TODO add random id to node, use in canvas id and in 'element' below

        opts = {
            'rom': self.options.get("rom_url"),
            'core': self.options.get("core_id"),
            'element': '#nostalgistjs_canvas',
            'respondToGlobalEvents': False,
        }
        opts.update(conf.get('nostalgist_options', {}))

        node = NostalgistJSNode()
        node['base_opts'] = opts;
        node['extra_nostalgist_options'] = conf.get('extra_nostalgist_options', '');
        node['before_launch_preamble'] = conf.get('before_launch_preamble', '');
        node['on_launch_preamble'] = conf.get('on_launch_preamble', '');
        node['before_launch_epilogue'] = conf.get('before_launch_epilogue', '');
        node['on_launch_epilogue'] = conf.get('on_launch_epilogue', '');

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