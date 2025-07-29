"""
Setup.py for streamlit_kanban_board
This file exists for compatibility with setuptools-based installs.
The project primarily uses Poetry for dependency management and packaging.
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
def read_version():
    import os
    here = os.path.abspath(os.path.dirname(__file__))
    init_path = os.path.join(here, 'streamlit_kanban_board', '__init__.py')
    with open(init_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '1.0.0'

# Get the list of all files in the frontend/build directory
def get_build_files():
    build_dir = "streamlit_kanban_board/frontend/build"
    build_files = []
    
    if os.path.exists(build_dir):
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                # Get the relative path from the build directory
                rel_path = os.path.relpath(os.path.join(root, file), build_dir)
                build_files.append(f"frontend/build/{rel_path}")
    
    return build_files

setup() 