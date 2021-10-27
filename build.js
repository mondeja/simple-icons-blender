const fs = require("fs");
const simpleIcons = require("simple-icons");

const simpleIconsArray = Object.keys(simpleIcons);

let simpleIconsClassesString = '';
for (let slug of simpleIconsArray) {
  const icon = simpleIcons[slug];
  const styledSvg = icon.svg
    .replace(/'/g, "\\'")
    .replace('<path d="', `<path fill="#${icon.hex}" d="`);
  const escapedTitle = icon.title.replace(/'/g, "\\'");

  simpleIconsClassesString += `class AddSi_${slug}(AddSi, bpy.types.Operator):
    bl_idname = "mesh.si_${slug}"
    bl_label = '${escapedTitle}'
    bl_description = 'Add ${escapedTitle} brand icon'
    si_svg = '${styledSvg}'
`
}

const template = fs.readFileSync("simple_icons_blender.template").toString();
let newInitContent =
  `# This file has been created automatically, don't edit it!\n\n` +
  template.replace(
    "%(simple_icons_classes)s", simpleIconsClassesString
  );

fs.writeFileSync("simple_icons_blender.py", newInitContent);
