const fs = require("fs");
const path = require("path");

const root = __dirname;
const cssPath = path.join(root, "styles.css");
const css = fs.readFileSync(cssPath, "utf8");

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

const usedClasses = new Set();
const usedIds = new Set();

function addClassToken(token) {
  if (!token) return;
  token = token.replace(/^\.|^#/, "").split(/[:.[]/)[0];
  if (token && !token.includes("${")) usedClasses.add(token);
}

function addClassesFromString(str) {
  if (!str || str.includes("${")) return;
  str.split(/\s+/).forEach((c) => {
    if (c && !c.includes("${")) usedClasses.add(c);
  });
}

// HTML / template class attributes
for (const re of [
  /class(?:Name)?=["']([^"']+)["']/g,
  /classList\.(?:add|remove|toggle|contains)\(\s*["']([^"']+)["']/g,
  /className\s*=\s*["']([^"']+)["']/g,
  /class=["']([^"']+)["']/g,
  /class='([^']+)'/g,
]) {
  let m;
  while ((m = re.exec(sourceText))) addClassesFromString(m[1]);
}

// Classes inside JS template strings (class="foo bar")
const tplRe = /class="([a-zA-Z][^"]*)"/g;
let m;
while ((m = tplRe.exec(sourceText))) addClassesFromString(m[1]);

// querySelector / qsa class selectors
const selRe = /(?:querySelector(?:All)?|qsa|qs)\(\s*["']([^"']+)["']/g;
while ((m = selRe.exec(sourceText))) {
  m[1].split(/[\s,>+~]/).forEach((part) => {
    part = part.trim();
    if (part.startsWith(".")) addClassToken(part);
    if (part.startsWith("#")) usedIds.add(part.slice(1).split(/[:.[]/)[0]);
  });
}

// .closest(".foo")
const closestRe = /\.closest\(\s*["']([^"']+)["']/g;
while ((m = closestRe.exec(sourceText))) {
  m[1].split(/[\s,>+~]/).forEach((part) => {
    if (part.startsWith(".")) addClassToken(part);
  });
}

// ids
const idRe = /id=["']([^"']+)["']/g;
while ((m = idRe.exec(sourceText))) usedIds.add(m[1]);

const STATE = new Set([
  "active", "open", "visible", "hidden", "selected", "is-open", "is-active", "is-loaded",
  "compare-view", "workout-overlay-open", "cursor-hover", "logged-in", "sm-left", "sm-right",
  "hidden-level", "has-img", "magnetic", "reveal", "is-sticky", "featured", "animate", "cnt",
]);

const ALWAYS_KEEP = new Set([
  ...STATE,
  "bg-ambient", "bg-plus", "bg-dot", "bg-diamond", "bg-orb",
  "auth-overlay", "book-modal-overlay", "coach-modal-overlay",
  "ripple", "ripple-effect", "fg-cursor", "fg-cursor-dot",
]);

const ELEMENTS = new Set([
  "html", "body", "main", "img", "a", "button", "input", "select", "textarea", "form", "label",
  "nav", "header", "footer", "section", "article", "div", "span", "svg", "path", "polygon",
  "em", "strong", "small", "ul", "ol", "li", "p", "h1", "h2", "h3", "h4", "h5", "h6",
  "table", "thead", "tbody", "tr", "th", "td", "time", "blockquote", "details", "summary",
  "iframe", "video", "option",
]);

function splitSelectors(text) {
  const parts = [];
  let cur = "";
  let depth = 0;
  for (const ch of text) {
    if (ch === "(") depth++;
    else if (ch === ")") depth--;
    if (ch === "," && depth === 0) {
      parts.push(cur.trim());
      cur = "";
    } else cur += ch;
  }
  if (cur.trim()) parts.push(cur.trim());
  return parts;
}

function extractTokens(sel) {
  const classes = [];
  const ids = [];
  let mm;
  const rc = /\.([a-zA-Z_][\w-]*)/g;
  const ri = /#([a-zA-Z_][\w-]*)/g;
  while ((mm = rc.exec(sel))) classes.push(mm[1]);
  while ((mm = ri.exec(sel))) ids.push(mm[1]);
  return { classes, ids };
}

function partIsUsed(part) {
  const clean = part.replace(/::?(before|after|placeholder|webkit-details-marker|selection|focus-visible|focus-within)/g, "").trim();
  if (!clean || clean === ":root" || /^::/.test(part)) return true;

  const { classes, ids } = extractTokens(clean);
  if (ids.some((id) => usedIds.has(id))) return true;
  if (classes.some((c) => usedClasses.has(c) || ALWAYS_KEEP.has(c))) return true;

  const withoutTokens = clean.replace(/[#.][\w-]+/g, "").replace(/\[.*?\]/g, "").replace(/:\w+(-[\w-]+)*/g, "").trim();
  if (classes.length === 0 && ids.length === 0) {
    const first = withoutTokens.split(/[\s>+~]/).filter(Boolean)[0];
    if (!first || ELEMENTS.has(first)) return true;
  }
  return false;
}

function selectorIsUsed(selector) {
  return splitSelectors(selector).some(partIsUsed);
}

function parseBlocks(input) {
  const items = [];
  let i = 0;
  while (i < input.length) {
    if (input[i] === "/" && input[i + 1] === "*") {
      const end = input.indexOf("*/", i + 2);
      if (end < 0) break;
      items.push({ kind: "comment", text: input.slice(i, end + 2) });
      i = end + 2;
      continue;
    }
    if (input[i] === "@") {
      const open = input.indexOf("{", i);
      if (open < 0) break;
      let depth = 1;
      let j = open + 1;
      while (j < input.length && depth > 0) {
        if (input[j] === "{") depth++;
        else if (input[j] === "}") depth--;
        j++;
      }
      items.push({
        kind: "at",
        prelude: input.slice(i + 1, open).trim(),
        body: input.slice(open + 1, j - 1),
      });
      i = j;
      continue;
    }
    const open = input.indexOf("{", i);
    if (open < 0) break;
    const selector = input.slice(i, open).trim();
    if (!selector) {
      i = open + 1;
      continue;
    }
    let depth = 1;
    let j = open + 1;
    while (j < input.length && depth > 0) {
      if (input[j] === "{") depth++;
      else if (input[j] === "}") depth--;
      j++;
    }
    items.push({ kind: "rule", selector, body: input.slice(open + 1, j - 1).trim() });
    i = j;
  }
  return items;
}

function renderBlocks(blocks) {
  const out = [];
  const seen = new Set();
  let removed = 0;
  let dupes = 0;

  function walk(list, into) {
    for (const b of list) {
      if (b.kind === "comment") {
        into.push(b.text);
        continue;
      }
      if (b.kind === "at") {
        if (/^keyframes\s/i.test(b.prelude) || /^import\s/i.test(b.prelude) || /^font-face/i.test(b.prelude)) {
          into.push(`@${b.prelude}{${b.body}}`);
          continue;
        }
        const inner = [];
        walk(parseBlocks(b.body), inner);
        if (inner.length) into.push(`@${b.prelude}{\n${inner.join("\n")}\n}`);
        continue;
      }
      if (b.kind === "rule") {
        if (!selectorIsUsed(b.selector)) {
          removed++;
          continue;
        }
        const key = b.selector.replace(/\s+/g, " ") + "{" + b.body.replace(/\s+/g, " ") + "}";
        if (seen.has(key)) {
          dupes++;
          continue;
        }
        seen.add(key);
        into.push(`${b.selector}{${b.body}}`);
      }
    }
    return { removed, dupes };
  }

  walk(blocks, out);
  return { text: out.join("\n\n").replace(/\n{3,}/g, "\n\n").trim() + "\n", removed, dupes };
}

const blocks = parseBlocks(css);
const { text, removed, dupes } = renderBlocks(blocks);

fs.writeFileSync(path.join(root, "styles.css.bak"), css);
fs.writeFileSync(cssPath, text);

console.log("Used classes:", usedClasses.size);
console.log("Used ids:", usedIds.size);
console.log("Original lines:", css.split("\n").length);
console.log("Cleaned lines:", text.split("\n").length);
console.log("Removed unused rules:", removed);
console.log("Removed duplicate rules:", dupes);
