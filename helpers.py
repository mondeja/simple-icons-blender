import re


def simple_icons_slugs():
    with open("simple_icons_blender.py") as f:
        slugs = re.findall(
            r'^class AddSi_(.+)\(A,O\):',
            f.read(),
            re.M,
        )
    return slugs


def simple_icons_titles():
    with open("simple_icons_blender.py") as f:
        titles = re.findall(r'bl_label=(.+);bl_description=', f.read(), re.M)
    return [title.strip("'").replace("\\'", "'") for title in titles[:-1]]


def simple_icons_svgs():
    with open("simple_icons_blender.py") as f:
        svgs = re.findall(r';si_svg=(.+)$', f.read(), re.M)
    return [svg.strip("'").replace("\\'", "'") for svg in svgs]
