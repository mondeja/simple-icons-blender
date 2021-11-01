const fs = require("fs");
const path = require("path");
const simpleIcons = require("simple-icons");

const COMMIT_HASH = "3fdcb11536ef0356f3f84594fbee835531bcd05b";

const failedSlugsFile = path.join("scripts", "showcase", "failed-slugs.txt")
const failedSlugs = fs.readFileSync(failedSlugsFile)
  .toString()
  .split("\n")
  .filter(l => !(l.trim()).startsWith("#") && l.trim().length > 0)
  .map(l => l.trim());

let failedSlugsTitlesList = "";
for (let i=0; i<failedSlugs.length; i++) {
  const slug = failedSlugs[i];
  const icon = simpleIcons.Get(slug),
    link = `https://github.com/simple-icons/simple-icons/blob/${COMMIT_HASH}/icons/${slug}.svg`
  failedSlugsTitlesList += `- [${icon.title} - ${slug}](${link})\n`
}
console.log(failedSlugsTitlesList);
