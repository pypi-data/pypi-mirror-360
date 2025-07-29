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

setup(
    name="streamlit-kanban-board-goviceversa",
    version="1.0.2",
    description="A powerful, interactive Kanban board component for Streamlit applications with drag-and-drop functionality, role-based permissions, and customizable workflows.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Pierluigi Segatto",
    author_email="pier@goviceversa.com",
    url="https://github.com/goviceversa-com/streamlit_kanban_board",
    packages=find_packages(),
    package_data={
        "streamlit_kanban_board": get_build_files(),
    },
    include_package_data=True,
    install_requires=[
        "streamlit>=1.0.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Groupware", 
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
    ],
) 