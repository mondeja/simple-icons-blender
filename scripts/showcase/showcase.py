"""Simple Icons Blender demo script.

All options passed after '--' are treated as options for the script.

Examples:
    blender --python scripts/showcase/showcase.py -- \
        --help

    blender scripts/showcase/showcase.blend \
        --python scripts/showcase/showcase.py -- \
        --icons 0-10 --debug

    blender scripts/showcase/showcase.blend \
        --python scripts/showcase/showcase.py -- \
        --icons 0-5 \
        --debug \
        --layout zoomed \
        --fps 60 \
        --render
"""

import argparse
import math
import os
import shutil
import subprocess
import sys
import tempfile

import bpy

ROOT_DIR = os.getcwd()
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)


from helpers import simple_icons_slugs, simple_icons_titles, simple_icons_svgs


DEFAULT_RENDER_DIR = os.path.join(ROOT_DIR, "scripts", "showcase")


def remove_all_objects_from_collection(collection):
    for obj in collection.all_objects:
        bpy.data.objects.remove(obj, do_unlink=True)


def build_layout(layout, add_titles, inkscape_comparison, loop):
    response = {"name": layout}
    if layout == "horizontal":
        # handle all layout possibilities
        if inkscape_comparison:
            if loop:
                response.update({
                    "camera_y_location": -0.0025 if add_titles else -0.0013,
                    "camera_lens": 184 if add_titles else 213,
                    "camera_keyframe_start_padding": (
                        0.04918 if add_titles else 0.042
                    ),
                    "camera_keyframe_end_padding": (
                        -0.05305 if add_titles else -0.0255
                    ),
                })
            else:
                response.update({
                    "camera_y_location": -0.0025 if add_titles else -0.0013,
                    "camera_lens": 184 if add_titles else 213,
                    "camera_keyframe_start_padding": (
                        0.04918 if add_titles else 0.032
                    ),
                    "camera_keyframe_end_padding": (
                        -0.05 if add_titles else None
                    ),
                })
        else:
            if loop:
                response.update({
                    "camera_y_location": (
                        0.002 if add_titles else 0.0036
                    ),
                    "camera_lens": 184 if add_titles else 280,
                    "camera_keyframe_start_padding": (
                        0.04918 if add_titles else 0.032
                    ),
                    "camera_keyframe_end_padding": (
                        -0.0529 if add_titles else -0.036
                    ),
                })
            else:
                response.update({
                    "camera_y_location": (
                        0.002 if add_titles else 0.0036
                    ),
                    "camera_lens": 184 if add_titles else 280,
                    "camera_keyframe_start_padding": (
                        0.04918 if add_titles else 0.032
                    ),
                    "camera_keyframe_end_padding": (
                        -0.0493 if add_titles else -0.03393
                    ),
                })
        response.update({
            "camera_z_location": 0.51,
            "resolution": (800, 100 if not inkscape_comparison else 180),
            "n_icons_shown": 8 if not add_titles else 12,
        })
    elif layout == "landscape":
        if add_titles:
            raise NotImplementedError(
                "'landscape' layout does not support titles"
            )
        if inkscape_comparison:
            raise NotImplementedError(
                "'landscape' layout does not support Inkscape comparison"
            )
        response.update({
            "camera_z_location": 0.11,
            "camera_y_location": 0.0036,
            "camera_keyframe_start_padding": 0.007,
            "camera_keyframe_end_padding": -0.0105,
            "camera_lens": 265,
            "resolution": (640, 480),
            "n_icons_shown": 2,
        })
    else:
        raise NotImplementedError(f"Layout '{layout}' not implemented")
    return response


class SimpleIconsShowcase:
    def __init__(
        self,
        fps=24,
        layout="horizontal",
        loop=False,
        space_between_icons=0.0085,
        icons_each_second=2,
        add_titles=False,
        inkscape_comparison=False,
        icons='0-inf',
        setup_scene=True,
        render=False,
        render_gif=False,
        render_mp4=False,
        render_dir=DEFAULT_RENDER_DIR,
        logger=sys.stdout,
        debug=True,
    ):
        self.fps = fps
        self.space_between_icons = space_between_icons
        self.add_titles = add_titles
        self.loop = loop
        self.inkscape_comparison = inkscape_comparison
        if self.inkscape_comparison and not shutil.which("inkscape"):
            raise EnvironmentError(
                "You need to install inkscape to make comparison between"
                " renderings."
            )
        self.layout = build_layout(
            layout,
            add_titles,
            inkscape_comparison,
            loop,
        )

        self.setup_scene = setup_scene
        self.render_gif = render or render_gif
        self.render_mp4 = render or render_mp4
        self.render_dir = render_dir
        self.frames_dir = os.path.join(self.render_dir, "frames")
        self.inkscape_pngs_dir = os.path.join(
            self.render_dir,
            "inkscape-pngs",
        )

        self.slugs_titles_svgs = self.filter_slugs(
            list(zip(
                simple_icons_slugs(),
                simple_icons_titles(),
                simple_icons_svgs(),
            )),
            icons,
        )
        self.n_icons = len(self.slugs_titles_svgs)
        self.frame_end = (
            self.fps / icons_each_second * \
            (self.n_icons - self.layout["n_icons_shown"] + 1)
        )

        self.camera_start_location = (
            self.layout["camera_keyframe_start_padding"],
            self.layout["camera_y_location"],
            self.layout["camera_z_location"],
        )

        self.logger = (
            logger if debug else type("FakeLogger", (), {"write": lambda v: None})
        )

    def run(self):
        if self.setup_scene:
            self.configure_workspace()
            self.clear_3d_view()
            icons_objects = self.add_icons()
            if self.add_titles:
                self.add_icon_titles(icons_objects)
            if self.inkscape_comparison:
                self.inkscape_render_icons_pngs()
                self.add_inkscape_pngs(icons_objects)
            self.add_background()
            self.add_camera()
            self.add_camera_keyframes()
            self.configure_scene()

        if self.render_gif or self.render_mp4:
            self.check_render_dependencies()
            self.render_frame_images()

            if self.render_gif:
                self.ffmpeg_render("gif")
            if self.render_mp4:
                self.ffmpeg_render("mp4")

    def filter_slugs(self, slugs_titles_svgs, icons):
        # parse icons selector
        if os.path.isfile(icons):
            with open(icons) as f:
                slugs = []
                for slug in f.read().splitlines():
                    stripped_slug = slug.strip()
                    if not stripped_slug or stripped_slug.startswith("#"):
                        continue
                    slugs.append(stripped_slug)

            _slugs_titles_svgs = []
            for slug, title, svg in slugs_titles_svgs:
                if slug in slugs:
                    _slugs_titles_svgs.append((slug, title, svg))

            if len(slugs) != len(_slugs_titles_svgs):
                valid_slugs = [slug for slug, _, _ in _slugs_titles_svgs]
                for slug in slugs:
                    if slug not in valid_slugs:
                        raise ValueError(
                            f"Unknown selected icon slug '{slug}'"
                        )
            slugs_titles_svgs = _slugs_titles_svgs
        elif '-' in icons:
            icons_split = icons.split("-")
            icons = (
                int(icons_split[0]),
                int(icons_split[1]) if icons_split[1] != "inf" else len(slugs_titles_svgs),
            )
            slugs_titles_svgs = slugs_titles_svgs[icons[0]:icons[1]]
        elif ',' in icons:
            icons_split = icons.split(',')
            all_are_integers = True
            for icon in icons_split:
                for letter in icon:
                    if not letter.isdigit():
                        all_are_integers = False
                        break
                if not all_are_integers:
                    break

            _slugs_titles_svgs = []
            if all_are_integers:
                n_slugs = len(slugs_titles_svgs)
                for icon_index_str in icons_split:
                    icon_index = int(icon_index_str)
                    if icon_index >= n_slugs:
                        raise ValueError(
                            f"Index to select icon ({icon_index}) is outside"
                            f" icons select-by-index range (0-{n_slugs-1})"
                        )
                    _slugs_titles_svgs.append(slugs_titles_svgs[icon_index])
            else:
                slugs_titles_svgs_dict = {
                    slug: (title, svg) for slug, title, svg in slugs_titles_svgs
                }
                for slug in icons_split:
                    if slug not in slugs_titles_svgs_dict:
                        raise ValueError(
                            f"Unknown selected icon slug '{slug}'"
                        )
                    _slugs_titles_svgs.append((
                        slug,
                        *slugs_titles_svgs_dict[slug],
                    ))
            slugs_titles_svgs = _slugs_titles_svgs

        if not slugs_titles_svgs:
            raise ValueError(f"No icons selected using icons={icons}")

        # repeat starting icons pattern at the end to render a loop
        if self.loop:
            n_slugs = len(slugs_titles_svgs)
            for i in range(self.layout["n_icons_shown"]):
                slugs_titles_svgs.append(slugs_titles_svgs[i % n_slugs])

        return slugs_titles_svgs

    def check_render_dependencies(self):
        if not shutil.which("ffmpeg"):
            raise EnvironmentError("FFmpeg needed to render media files")

    def configure_workspace(self):
        bpy.context.window.workspace = bpy.data.workspaces['Scripting']

    def clear_3d_view(self):
        for collection in bpy.context.scene.collection.children:
            self.logger.write(
                f"Removing objects from collection '{collection.name}'\n",
            )
            remove_all_objects_from_collection(collection)
            bpy.data.collections.remove(collection)

        self.logger.write(
            "Removing objects from collection"
            f" '{bpy.context.scene.collection.name}'\n",
        )
        remove_all_objects_from_collection(bpy.context.scene.collection)

    def add_icons(self):
        icons_objects = []
        for i, (slug, _, _) in enumerate(self.slugs_titles_svgs):
            getattr(bpy.ops.mesh, f"si_{slug}")()
            icon = bpy.context.scene.collection.children[-1].all_objects[-1]
            icon.location[0] = i * self.space_between_icons
            icons_objects.append(icon)
            self.logger.write(f"Added icon geometry '{slug}'\n")
        return icons_objects

    def add_icon_titles(self, icons_objects):
        black_color_material = bpy.data.materials.new(name="Back")
        black_color_material.diffuse_color = (0, 0, 0, 1)

        for i, (_, title, _) in enumerate(self.slugs_titles_svgs):
            font_curve = bpy.data.curves.new(
                type="FONT",
                name="Font Curve",
            )
            font_curve.body = title.replace(" ", "\n")
            font_curve.align_x = "CENTER"

            font_obj = bpy.data.objects.new(
                name="Font Object",
                object_data=font_curve,
            )
            font_obj.scale = (0.0015, 0.0015, 0.0015)
            font_obj.location[1] = -0.0018
            font_obj.active_material = black_color_material

            bpy.context.scene.collection.objects.link(font_obj)

            font_obj.select_set(True)
            icons_objects[i].select_set(True)
            bpy.context.view_layer.objects.active = icons_objects[i]
            bpy.ops.object.align(
                align_mode="OPT_2", relative_to="OPT_4", align_axis={'X'})
            font_obj.select_set(False)
            icons_objects[i].select_set(False)
            self.logger.write(f"Added icon title '{title}'\n")

    def add_inkscape_pngs(self, icons_objects):
        for i, (slug, _, _) in enumerate(self.slugs_titles_svgs):
            self.logger.write(f"Adding inkscape image for '{slug}'...\n")
            filepath = os.path.join(self.inkscape_pngs_dir, f'{slug}.png')

            ink_material = bpy.data.materials.new(name=f"{slug}__inkmat")
            ink_material.preview_render_type = "FLAT"
            ink_material.use_nodes = True
            bsdf = ink_material.node_tree.nodes["Principled BSDF"]
            tex_image = ink_material.node_tree.nodes.new('ShaderNodeTexImage')
            tex_image.image = bpy.data.images.load(filepath)
            ink_material.node_tree.links.new(
                bsdf.inputs['Base Color'],
                tex_image.outputs['Color'],
            )

            # create plane
            bpy.ops.mesh.primitive_plane_add()
            plane_object = bpy.context.view_layer.objects.active
            plane_object.scale = (0.0035, 0.0035, 0.0035)
            plane_object.location[1] = -0.0088 if self.add_titles else -0.006

            # align in X with SVG icon
            plane_object.select_set(True)
            icons_objects[i].select_set(True)
            bpy.context.view_layer.objects.active = icons_objects[i]
            bpy.ops.object.align(
                align_mode="OPT_2", relative_to="OPT_4", align_axis={'X'})
            plane_object.select_set(False)
            icons_objects[i].select_set(False)

            if plane_object.data.materials:
                plane_object.data.materials[0] = ink_material
            else:
                plane_object.data.materials.append(ink_material)

    def add_background(self):
        self.logger.write("Adding background...\n")
        bpy.context.scene.world.color = (1, 1, 1)
        bpy.context.preferences.themes[
            'Default'
        ].view_3d.space.gradients.high_gradient = (1, 1, 1)
        self.logger.write("Background added\n")

    def add_camera(self):
        self.logger.write("Adding camera\n")
        camera_data = bpy.data.cameras.new(name='MainCamera')
        camera_data.lens = self.layout["camera_lens"]
        camera_object = bpy.data.objects.new('MainCamera', camera_data)
        camera_object.location = self.camera_start_location
        camera_object.scale = (1, 1, 0.001)

        bpy.context.scene.collection.objects.link(camera_object)
        bpy.context.scene.camera = bpy.data.objects['MainCamera']
        bpy.context.view_layer.objects.active = camera_object

        # set camera perspective
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_perspective = 'CAMERA'
                break

    def add_camera_keyframes(self):
        self.logger.write("Adding keyframes\n")
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = int(self.frame_end)

        camera_object = bpy.context.object

        camera_object.animation_data_create()
        camera_object.animation_data.action = bpy.data.actions.new(
            name="Showcase",
        )

        fcurve = camera_object.animation_data.action.fcurves.new(
            data_path="location",
        )
        keyframe_one = fcurve.keyframe_points.insert(
            frame=1,
            value=self.camera_start_location[0],
        )
        keyframe_one.interpolation = "LINEAR"

        keyframe_two = fcurve.keyframe_points.insert(
            frame=self.frame_end,
            value=self.space_between_icons * self.n_icons + \
                self.layout["camera_keyframe_end_padding"],
        )
        keyframe_two.interpolation = "LINEAR"

    def configure_scene(self):
        bpy.context.scene.render.resolution_x = self.layout["resolution"][0]
        bpy.context.scene.render.resolution_y = self.layout["resolution"][1]
        bpy.context.scene.render.fps = self.fps

        # disable gravity
        bpy.context.scene.use_gravity = False

        # jpeg output
        bpy.context.scene.render.image_settings.file_format = 'JPEG'
        bpy.context.scene.render.image_settings.quality = 100

        # render directory
        if os.path.isdir(self.frames_dir):
            shutil.rmtree(self.frames_dir)
        os.mkdir(self.frames_dir)
        bpy.context.scene.render.filepath = os.path.join(self.frames_dir, "frame-")

        resolution = 'x'.join(str(n) for n in self.layout['resolution'])
        self.logger.write(
            f"Configured scene:\n  - resolution={resolution}\n"
            f"  - fps={self.fps}\n  - frames_dir={self.frames_dir}\n"
        )

    def render_frame_images(self):
        self.logger.write(f"Rendering {self.frame_end} frame images...\n")
        bpy.ops.render.render(animation=True)

    def ffmpeg_render(self, extension):
        self.logger.write(f"Rendering 'showcase.{extension}'...\n")
        n_zeros = max(len(str(int(self.frame_end))), 4)
        if extension == "gif":
            args = ["-f", "image2"]
        else:
            args = []
        subprocess.run([
            "ffmpeg",
            *args,
            "-framerate",
            str(self.fps),
            "-i",
            os.path.join(self.frames_dir, f"frame-%0{n_zeros}d.jpg"),
            "-y",
            os.path.join(self.render_dir, f"showcase.{extension}"),
        ])

    def inkscape_render_icons_pngs(self):
        # render pngs versions of icons using inkscape
        if not os.path.isdir(self.inkscape_pngs_dir):
            os.mkdir(self.inkscape_pngs_dir)

        for slug, _, svg in self.slugs_titles_svgs:
            png_icon_filepath = os.path.join(
                self.inkscape_pngs_dir,
                f"{slug}.png"
            )
            if os.path.isfile(png_icon_filepath):
                continue

            tmp_filepath = os.path.join(
                tempfile.gettempdir(), f"{slug}.svg"
            )
            with open(tmp_filepath,  "w") as f:
                f.write(svg)
            self.logger.write(f"Rendering '{slug}' icon with Inkscape...\n")

            subprocess.run(
                [
                    "inkscape",
                    "-w",
                    "512",
                    "-h",
                    "512",
                    tmp_filepath,
                    "-o",
                    png_icon_filepath,
                ],
                stdout=subprocess.DEVNULL,
            )

def build_parser():
    parser = argparse.ArgumentParser(
        description="Render a Simple Icons Blender showcase"
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Print debug messages to STDOUT.',
    )
    parser.add_argument(
        '-f', '--fps', dest='fps', metavar='N', type=int,
        default=24,
        choices=[23.98, 24, 25, 29.97, 30, 50, 59.94, 60, 120, 240],
        help='Set frames per second for resulting output.',
    )
    parser.add_argument(
        '-l', '--layout', dest='layout', metavar='800x100 / 640x480', type=str,
        default='800x100',
        choices=['800x100', 'horizontal', '640x480', 'zoomed'],
        help='Set showcase layout from a set of predefined ones.',
    )
    parser.add_argument(
        '-s', '--space-between-icons', dest='space_between_icons', metavar='N',
        type=float, default=0.0085, help='Separation between icons.'
    )
    parser.add_argument(
        '--icons-each-second', dest='icons_each_second', metavar='N',
        type=float, default=2, help='Number of new icons shown each second.'
    )
    parser.add_argument(
        '--loop', action='store_true', help='Creates a looped output.',
    )
    parser.add_argument(
        '-t', '--add-titles', action='store_true',
        help='Add readable titles for each icon.',
    )
    parser.add_argument(
        '-k', '--inkscape-comparison', action='store_true',
        dest="inkscape_comparison",
        help='Compare icons rendered by Blender with icons rendered by'
             ' Inkscape (needs inkscape installed).',
    )
    parser.add_argument(
        '-i', '--icons', dest='icons',
        metavar='N-N / N,N,N... / SLUG,SLUG,SLUG... / SLUGS-FILEPATH',
        type=str, default='0-inf',
        help='Icons to include in the showcase. It can be specified in'
             ' different ways. If the format is N-N, the icons are selected'
             ' from the alphabetical ordered subset slicing it from N to N'
             ' being N 0-based indexes. You can use \'inf\' as the latest'
             ' index. If it is N,N,N... the icons are selected from the'
             ' alphabetical ordered subset choosing one by one instead of'
             ' subset from a range and if N are not numbers, then will be'
             ' considered as slugs. If you pass a file path, the icons slugs'
             ' must be defined in it, one by line.'
    )
    parser.add_argument(
        '--no-setup-scene', action='store_false', dest='setup_scene',
        help='Do not setup and configure the scene. This only has sense if you'
             ' are running the script from Blender scripting panel and the'
             ' scene has been previously configured.',
    )
    parser.add_argument(
        '-r', '--render', action='store_true', dest='render',
        help='Render the scene in MP4 and GIF formats. Needs FFmpeg installed.'
             ' Keep in mind that this could take a lot of time, so be sure'
             ' that all is in order before pass this option. This is the same'
             ' as executing the script with the options \'--render-gif\' and'
             ' \'--render-mp4\'.',
    )
    parser.add_argument(
        '--render-gif', action='store_true', dest='render_gif',
        help='Render the scene in GIF format.',
    )
    parser.add_argument(
        '--render-mp4', action='store_true', dest='render_mp4',
        help='Render the scene in MP4 format.',
    )
    parser.add_argument(
        '-D', '--render-dir', dest='render_dir',
        metavar='DIRPATH', type=str, default=DEFAULT_RENDER_DIR,
        help="Rendered output directory."
    )
    return parser


def parse_options(args=[]):
    parser = build_parser()
    if '-h' in args or '--help' in args:
        parser.print_help()
        sys.exit(1)
    opts, unknown = parser.parse_known_args(args)
    return opts


def run(args=[], running_in_background=False):
    opts = parse_options(args)

    kwargs = {
        "debug": opts.debug,
        "fps": opts.fps,
        'space_between_icons': opts.space_between_icons,
        'icons_each_second': opts.icons_each_second,
        'loop': opts.loop,
        'add_titles': opts.add_titles,
        'inkscape_comparison': opts.inkscape_comparison,
        'layout': opts.layout,
        'icons': opts.icons,
        "setup_scene": opts.setup_scene,
        "render": opts.render,
        "render_gif": opts.render_gif,
        "render_mp4": opts.render_mp4,
    }

    SimpleIconsShowcase(**kwargs).run()

    if running_in_background:
        sys.exit(0)
    return 0

def main():
    args, valid_args, running_in_background = [], False, False
    for arg in sys.argv:
        if arg == '--':
            valid_args = True
            continue
        elif arg in ["-b", "--background"]:
            running_in_background = True
        if valid_args:
            args.append(arg)
    run(args=args, running_in_background=running_in_background)

if __name__ == '__main__':
    main()
