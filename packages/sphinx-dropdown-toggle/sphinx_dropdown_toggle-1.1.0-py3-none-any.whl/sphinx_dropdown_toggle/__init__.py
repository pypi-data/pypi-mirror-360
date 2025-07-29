import os

from sphinx.application import Sphinx

try:
    from sphinx_dropdown_toggle._version import version as __version__
except ImportError:
    __version__ = "1.0.0"

def copy_javascript(app: Sphinx, exc):
    # Copy the JavaScript file to the output directory
    js_file = os.path.join(os.path.dirname(__file__), 'static', 'dropdown_toggle.js')
    
    with open(js_file,'r') as js:
        js_content = js.read()
    if app.builder.format == 'html' and not exc:
        staticdir = os.path.join(app.builder.outdir, '_static')
        outfile = os.path.join(staticdir,'dropdown_toggle.js')
        with open(outfile,'w') as js:
            js.write(js_content)

def setup(app: Sphinx):
    app.add_js_file('dropdown_toggle.js')
    app.connect('build-finished', copy_javascript)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
