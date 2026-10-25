#!/usr/bin/env node
// Maintainer check (not shipped): validates every skill and the bundled agent before publishing.
// - SKILL.md frontmatter: name matches folder, hyphen-case, one-line description <= 1024 chars,
//   compatibility present and <= 500 chars
// - every file referenced as `references/...`, `scripts/...`, `assets/...` in SKILL.md exists, and no
//   file in those folders is orphaned (never mentioned in SKILL.md)
// - a `references/*.md` file never points at a sibling reference that only exists in another skill
// - intentionally duplicated files (each skill is standalone) are byte-identical across their carriers
// - every Python script parses (ast) with the system python3
// - the agent JSON is valid, its prompt/resources exist, every skill is wired in and routed, the
//   persona name is consistent, and no stray Markdown agent file ships beside the JSON
// - `npm pack` contains no personal data (tracker CSV, docx, offers, reference sheets, .env, pyc)
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SKILLS = path.join(ROOT, ".agents", "skills");
const DUPLICATED = [
  "scripts/render_docx.py",
  "scripts/doc_lint.py",
  "references/evidence.md",
  "references/regional-conventions.md",
  "references/markdown-format.md",
  "references/ats-parsing.md",
  "references/keyword-tailoring.md",
];
const errors = [];
const hashes = new Map();
const skillNames = fs
  .readdirSync(SKILLS, { withFileTypes: true })
  .filter((d) => d.isDirectory())
  .map((d) => d.name)
  .sort();

// Filenames of every reference file, by skill (to detect dangling cross-skill pointers).
const refsBySkill = new Map();
for (const name of skillNames) {
  const rd = path.join(SKILLS, name, "references");
  refsBySkill.set(name, fs.existsSync(rd) ? new Set(fs.readdirSync(rd)) : new Set());
}
const allRefNames = new Set([...refsBySkill.values()].flatMap((s) => [...s]));

for (const name of skillNames) {
  const dir = path.join(SKILLS, name);
  const mdPath = path.join(dir, "SKILL.md");
  if (!fs.existsSync(mdPath)) { errors.push(`${name}: missing SKILL.md`); continue; }
  const md = fs.readFileSync(mdPath, "utf8");
  const fm = md.match(/^---\n([\s\S]*?)\n---/);
  if (!fm) { errors.push(`${name}: missing frontmatter`); continue; }
  const fmName = (fm[1].match(/^name:\s*(.+)$/m) || [])[1]?.trim();
  const desc = (fm[1].match(/^description:\s*(.+)$/m) || [])[1]?.trim() || "";
  const compat = (fm[1].match(/^compatibility:\s*(.+)$/m) || [])[1]?.trim() || "";
  if (fmName !== name) errors.push(`${name}: frontmatter name "${fmName}" != folder`);
  if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(name) || name.length > 64) errors.push(`${name}: invalid name`);
  if (!desc || /^[>|]/.test(desc)) errors.push(`${name}: description must be a single non-empty line`);
  if (desc.length > 1024) errors.push(`${name}: description ${desc.length} > 1024 chars`);
  if (/[<>]/.test(desc)) errors.push(`${name}: description contains angle brackets`);
  if (!compat) errors.push(`${name}: missing compatibility`);
  if (compat.length > 500) errors.push(`${name}: compatibility ${compat.length} > 500 chars`);
  const lines = md.split("\n").length;
  if (lines > 500) errors.push(`${name}: SKILL.md has ${lines} lines (> 500)`);

  const mentioned = new Set(md.match(/`((?:references|scripts|assets)\/[\w.\-/]+)`/g) || []);
  for (const ref of mentioned) {
    const rel = ref.slice(1, -1);
    if (!fs.existsSync(path.join(dir, rel))) errors.push(`${name}: referenced file missing: ${rel}`);
  }
  // Orphans: files in references/, scripts/, assets/ that SKILL.md never names.
  for (const sub of ["references", "scripts", "assets"]) {
    const sd = path.join(dir, sub);
    if (!fs.existsSync(sd)) continue;
    for (const f of fs.readdirSync(sd)) {
      if (f.startsWith(".") || f === "__pycache__") continue;
      if (!md.includes(f)) errors.push(`${name}: ${sub}/${f} is never mentioned in SKILL.md`);
    }
  }
  // Dangling sibling pointers inside reference files.
  const rd = path.join(dir, "references");
  if (fs.existsSync(rd)) {
    for (const f of fs.readdirSync(rd).filter((x) => x.endsWith(".md"))) {
      const body = fs.readFileSync(path.join(rd, f), "utf8");
      for (const m of body.matchAll(/`([\w-]+\.md)`/g)) {
        const target = m[1];
        if (allRefNames.has(target) && !refsBySkill.get(name).has(target)) {
          errors.push(`${name}: references/${f} points at ${target}, which is not in this skill`);
        }
      }
    }
  }
  // Every Python script must parse, and # >>> shared:<id> blocks must match across scripts.
  const sd = path.join(dir, "scripts");
  if (fs.existsSync(sd)) {
    for (const f of fs.readdirSync(sd).filter((x) => x.endsWith(".py"))) {
      const sp = path.join(sd, f);
      const src = fs.readFileSync(sp, "utf8");
      for (const m of src.matchAll(/# >>> shared:(\w+)\n([\s\S]*?)# <<< shared:\1/g)) {
        const key = `shared:${m[1]}`;
        const h = crypto.createHash("sha256").update(m[2]).digest("hex");
        if (!hashes.has(key)) hashes.set(key, new Map());
        hashes.get(key).set(`${name}/scripts/${f}`, h);
      }
      const r = spawnSync("python3", ["-c", "import ast,sys; ast.parse(open(sys.argv[1], encoding='utf-8').read())", sp], { encoding: "utf8" });
      if (r.error) { console.warn(`  (python3 not available; skipped syntax check of ${name}/scripts/${f})`); break; }
      if (r.status !== 0) errors.push(`${name}: scripts/${f} does not parse: ${(r.stderr || "").trim().split("\n").pop()}`);
    }
  }
  for (const rel of DUPLICATED) {
    const p = path.join(dir, rel);
    if (!fs.existsSync(p)) continue;
    const h = crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
    if (!hashes.has(rel)) hashes.set(rel, new Map());
    hashes.get(rel).set(name, h);
  }
}
for (const [rel, bySkill] of hashes) {
  if (new Set(bySkill.values()).size > 1) {
    errors.push(`${rel} differs between skills: ${[...bySkill.keys()].join(", ")} (copy the updated file into every skill)`);
  }
}

// Validate the bundled custom agent, if present.
const AGENTS_DIR = path.join(ROOT, ".agents", "agents");
if (fs.existsSync(AGENTS_DIR)) {
  for (const f of fs.readdirSync(AGENTS_DIR)) {
    const p = path.join(AGENTS_DIR, f);
    if (fs.statSync(p).isFile() && !f.endsWith(".json")) {
      errors.push(`agents/${f}: stray file next to the agent JSON (the prompt lives in a sub-folder)`);
    }
  }
  for (const f of fs.readdirSync(AGENTS_DIR)) {
    if (!f.endsWith(".json")) continue;
    const p = path.join(AGENTS_DIR, f);
    let agent;
    try {
      agent = JSON.parse(fs.readFileSync(p, "utf8"));
    } catch (e) {
      errors.push(`agents/${f}: invalid JSON (${e.message})`);
      continue;
    }
    if (!agent.description) errors.push(`agents/${f}: missing description`);
    if (agent.name !== f.replace(/\.json$/, "")) errors.push(`agents/${f}: name "${agent.name}" != file name`);
    if (!agent.permissions || !Array.isArray(agent.permissions.rules)) errors.push(`agents/${f}: missing permissions.rules`);
    // prompt file:// target must exist
    let promptText = "";
    if (typeof agent.prompt === "string" && agent.prompt.startsWith("file://")) {
      const rel = agent.prompt.slice("file://".length).replace(/^\.\//, "");
      const pp = path.join(AGENTS_DIR, rel);
      if (!fs.existsSync(pp)) errors.push(`agents/${f}: prompt file missing: ${rel}`);
      else promptText = fs.readFileSync(pp, "utf8");
    }
    // every skill:// / file:// resource must point at an existing file in this package
    const wired = new Set();
    for (const r of agent.resources || []) {
      if (typeof r !== "string" || r.includes("*")) continue;
      if (r.startsWith("skill://")) {
        const rel = r.slice("skill://".length);
        if (!fs.existsSync(path.join(ROOT, rel))) errors.push(`agents/${f}: skill resource missing: ${rel}`);
        const m = rel.match(/skills\/([^/]+)\/SKILL\.md$/);
        if (m) wired.add(m[1]);
      } else if (r.startsWith("file://")) {
        const rel = r.slice("file://".length).replace(/^\.\//, "");
        if (!fs.existsSync(path.join(AGENTS_DIR, rel))) errors.push(`agents/${f}: file resource missing: ${rel}`);
      }
    }
    for (const s of skillNames) {
      if (!wired.has(s)) errors.push(`agents/${f}: skill ${s} is not listed in resources`);
      if (promptText && !promptText.includes("`" + s + "`")) errors.push(`agents/${f}: prompt never routes to skill ${s}`);
    }
    // Persona name must match between prompt and welcome message.
    const persona = (promptText.match(/You are (\w+),/) || [])[1];
    if (persona && !(agent.welcomeMessage || "").includes(persona)) {
      errors.push(`agents/${f}: welcomeMessage does not use the persona name "${persona}"`);
    }
    for (const needle of ["artifacts/input", "artifacts/output"]) {
      if (promptText && !promptText.includes(needle)) errors.push(`agents/${f}: prompt does not mention ${needle}`);
    }
  }
}

// The published tarball must not contain personal data or junk.
{
  const r = spawnSync("npm", ["pack", "--dry-run", "--json", "--ignore-scripts"], { cwd: ROOT, encoding: "utf8" });
  if (r.status === 0) {
    try {
      const files = JSON.parse(r.stdout)[0].files.map((x) => x.path);
      const bad = files.filter((x) => /(^|\/)(job-applications\.csv|\.env[^/]*|\.DS_Store)$|\.(docx|pyc|pem|key|tgz|jsonl)$|__pycache__|offers[^/]*\.json$|_References[^/]*\.md$/i.test(x) && !/(^|\/)example-offers\.json$/.test(x));
      for (const b of bad) errors.push(`npm pack would publish a file that must not ship: ${b}`);
    } catch (e) {
      errors.push(`could not parse npm pack output: ${e.message}`);
    }
  } else {
    console.warn("  (npm pack --dry-run unavailable; skipped tarball content check)");
  }
}

if (errors.length) {
  console.error("Skill check FAILED:\n  " + errors.join("\n  "));
  process.exit(1);
}
console.log(`Skill check passed: ${skillNames.length} skills.`);
