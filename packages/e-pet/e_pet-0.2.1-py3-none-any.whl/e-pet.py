#!/usr/bin/env python3
"""
E-Pet - Virtual Pet Companion CLI Application

A terminal-based virtual pet game where you can feed, play with, and talk to your pet.
Your pet has various attributes that change based on your interactions and naturally
decay over time.

Usage:
    python e-pet.py

Author: Claude Code
Version: 1.0.0
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_engine import main

if __name__ == "__main__":
    main()