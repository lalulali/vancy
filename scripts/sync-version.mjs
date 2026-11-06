#!/usr/bin/env node
// Keeps every shipped version string in sync with package.json.
//
// package.json is the single source of truth. This script never invents a
// version; it copies the one from package.json into the places that must
// repeat it:
//   - .agents/skills/*/SKILL.md  ->  metadata.version
//   - .agents/manifest.json      ->  version
//
// Usage:
//   node scripts/sync-version.mjs            # write the missing copies
//   node scripts/sync-version.mjs --check    # fail if anything has drifted
//   node scripts/sync-version.mjs --stage    # write, then `git add` the files
//
// `npm version <bump>` runs this automatically via the "version" script.
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PKG_PATH = path.join(ROOT, "package.json");
const SKILLS_DIR = path.join(ROOT, ".agents", "skills");
const MANIFEST_PATH = path.join(ROOT, ".agents", "manifest.json");

const check = process.argv.includes("--check");
const stage = process.argv.includes("--stage");

function readVersion() {
  const { version } = JSON.parse(fs.readFileSync(PKG_PATH, "utf8"));
  if (typeof version !== "string" || version.trim() === "") {
    throw new Error('package.json has no "version" field');
  }
  return version.trim();
}

/** Replace the `version` line inside the YAML frontmatter's metadata block. */
function syncSkillFrontmatter(text, version) {
  const lines = text.split("\n");
  if (lines[0] !== "---") return text;

  const end = lines.indexOf("---", 1);
  if (end === -1) return text;

  let inMetadata = false;
  for (let i = 1; i < end; i += 1) {
    const line = lines[i];

    if (/^metadata:\s*$/.test(line)) {
      inMetadata = true;
      continue;
    }
    if (inMetadata && /^\S/.test(line)) {
      inMetadata = false;
      continue;
    }
    if (!inMetadata) continue;

    const match = line.match(/^(\s+version:\s*)"?([^"\n]*)"?\s*$/);
    if (match) {
      lines[i] = `${match[1]}"${version}"`;
      break;
    }
  }

  return lines.join("\n");
}

/** Replace the top-level `"version"` value without reformatting the file. */
function syncManifest(text, version) {
  return text.replace(/^(\{\s*\n\s*"version":\s*)"[^"]*"/, `$1"${version}"`);
}

const version = readVersion();
const changed = [];
const drifted = [];

function apply(relPath, transform) {
  const fullPath = path.join(ROOT, relPath);
  if (!fs.existsSync(fullPath)) return;

  const before = fs.readFileSync(fullPath, "utf8");
  const after = transform(before);
  if (after === before) return;

  if (check) {
    drifted.push(relPath);
    return;
  }

  fs.writeFileSync(fullPath, after);
  changed.push(relPath);
}

for (const name of fs.readdirSync(SKILLS_DIR)) {
  apply(`.agents/skills/${name}/SKILL.md`, (text) => syncSkillFrontmatter(text, version));
}
apply(".agents/manifest.json", (text) => syncManifest(text, version));

if (check) {
  if (drifted.length > 0) {
    console.error(`Version drift: package.json says ${version}, but these files disagree:`);
    for (const file of drifted) console.error(`  ${file}`);
    console.error("Run `node scripts/sync-version.mjs` (or `npm version <bump>`) to fix.");
    process.exit(1);
  }
  console.log(`Version check passed: every file agrees on ${version}.`);
  process.exit(0);
}

if (changed.length === 0) {
  console.log(`Version already in sync: ${version}.`);
} else {
  console.log(`Synced ${changed.length} file(s) to ${version}:`);
  for (const file of changed) console.log(`  ${file}`);
}

if (stage && changed.length > 0) {
  const result = spawnSync("git", ["add", ...changed], { cwd: ROOT, stdio: "inherit" });
  if (result.status !== 0) {
    console.error("git add failed; the files are updated but not staged.");
    process.exit(result.status ?? 1);
  }
}
