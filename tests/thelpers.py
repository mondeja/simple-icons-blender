import re


def simple_icons_slugs():
    with open("simple_icons_blender.py") as f:
        slugs = re.findall(
            r'^class AddSi_(.+)\(AddSi, bpy\.types\.Operator\):$',
            f.read(),
            re.M,
        )
    return slugs


def simple_icons_titles():
    with open("simple_icons_blender.py") as f:
        titles = re.findall(r'^    bl_label = (.+)$', f.read(), re.M)
    return [title.strip("'").replace("\\'", "'") for title in titles[:-1]]
