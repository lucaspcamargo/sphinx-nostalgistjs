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
        self.body.append(f"""
                         <canvas id="nostalgistjs_canvas" style="aspect-ratio: 4 / 3; width: 100%; background: black; radius: 10px;">
                            <p>This browser does not seem to support the canvas element.</p>
                         </canvas> 
                         <script>
                            BLACKLISTED_KEY_CONTROL_ELEMENTS.add("CANVAS");
                            // TODO use bootstrap button to show canvas and launch
                            Nostalgist.launch({{ 
                                rom: '{node['rom_url']}', 
                                core: '{node['core_id']}',
                                element: '#nostalgistjs_canvas',
                                respondToGlobalEvents: false,
                                retroarchConfig: {json.dumps(node['rc_config'] or {})},
                                retroarchCoreConfig: {json.dumps(node['rcc_config'] or {})},
                                beforeLaunch: function (nostalgist) {{
                                    // TODO make this generic, optional
                                    window.efs = nostalgist.getEmscriptenFS();
                                    window.efs.mkdirTree('/home/web_user/retroarch/userdata/config/remaps/Genesis Plus GX');
                                    window.efs.writeFile('/home/web_user/retroarch/userdata/config/remaps/Genesis Plus GX/Dweep_Genesis_(latest).rmp', 
                                                         'input_libretro_device_p1 = "1"\\ninput_libretro_device_p2 = "2"');
                                }},
                                onLaunch: function (nostalgist) {{
                                    
                                }},
                            }}).then(function () {{console.log("NostalgistJS launch complete.")}});
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
        node = NostalgistJSNode()
        node['rom_url'] = self.options.get("rom_url")
        node['core_id'] = self.options.get("core_id")

        content = '\n'.join(self.content or [])
        conf = json.loads(content) if content else {}
        node['rc_config'] = conf.get('retroarchConfig', {})
        node['rcc_config'] = conf.get('retroarchCoreConfig', {})

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