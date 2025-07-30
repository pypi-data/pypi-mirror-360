# GENOCIDE OTP-CR-117/19
# -*- coding: utf-8 -*-
#


"Bejaarden en Gehandicapten (Wzd), Criminelen (Wzd), Psychiatrische Patienten (WvGGZ)"


__name__ = "president"
__version__ = "131"


import doctest
import os
import sys
import unittest


sys.setrecursionlimit(1500)


curdir = os.getcwd()


sys.path.insert(0, os.path.join(curdir))
sys.path.insert(0, os.path.join(curdir, ".."))
sys.path.insert(0, os.path.join(curdir, "..", ".."))


# -- Options for GENERIC output ---------------------------------------------


project = __name__
master_doc = 'index'
version = '%s' % __version__
release = '%s' % __version__
language = 'utf-8'
today = ''
today_fmt = '%B %d, %Y'
needs_sphinx='1.7'
exclude_patterns = ['_build', '_templates', '_source', 'Thumbs.db', '.DS_Store']
source_suffix = '.rst'
source_encoding = 'utf-8-sig'
modindex_common_prefix = [""]
keep_warnings = True
templates_path=['_templates']
add_function_parentheses = False
add_module_names = False
show_authors = False
pygments_style = 'colorful'
extensions=[
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.githubpages'
]


# -- Options for HTML output -------------------------------------------------


html_title = "Bejaarden en Gehandicapten (Wzd), Criminelen (Wfz), Psychiatrische Patienten (WvGGZ)"
html_style = 'president.css'
html_static_path = ["_static"]
html_css_files = ["president.css",]
html_short_title = "PRESIDENT %s" % __version__
html_sidebars = {
    '**': [
        'about.html',
        'searchbox.html',
        'navigation.html',
        'relations.html',
    ]
}
html_theme = "alabaster"
html_theme_options = {
    'github_user': 'bthate',
    'github_repo': __name__,
    'github_button': False,
    'github_banner': False,
    'logo': 'aes.ico',
    'link': '#000',
    'link_hover': '#000',
    'nosidebar': True,
    'show_powered_by': False,
    'show_relbar_top': False,
    'sidebar_width': 0,
}
html_favicon = "aes.ico"
html_extra_path = ["robots.txt"]
html_last_updated_fmt = '%Y-%b-%d'
html_additional_pages = {}
html_domain_indices = False
html_use_index = False
html_split_index = False
html_show_sourcelink = False
html_show_sphinx = False
html_show_copyright = False
html_copy_source = False
html_use_opensearch = 'http://%s.rtfd.io/' % __name__
html_file_suffix = '.html'
htmlhelp_basename = 'testdoc'

intersphinx_mapping = {
                       'python': ('https://docs.python.org/3', 'objects.inv'),
                       'sphinx': ('http://sphinx.pocoo.org/', None),
                      }
intersphinx_cache_limit=1


rst_prolog = '''.. image:: bewijsgif4.jpg
    :width: 100%
    :height: 2.6cm
    :target: index.html


.. raw:: html

    <br>

'''


rst_epilog = '''.. raw:: html

     <br>
     <center>
     <b>

:ref:`reconsider <reconsider>` - :ref:`evidence <evidence>` - :ref:`guilty <guilty>` - :ref:`writings <writings>`

.. raw:: html

    </b>
    </center>
'''


autosummary_generate=True
autodoc_default_flags=['members', 'undoc-members', 'private-members', "imported-members"]
autodoc_member_order='groupwise'
autodoc_docstring_signature=True
autoclass_content="class"
doctest_global_setup=""
doctest_global_cleanup=""
doctest_test_doctest_blocks="default"
trim_doctest_flags=True
doctest_flags=doctest.REPORT_UDIFF
nitpick_ignore=[
                ('py:class', 'builtins.BaseException'),
               ]
