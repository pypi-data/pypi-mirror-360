# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from importlib.metadata import version as get_version

project: str = "canesm-processor"
copyright: str = "2024, Landon Rieger"
author: str = "Landon Rieger"
release: str = get_version("canesm-process")
version: str = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinxcontrib.mermaid",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_design",
    "sphinx_tabs.tabs",
    "sphinx_click",
]

templates_path = ["_templates"]
exclude_patterns = []

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_param = False
napoleon_use_rtype = False
napoleon_preprocess_types = True

mermaid_version = "11.1.1"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]


html_theme_options = {
    "repository_url": "https://gitlab.com/LandonRieger/canesm-processor",
    "repository_branch": "main",
    "path_to_docs": "docs/sphinx/source",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
    "repository_provider": "gitlab",
    "logo": {
        "text": f"canesm-processor {version}",
    },
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "scipy": ("https://docs.scipy.org/doc/scipy", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "dask": ("https://docs.dask.org/en/latest", None),
    "sparse": ("https://sparse.pydata.org/en/latest/", None),
    "xarray-tutorial": ("https://tutorial.xarray.dev/", None),
    "xarray": ("https://docs.xarray.dev/en/stable/", None),
}
