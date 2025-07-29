# aggregate documentation build configuration file, created by
# sphinx-quickstart on Sat Sep  1 14:08:11 2018.
#
# This file is executed with the current directory set to its
# containing dir.
#

import matplotlib.pyplot as plt
import sys
import os

# allow RTD to find aggregate
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../'))
import aggregate as agg

# color graphs
agg.knobble_fonts(True)

# graphics defaults - better res graphics
plt.rcParams['figure.dpi'] = 300

# -- Project information -----------------------------------------------------
project = agg.__project__
copyright = agg.__copyright__
author = agg.__author__

# generally want True, so warning to be an error
# helpful in debugging to set equal to False
ipython_warning_is_error = True

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
release = agg.__version__
version = release[: len(release) -
                  len(release.lstrip("0123456789."))].rstrip(".")

# -- General configuration ------------------------------------------------
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosectionlabel',
    'sphinx_copybutton',
    'sphinx_toggleprompt',
    'IPython.sphinxext.ipython_directive',
    'IPython.sphinxext.ipython_console_highlighting',
    'nbsphinx',
    'sphinx_panels',
    'sphinxcontrib.bibtex',
    'sphinx_multitoc_numbering',
    'sphinx_rtd_dark_mode'
]


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

exclude_patterns = ['_build', '**.ipynb_checkpoints', 'Thumbs.db', '.DS_Store']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path

# The master toctree document.
master_doc = 'index'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# GPT suggestions for the reference problem
autonumbering_enabled = True

# warnings_filters = {
#     'suppress': [
#         'ref.ref_has_no_links',
#         'ref.term_not_defined',
#         'autosectionlabel.label_from_unnamed_label',
#     ]
# }


# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# https://sphinx-toggleprompt.readthedocs.io/en/stable/#offset
toggleprompt_offset_right = 35

# bibtex options
bibtex_bibfiles = ['extract.bib', 'books.bib']
bibtex_reference_style = 'author_year'

# user starts in light mode
default_dark_mode = False

# https://www.spinics.net/lists/linux-doc/msg77015.html
# autosectionlabel_prefix_document = True
# autosectionlabel_maxdepth = 1


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'both',
    'style_external_links': False,
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 3,
    'includehidden': True,
    'titles_only': False,
}

html_logo = '_static/agg_logo.png'
html_favicon = '_static/agg_favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'aggregatedoc'


# -- Options for LaTeX output ---------------------------------------------
# better unicode support
latex_engine = "xelatex"

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'a4paper',
    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '10pt',
    'extrapackages': '\\usepackage{mathrsfs}',
    # 'preamble': '\\renewenvironment{DUlineblock}{}{}',
    # 'preamble': '\\renewenvironment{DUlineblock}{\\begin{comment}}{\\end{comment}}'
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'aggregate.tex', 'aggregate Documentation',
     'Stephen J. Mildenhall', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'aggregate', 'aggregate Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'aggregate', 'aggregate Documentation',
     author, 'aggregate', 'Working with aggregate (compound) probability '
     'distributions.',
     'Miscellaneous'),
]
