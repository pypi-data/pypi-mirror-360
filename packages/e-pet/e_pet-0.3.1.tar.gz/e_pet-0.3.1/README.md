# e-pet

[![PyPI - Version](https://img.shields.io/pypi/v/e-pet?label=Latest%20Version&link=https%3A%2F%2Fpypi.org%2Fproject%2FPassioGo%2F)](https://pypi.org/project/e-pet/) [![Pepy Total Downlods](https://img.shields.io/pepy/dt/e-pet)](https://www.pepy.tech/projects/e-pet)

A CLI Virtual Pet Companion

# Installation

```sh
pip install e-pet
```

Local installation:
```sh
pip install .
```

# Usage

When installed using pip:
```sh
e-pet
```

Local development:
```sh
python e-pet.py
```

# Interface

The CLI interface should be an ASCII art/animation of the pet, and below various actions that the user can select. The user should be able to select the option they would like to go for using arrow keys (the selected option is highlighted) and then pressing enter, or by selecting the corresponding option number on their keyboard.


# Game Mechanics

The pet has the following attributes:
- name (randomly generated; can be re-generated at any time by the user)
- age (starts at 0, increases as the user plays)
- sex (M, F, ??; randomly assigned, can be re-generated at any time by the user)
- Health (between 0 and 5)
- Happiness (between 0 and 5)
- Despair (between 0 and 5)
- Wealth (unbounded number, starts at 100)

The user can interact with the pet in the following main ways:
- Feeding
- Playing
- Talking

Each option has many different dialog trees. The dialog trees are stored as JSON files. Throughout the dialog trees, selecting various options may have effects on any of the pet's attributes (health, ahppiness, ...). There may be multiple possible outcome at any point of a tree, in which case randomness is used to determine which path to let the user continue on.


# Architecture

Game data is saved in a JSON file in the current directory. When starting, the app looks for a current save, if it doesn't find one it creates a new one. The game auto-saves after each action.

The app runs as a Python application without internet connection.