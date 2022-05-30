import fs from "node:fs";
import * as icons from "simple-icons/icons";

const simplifyHexIfPossible = (hex) => {
  if (hex[0] === hex[1] && hex[2] === hex[3] && hex[4] == hex[5]) {
    return `${hex[0]}${hex[2]}${hex[4]}`;
  }
  return hex;
};

let simpleIconsClassesString = '';
for (let si in icons) {
  const icon = icons[si];
  const styledSvg = icon.svg
    .replace(/'/g, "\\'")
    .replace('<path d="', `<path fill="#${simplifyHexIfPossible(icon.hex)}" d="`);
  const escapedTitle = icon.title.replace(/'/g, "\\'");

  simpleIconsClassesString += `class AddSi_${icon.slug}(AddSi, bpy.types.Operator):
    bl_idname = 'mesh.si_${icon.slug}'
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
