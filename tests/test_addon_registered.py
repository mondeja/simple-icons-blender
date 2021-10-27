import re

def test_addon_registered(simple_icons_slugs):
    import _bpy
    import addon_utils

    # check addon registered
    installed_addons = [addon.__name__ for addon in addon_utils.modules()]
    assert "simple_icons_blender" in installed_addons

    # check addon operators registered
    current_operators = [cls.__name__ for cls in _bpy.types.Operator.__subclasses__()]
    for expected_si_operator in [f"AddSi_{slug}" for slug in simple_icons_slugs]:
        assert expected_si_operator in current_operators
