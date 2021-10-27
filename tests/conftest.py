import os
import sys

import pytest

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
if TESTS_DIR not in sys.path:
    sys.path.append(TESTS_DIR)

from thelpers import simple_icons_slugs as _simple_icons_slugs

@pytest.fixture(scope="session", autouse=True)
def _register_addons(request, install_addons_from_dir, disable_addons):
    addons_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    addon_module_names = install_addons_from_dir(addons_dir, addon_module_names=["simple_icons_blender"])
    yield
    sys.stdout.write("\n")
    disable_addons(addon_module_names)


@pytest.fixture
def simple_icons_slugs():
    return _simple_icons_slugs()
