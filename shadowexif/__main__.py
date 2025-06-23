#!/usr/bin/env python3
"""
Entry point for running ShadowEXIF as a module.

Usage:
    python -m shadowexif [options] files...
"""

import sys
from .cli import main

if __name__ == '__main__':
    sys.exit(main())