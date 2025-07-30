# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
source_suffix = ['.rst', '.md']
master_doc = 'index'
project = 'LiveNodes'
year = '2022'
author = 'Yale Hartmann'
copyright = '{0}, {1}'.format(year, author)
version = release = '0.7.0'

pygments_style = 'trac'
templates_path = ['.']
extlinks = {
    'issue': ('https://gitlab.csl.uni-bremen.de/livenodes/livenodes/issues/%s', '#'),
    'pr': ('https://gitlab.csl.uni-bremen.de/livenodes/livenodes/pull/%s', 'PR #'),
}
# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only set the theme if we're building docs locally
    html_theme = 'sphinx_rtd_theme'

html_use_smartypants = True
html_last_updated_fmt = '%b %d, %Y'
html_split_index = False
html_sidebars = {
    '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False

linkcheck_ignore = [r'https://livenodes\.pages\.csl\.uni-bremen\.de/.*']