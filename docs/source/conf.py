# Configuration file for the Sphinx documentation builder
import os
import sys

# Configuration générale
project = 'Projet Météo BTS'
copyright = '2023, Équipe'
author = 'Équipe'

# Extensions
extensions = [
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

# Thème
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False,
    'display_version': True,
}
