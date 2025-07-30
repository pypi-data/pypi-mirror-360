#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pkg_resources import get_distribution
from .wovodat import WOVOdat

__version__ = get_distribution("wovodat").version
__author__ = "Martanto"
__author_email__ = "martanto@live.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025, Martanto"
__url__ = "https://github.com/martanto/wovodat-python"

__all__ = [
    "__version__",
    "__author__",
    "__author_email__",
    "__license__",
    "__copyright__",
    "WOVOdat",
]
