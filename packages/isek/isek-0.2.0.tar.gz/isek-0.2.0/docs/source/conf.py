# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

# 假设 conf.py 在 docs/source/，那么你的项目根目录 (包含 isek/ 的目录) 是 ../../
sys.path.insert(0, os.path.abspath("../../"))

project = "ISEK"
copyright = "2025, ISEK Team"
author = "Moshi"
release = "0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # 核心：从 docstrings 生成文档
    "sphinx.ext.napoleon",  # 支持 Google/NumPy 风格 docstrings (如果使用)
    "sphinx.ext.intersphinx",  # 链接到其他库的文档 (如 Python)
    "sphinx.ext.viewcode",  # 添加源码链接
    "sphinx.ext.githubpages",  # 支持 GitHub Pages 发布
    # 'sphinx_rtd_theme',     # 如果使用 ReadTheDocs 主题
]

templates_path = ["_templates"]
exclude_patterns = []

language = "English"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_static_path = ["_static"]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# import sphinx_rtd_theme # 如果使用
# html_theme = 'sphinx_rtd_theme' # 或者 'alabaster', 'pydata_sphinx_theme' 等
html_permalinks_icon = "<span>#</span>"
html_theme = "sphinxawesome_theme"
# html_theme_path = [sphinx_rtd_theme.get_html_theme_path()] # 如果需要指定路径
