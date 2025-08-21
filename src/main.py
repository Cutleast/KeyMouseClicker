"""
Copyright (c) Cutleast
"""

import sys
from argparse import Namespace

from app import App
from resources_rc import qt_resource_data as qt_resource_data

if __name__ == "__main__":
    app = App(Namespace())

    sys.exit(app.exec())
