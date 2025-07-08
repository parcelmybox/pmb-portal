"""
Backend package for ParcelMyBox.
"""

# This file makes the backend directory a Python package
import os
import sys

# Add the apps directory to the Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPS_DIR = os.path.join(BASE_DIR, 'apps')
if APPS_DIR not in sys.path:
    sys.path.insert(0, APPS_DIR)
