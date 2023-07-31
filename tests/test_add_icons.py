import os
import re

import pytest

from helpers import simple_icons_slugs, simple_icons_titles


@pytest.mark.parametrize(
    ('slug', 'title'),
    zip(simple_icons_slugs(), simple_icons_titles())
)
def test_add_icon_operators(slug, title):
    import bpy

    # add icon
    op_executor = getattr(bpy.ops.mesh, f"si_{slug}")
    assert op_executor() == {"FINISHED"}

    # get added icon (created inside a new collection)
    last_collection = bpy.context.scene.collection.children[-1]
    assert last_collection.name == title.replace(os.sep, "-")
    last_object = last_collection.all_objects[-1]

    # check that icon is properly added
    assert bpy.context.scene.active_object == last_object
    assert last_object in bpy.context.selected_objects

    assert last_object.type == "CURVE"
    assert tuple(last_object.location) == (0.0, 0.0, 0.0)
    assert re.match(r'SVGMat\.\d+', last_object.active_material.name)

    if slug == "simpleicons":
        # test simpleicons icon geometry
        bezier_curves_expected_n_points = [12, 4, 5, 12, 4, 6]
        assert len(last_object.data.splines) == len(bezier_curves_expected_n_points)

        for i, spline in enumerate(last_object.data.splines):
            assert spline.type == "BEZIER"
            assert len(spline.bezier_points) == bezier_curves_expected_n_points[i]

    for obj in last_collection.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(last_collection)

    # check that was removed
    last_collection = bpy.context.scene.collection.children[-1]
    assert last_collection.name != title.replace(os.sep, "-")
    last_object = last_collection.all_objects[-1]

    # check that icon is properly added
    assert last_object.type != "CURVE"
    assert last_object.type == "CAMERA"
