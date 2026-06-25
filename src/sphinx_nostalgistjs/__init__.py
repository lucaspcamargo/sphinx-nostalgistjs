from docutils import nodes
from docutils.parsers.rst import directives

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

import json
import logging
import random

__title__= 'sphinx-nostalgistjs'
__license__ = 'GPLv3',
__version__ = '1.0'
__author__ = 'Lucas Pires Camargo'
__url__ = 'https://camargo.eng.br'
__description__ = 'Sphinx extension for embedding NostalgistJS emulation in HTML documents'
__keywords__ = 'documentation, sphinx, extension, nostalgistjs, emulation, games'

CONFIG_ITEMS = ['nostalgistjs_script_url']

logger = logging.getLogger(__name__)


class NostalgistJSNode(nodes.General, nodes.Element):

    @staticmethod
    def visit(self, node):
        uid           = node['unique_id']
        aspect_ratio  = node.get('aspect_ratio', '4/3')
        caption       = node.get('caption', '')
        omit_attr     = node.get('omit_attribution', False)

        options_extender = ""
        if node.get('extra_nostalgist_options'):
            options_extender = f"""
    var extra = {{ {node['extra_nostalgist_options']} }};
    Object.assign(opts, extra);"""

        if caption:
            caption_html = (
                f'<div class="px-3 py-1 border-top text-body-secondary small">'
                f'{caption}</div>'
            )
        elif not omit_attr:
            caption_html = (
                f'<div class="px-3 py-1 border-top text-body-secondary small">'
                f'Powered by <a href="https://github.com/lucaspcamargo/sphinx-nostalgistjs">'
                f'sphinx-nostalgistjs</a> and '
                f'<a href="https://nostalgist.js.org/">Nostalgist.js</a>.</div>'
            )
        else:
            caption_html = ''

        self.body.append(f"""\
<div class="border my-4" id="nostalgist-wrap-{uid}">
  <div class="d-flex align-items-center gap-2 p-2 bg-body-tertiary border-bottom">
    <button class="btn btn-sm btn-outline-secondary" id="nostalgist-toggle-{uid}">&#x25B6; Start</button>
    <button class="btn btn-sm btn-outline-secondary" id="nostalgist-reset-{uid}" disabled>&#x21BA; Reset</button>
    <span class="flex-grow-1"></span>
    <button class="btn btn-sm btn-outline-secondary" id="nostalgist-fs-{uid}" disabled aria-label="Fullscreen">&#x26F6; Fullscreen</button>
  </div>
  <div class="position-relative w-100" id="nostalgist-viewport-{uid}"
       style="aspect-ratio:{aspect_ratio};display:none;background:#000">
    <canvas class="sph_njs_canvas_{uid}" style="width:100%;height:100%;display:block">
      <p>This browser does not support the canvas element.</p>
    </canvas>
    <div id="nostalgist-overlay-{uid}"
         class="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
         style="background:rgba(0,0,0,.5);pointer-events:none;visibility:hidden">
      <div class="spinner-border text-light" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
  {caption_html}
</div>
<script>
(function () {{
  var viewport  = document.getElementById('nostalgist-viewport-{uid}');
  var btnToggle = document.getElementById('nostalgist-toggle-{uid}');
  var btnReset  = document.getElementById('nostalgist-reset-{uid}');
  var btnFs     = document.getElementById('nostalgist-fs-{uid}');
  var overlay   = document.getElementById('nostalgist-overlay-{uid}');
  var canvas    = document.querySelector('.sph_njs_canvas_{uid}');
  var nostalgist = null;
  var running   = false;

  function onStart() {{
    running = true;
    if (typeof BLACKLISTED_KEY_CONTROL_ELEMENTS !== 'undefined')
      BLACKLISTED_KEY_CONTROL_ELEMENTS.add('CANVAS');
    viewport.style.display = 'block';
    btnToggle.innerHTML = '&#x23F9; Stop';
    btnReset.disabled = false;
    btnFs.disabled = false;
    overlay.style.visibility = 'visible';

    var opts = {json.dumps(node['base_opts'])};
    opts.element = canvas;
    {options_extender}
    {node.get('before_launch_preamble', '')}
    opts.beforeLaunch = function (n) {{
      nostalgist = n;
      {node.get('before_launch_epilogue', '')}
    }};

    Nostalgist.launch(opts).then(function () {{
      {node.get('on_launch_preamble', '')}
      overlay.style.visibility = 'hidden';
      canvas.originalWidth  = canvas.width;
      canvas.originalHeight = canvas.height;
      canvas.focus();
      viewport.scrollIntoView();
      {node.get('on_launch_epilogue', '')}
    }});
  }}

  function onStop() {{
    if (!running || !nostalgist) return;
    nostalgist.exit({{ removeCanvas: false }});
    nostalgist = null;
    running = false;
    viewport.style.display = 'none';
    overlay.style.visibility = 'visible';
    btnToggle.innerHTML = '&#x25B6; Start';
    btnReset.disabled = true;
    btnFs.disabled = true;
  }}

  btnToggle.addEventListener('click', function () {{
    if (!running) {{ onStart(); }} else {{ onStop(); }}
  }});

  btnReset.addEventListener('click', function () {{
    if (nostalgist) nostalgist.restart();
  }});

  btnFs.addEventListener('click', function () {{
    if (!canvas) return;
    if (document.fullscreenElement) {{
      document.exitFullscreen();
    }} else {{
      if (canvas.requestFullscreen)            canvas.requestFullscreen();
      else if (canvas.webkitRequestFullscreen) canvas.webkitRequestFullscreen();
    }}
  }});

  document.addEventListener('fullscreenchange', function () {{
    if (!document.fullscreenElement && nostalgist && canvas.originalWidth) {{
      nostalgist.resize({{ width: canvas.originalWidth, height: canvas.originalHeight }});
    }}
  }});
}})();
</script>
""")

    @staticmethod
    def depart(self, _):
        pass


class NostalgistJSDirective(SphinxDirective):

    option_spec = {
        'rom_url':      str,
        'core_id':      str,
        'aspect-ratio': directives.unchanged,
        'caption':      directives.unchanged,
        'omit-attribution': directives.flag,
    }

    has_content = True

    def run(self):
        content = '\n'.join(self.content or [])
        content = content.strip()
        conf = json.loads(content) if content else {}

        unique_id = ''.join(random.choice('0123456789ABCDEF') for _ in range(8))
        opts = {
            'rom':  self.options.get("rom_url"),
            'core': self.options.get("core_id"),
            'respondToGlobalEvents': False,
        }
        opts.update(conf.get('nostalgist_options', {}))

        node = NostalgistJSNode()
        node['unique_id']               = unique_id
        node['base_opts']               = opts
        node['aspect_ratio']            = self.options.get('aspect-ratio', conf.get('aspect_ratio', '4/3'))
        node['caption']                 = self.options.get('caption', conf.get('caption', ''))
        node['omit_attribution']        = 'omit-attribution' in self.options or conf.get('omit_attribution', False)
        node['extra_nostalgist_options'] = conf.get('extra_nostalgist_options', '')
        node['before_launch_preamble']  = conf.get('before_launch_preamble', '')
        node['before_launch_epilogue']  = conf.get('before_launch_epilogue', '')
        node['on_launch_preamble']      = conf.get('on_launch_preamble', '')
        node['on_launch_epilogue']      = conf.get('on_launch_epilogue', '')

        return [node]


def on_html_page_context(app: Sphinx, pagename: str, templatename: str, context,
                         doctree: nodes.document) -> None:
    if not doctree:
        return
    for node in doctree.traverse(NostalgistJSNode):
        js_url = app.config.nostalgistjs_script_url
        app.add_js_file(js_url)
        logger.info("Using NostalgistJS from " + js_url)
        break  # only need to add the script once per page


def UnsupportedVisit(self, node):
    node.replace_self(nodes.Text(
        "The emulator is unsupported in this output format. "
        "Please visit the HTML version for full functionality."
    ))

def UnsupportedDepart(self, node):
    pass

def setup(app):
    for cfg in CONFIG_ITEMS:
        app.add_config_value(cfg, None, '')
    app.add_node(NostalgistJSNode,
                 html=(NostalgistJSNode.visit, NostalgistJSNode.depart),
                 text=(UnsupportedVisit, UnsupportedDepart),
                 latex=(UnsupportedVisit, UnsupportedDepart),
                 gemini=(UnsupportedVisit, UnsupportedDepart))
    app.add_directive('nostalgistjs', NostalgistJSDirective)
    app.connect('html-page-context', on_html_page_context)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
