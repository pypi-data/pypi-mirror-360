import importlib.metadata
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ovrlpy"
copyright = f"""
{datetime.now():%Y}, Sebastian Tiesmeyer, Naveed Ishaque, Roland Eils,
Berlin Institute of Health @ Charité"""
author = "Sebastian Tiesmeyer"
version = importlib.metadata.version("ovrlpy")
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


extensions = [
    "sphinx_copybutton",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "autoapi.extension",
    "sphinx.ext.mathjax",
    "myst_nb",
]

nb_execution_mode = "off"


autodoc_typehints = "none"
autodoc_typehints_format = "short"

autoapi_dirs = ["../../ovrlpy"]
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]
autoapi_own_page_level = "function"

python_use_unqualified_type_names = True  # still experimental

autosummary_generate = True
autosummary_imported_members = True

nitpicky = True
nitpick_ignore = [
    ("py:class", "numpy.typing.DTypeLike"),
    ("py:class", "polars.DataFrame"),
    ("py:class", "polars.DataType"),
    ("py:class", "umap.UMAP"),
    ("py:class", "optional"),
]

intersphinx_mapping = dict(
    anndata=("https://anndata.readthedocs.io/en/stable/", None),
    matplotlib=("https://matplotlib.org/stable/", None),
    numpy=("https://numpy.org/doc/stable/", None),
    pandas=("https://pandas.pydata.org/pandas-docs/stable/", None),
    polars=("https://docs.pola.rs/api/python/stable/", None),
    python=("https://docs.python.org/3", None),
    scipy=("https://docs.scipy.org/doc/scipy/", None),
    sklearn=("https://scikit-learn.org/stable/", None),
    umap=("https://umap-learn.readthedocs.io/page/", None),
)

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_logo = "../resources/ovrlpy-logo.png"
html_theme_options = {"logo_only": True}


def skip_attributes(app, what, name, obj, skip, options):
    if what == "attribute":
        skip = True
    return skip


def setup(sphinx):
    sphinx.connect("autoapi-skip-member", skip_attributes)
