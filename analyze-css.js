const fs = require("fs");
const path = require("path");

const root = __dirname;
const css = fs.readFileSync(path.join(root, "styles.css"), "utf8");

// Collect HTML/JS content (exclude node_modules)
function walk(dir, exts, files = []) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ent.name === "node_modules" || ent.name.startsWith(".")) continue;
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) walk(p, exts, files);
    else if (exts.some((e) => ent.name.endsWith(e))) files.push(p);
  }
  return files;
}

const sources = walk(root, [".html", ".js"]).filter((f) => !f.includes("node_modules"));
let sourceText = "";
for (const f of sources) sourceText += fs.readFileSync(f, "utf8") + "\n";

// Extract classes from HTML/JS
const usedClasses = new Set();
const classAttrRe = /class(?:Name)?=["']([^"']+)["']/g;
const classListRe = /classList\.(?:add|remove|toggle|contains)\(\s*["']([^"']+)["']/g;
const templateClassRe = /class="([^"]+)"/g;
for (const re of [classAttrRe, classListRe, templateClassRe]) {
  let m;
  while ((m = re.exec(sourceText))) {
    m[1].split(/\s+/).forEach((c) => c && usedClasses.add(c));
  }
}
// Also match class='...' in JS templates
const classSingleRe = /class='([^']+)'/g;
while ((m = classSingleRe.exec(sourceText))) {
  m[1].split(/\s+/).forEach((c) => c && usedClasses.add(c));
}

// Parse CSS rules - extract top-level selectors (simplified)
const ruleBlocks = [];
const stripComments = css.replace(/\/\*[\s\S]*?\*\//g, "");
let depth = 0;
let blockStart = 0;
let selectorStart = 0;
let inAtRule = false;

for (let i = 0; i < stripComments.length; i++) {
  const ch = stripComments[i];
  if (ch === "{") {
    if (depth === 0) {
      const sel = stripComments.slice(selectorStart, i).trim();
      blockStart = i + 1;
      inAtRule = sel.startsWith("@");
    }
    depth++;
  } else if (ch === "}") {
    depth--;
    if (depth === 0 && !inAtRule) {
      const body = stripComments.slice(blockStart, i);
      ruleBlocks.push({ selector: stripComments.slice(selectorStart, blockStart - 1).trim(), body: body.trim(), start: selectorStart });
    } else if (depth === 0) {
      inAtRule = false;
    }
    selectorStart = i + 1;
  }
}

// Extract class names from selectors
function extractClasses(selector) {
  const classes = [];
  const re = /\.([a-zA-Z_][\w-]*)/g;
  let m;
  while ((m = re.exec(selector))) classes.push(m[1]);
  return classes;
}

const selectorCounts = new Map();
const classToSelectors = new Map();

for (const block of ruleBlocks) {
  if (!block.selector || block.selector.startsWith("@")) continue;
  const parts = block.selector.split(",").map((s) => s.trim());
  for (const part of parts) {
    const count = selectorCounts.get(part) || 0;
    selectorCounts.set(part, count + 1);
    for (const cls of extractClasses(part)) {
      if (!classToSelectors.has(cls)) classToSelectors.set(cls, []);
      classToSelectors.get(cls).push(part);
    }
  }
}

// Duplicate exact selectors
const dupSelectors = [...selectorCounts.entries()].filter(([, c]) => c > 1).sort((a, b) => b[1] - a[1]);

// CSS classes never referenced in HTML/JS
const cssClasses = new Set(classToSelectors.keys());
const unusedClasses = [...cssClasses].filter((c) => !usedClasses.has(c)).sort();

// Used classes with no CSS
const missingCss = [...usedClasses].filter((c) => !cssClasses.has(c) && !c.includes("${")).sort();

// Find duplicate class definitions (same class, different rule blocks)
const classDefCount = new Map();
for (const block of ruleBlocks) {
  for (const cls of extractClasses(block.selector)) {
    classDefCount.set(cls, (classDefCount.get(cls) || 0) + 1);
  }
}
const multiDefClasses = [...classDefCount.entries()].filter(([, c]) => c > 3).sort((a, b) => b[1] - a[1]);

console.log("=== STATS ===");
console.log("CSS lines:", css.split("\n").length);
console.log("Rule blocks:", ruleBlocks.length);
console.log("Unique CSS classes:", cssClasses.size);
console.log("Used classes in HTML/JS:", usedClasses.size);
console.log("Unused CSS classes:", unusedClasses.length);
console.log("Duplicate exact selectors:", dupSelectors.length);
console.log("Classes with 4+ rule blocks:", multiDefClasses.length);

console.log("\n=== TOP DUPLICATE SELECTORS (exact) ===");
dupSelectors.slice(0, 40).forEach(([s, c]) => console.log(c + "x", s.slice(0, 120)));

console.log("\n=== SAMPLE UNUSED CLASSES (first 80) ===");
unusedClasses.slice(0, 80).forEach((c) => console.log(c));

console.log("\n=== CLASSES WITH MOST RULE BLOCKS ===");
multiDefClasses.slice(0, 30).forEach(([c, n]) => console.log(n, c));

// Write full unused list
fs.writeFileSync(path.join(root, "css-unused-classes.txt"), unusedClasses.join("\n"));
fs.writeFileSync(path.join(root, "css-dup-selectors.txt"), dupSelectors.map(([s, c]) => c + "x " + s).join("\n"));
console.log("\nWrote css-unused-classes.txt and css-dup-selectors.txt");
