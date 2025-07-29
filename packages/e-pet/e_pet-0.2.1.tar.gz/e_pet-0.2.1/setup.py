#!/usr/bin/env python3
"""
Setup script for e-pet virtual pet companion application.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "E-Pet - Virtual Pet Companion CLI Application"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="e-pet",
    version="0.2.1",
    description="A virtual pet companion CLI application",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Andrei Thüler",
    author_email="info@andreithuler.com",
    url="https://github.com/athuler/e-pet",
    packages=find_packages() + [''],
    py_modules=[
        'pet',
        'save_manager',
        'ui_manager',
        'dialog_engine',
        'settings_manager',
        'game_engine',
        'input_handler'
    ],
    install_requires=read_requirements() + [
        'importlib_resources>=5.0.0;python_version<"3.9"'
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'e-pet=game_engine:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.json', '*.txt', '*.md'],
    },
    data_files=[
        ('', ['dialog_tree.json', 'settings.json', 'pet_names.txt'])
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment :: Simulation",
        "Environment :: Console",
    ],
    keywords="virtual pet, cli, game, simulation, terminal, simulation",
    project_urls={
        "Bug Reports": "https://github.com/athuler/e-pet/issues",
        "Donate": "https://ko-fi.com/andreithuler",
        "Source": "https://github.com/athuler/e-pet",
    },
)