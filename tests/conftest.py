import os
import sys

import pytest

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from helpers import simple_icons_slugs as _simple_icons_slugs

@pytest.fixture
def simple_icons_slugs():
    return _simple_icons_slugs()
