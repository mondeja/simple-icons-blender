import fs from "node:fs";
import * as icons from "simple-icons/icons";

const ASCII_ALPHABET = "abcdefghijklmnopqrstuvwxyz";

const simplifyHexIfPossible = (hex) => {
  if (hex[0] === hex[1] && hex[2] === hex[3] && hex[4] == hex[5]) {
    return `${hex[0]}${hex[2]}${hex[4]}`;
  }
  return hex;
};

let simpleIconsClassesString = "";
const lettersForPagination = {};
for (let icon of Object.values(icons)) {
  const styledSvg = icon.svg
    .replace(/'/g, "\\'")
    .replace(
      '<path d="',
      `<path fill="#${simplifyHexIfPossible(icon.hex)}" d="`
    );
  const escapedTitle = icon.title.replace(/'/g, "\\'");

  simpleIconsClassesString +=
    `class AddSi_${icon.slug}(A,O):` +
    `bl_idname="mesh.si_${icon.slug}";` +
    `bl_label='${escapedTitle}';` +
    `bl_description='Add ${escapedTitle} icon';` +
    `si_svg='${styledSvg}'\n`;

  const firstLetterLower = icon.title[0].toLowerCase();
  if (lettersForPagination[firstLetterLower] === undefined) {
    if (ASCII_ALPHABET.includes(firstLetterLower)) {
      lettersForPagination[firstLetterLower] = [icon.title];
    } else {
      lettersForPagination["symbol"] = [icon.title];
    }
  } else {
    if (ASCII_ALPHABET.includes(firstLetterLower)) {
      lettersForPagination[firstLetterLower].push(icon.title);
    } else {
      lettersForPagination["symbol"].push(icon.title);
    }
  }
}

let letterSubmenuClasses = "";
for (const letter in lettersForPagination) {
  if (letter !== "symbol") {
    letterSubmenuClasses += `class VIEW3D_MT_simple_icons_add_${letter}_submenu(LS):
    bl_idname = "VIEW3D_MT_simple_icons_add_${letter}_submenu"
    bl_label = "${letter.toUpperCase()}"\n\n`;
  }
}

const template = fs.readFileSync("simple_icons_blender.template").toString();
let newInitContent =
  `# This file has been generated\n\n` +
  template
    .replace("%(simple_icons_classes)s", simpleIconsClassesString)
    .replace(
      "%(letter_submenus_array)s",
      JSON.stringify(Object.keys(lettersForPagination))
    )
    .replace("%(letter_submenu_classes)s", letterSubmenuClasses);

fs.writeFileSync("simple_icons_blender.py", newInitContent);
