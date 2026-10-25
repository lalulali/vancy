#!/usr/bin/env node

/**
 * Vancy CLI — AI Career Consultant Agent & Skills Installer
 * Follows vespyr/bin/cli.js for harness configuration, interactive wizard,
 * symlink/copy installation, manifest pinning, and surgical uninstall.
 */

import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import readline from "node:readline";
import { fileURLToPath } from "node:url";

import {
  ADAPTERS as HARNESS_ADAPTERS,
  HARNESS_OPTIONS,
  REGISTRY as HARNESS_REGISTRY,
  getAdapter as getHarnessAdapter,
  getGlobalPath,
} from "./lib/harnesses/index.mjs";
import { createInstaller } from "./lib/installer.mjs";
import { createLinkOrCopy, handleConflict } from "./lib/link-utils.mjs";
import { log, logDry, logError, logWarn } from "./lib/logger.mjs";
import { R, resetRuntimeState, setState } from "./lib/state.mjs";
import { createUi } from "./lib/ui.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PKG_ROOT = path.resolve(__dirname, "..");
const AGENTS_SRC = path.join(PKG_ROOT, ".agents");
const SKILLS_SRC = path.join(AGENTS_SRC, "skills");
const AGENT_SRC = path.join(AGENTS_SRC, "agents", "career-consultant");
const IS_TTY = Boolean(process.stdout && process.stdout.isTTY);

const VERSION = (() => {
  try {
    return JSON.parse(fs.readFileSync(path.join(PKG_ROOT, "package.json"), "utf8")).version;
  } catch {
    return "0.1.0";
  }
})();

const ASCII_ART = `
 __  __                              
/\\ \\/\\ \\                             
\\ \\ \\ \\ \\     __      ___     ___    __  __  
 \\ \\ \\ \\ \\  /'__\`\\  /' _ \`\\  /'___\\ /\\ \\/\\ \\ 
  \\ \\ \\_/ \\/\\ \\L\\.\\_/\\ \\/\\ \\/\\ \\__/ \\ \\ \\_\\ \\
   \\ \`\\___/\\ \\__/.\\_\\ \\_\\ \\_\\ \\____\\ \\/\`____ \\
    \`\\/__/  \\/__/\\/_/\\/_/\\/_/\\/____/  \`/___/> \\
                                         /\\___/
                                         \\/__/`;

const wizardState = {};

const uiApi = createUi({
  VERSION,
  ASCII_ART,
  ADAPTERS: HARNESS_ADAPTERS,
  IS_TTY,
  wizardState,
});
const {
  printSummary,
  setupSignalHandler,
  teardownSignalHandler,
  clearScreen,
  printWizardSummary,
} = uiApi;

const installerApi = createInstaller({
  log,
  logDry,
  logWarn,
  logError,
  askChecklist,
  askSingleChoice,
  askQuestion,
  detectMethod,
  writeManifest,
  performGenerateManifest,
  removeStaleManifestFiles,
  detectInstalledHarnesses,
  detectState,
  backupExistingAgentsDir,
  setupSignalHandler,
  teardownSignalHandler,
  printSummary,
  clearScreen,
  printWizardSummary,
  wizardState,
  ASCII_ART,
  VERSION,
  AGENTS_SRC,
});

const {
  scaffoldArtifacts,
  backupExistingArtifactsDir,
  bootstrapRootDocs,
  writeVersionFile,
  getInstalledVersion,
  installHarnesses,
  uninstallHarnesses,
  surgicallyCleanupAgentsDir,
  removeDirIfEmpty,
  performFreshInstall,
  performUpdate,
  performGlobalInstall,
  performReconfigure,
  performUninstall,
  performForeignConflict,
  performRepair,
} = installerApi;

// ---------------------------------------------------------------------------
// Interactive prompts (matching vespyr/bin/cli.js)
// ---------------------------------------------------------------------------

function askChecklist(question, options, showBack = false, initialSelections = []) {
  return new Promise((resolve) => {
    const selected = options.map((o) => initialSelections.includes(o.id));
    let cursor = 0;
    const totalOptions = options.length + (showBack ? 1 : 0);

    const stdin = process.stdin;
    stdin.setRawMode(true);
    stdin.resume();
    stdin.setEncoding("utf8");

    function render() {
      clearScreen();
      log(ASCII_ART);
      printWizardSummary();
      process.stdout.write(`\n  ${question}\n`);
      process.stdout.write(`  \x1b[2m(Space to toggle, Enter to confirm)\x1b[0m\n\n`);
      process.stdout.write(`    \x1b[32m✔\x1b[0m Core Agent Directory [Mandatory]\n\n`);
      for (let i = 0; i < options.length; i++) {
        const pointer = i === cursor ? "\x1b[36m❯\x1b[0m" : " ";
        const check = selected[i] ? "\x1b[32m◉\x1b[0m" : "◯";
        process.stdout.write(`    ${pointer} ${check} ${options[i].label}\n`);
        process.stdout.write(`      \x1b[2m${options[i].description}\x1b[0m\n`);
      }
      if (showBack) {
        const pointer = cursor === options.length ? "\x1b[36m❯\x1b[0m" : " ";
        process.stdout.write(`\n    ${pointer} ← Back\n`);
      }
    }

    render();

    function onData(key) {
      if (key === "\u0003") {
        stdin.setRawMode(false);
        stdin.removeListener("data", onData);
        process.exit(130);
      }

      if (key === "\r" || key === "\n") {
        stdin.setRawMode(false);
        stdin.removeListener("data", onData);
        stdin.pause();
        if (showBack && cursor === options.length) {
          clearScreen();
          log(ASCII_ART);
          printWizardSummary();
          process.stdout.write("\n");
          resolve({ back: true });
          return;
        }
        const result = options.filter((_, i) => selected[i]).map((o) => o.id);
        wizardState.harnesses = result;
        clearScreen();
        log(ASCII_ART);
        printWizardSummary();
        process.stdout.write("\n");
        resolve(result);
        return;
      }

      if (key === " ") {
        if (cursor < options.length) {
          selected[cursor] = !selected[cursor];
        }
      }

      if (key === "\x1b[A") cursor = (cursor - 1 + totalOptions) % totalOptions;
      if (key === "\x1b[B") cursor = (cursor + 1) % totalOptions;

      render();
    }

    stdin.on("data", onData);
  });
}

function askSingleChoice(question, choices, initialIndex = 0) {
  return new Promise((resolve) => {
    let cursor =
      Number.isInteger(initialIndex) && initialIndex >= 0 && initialIndex < choices.length
        ? initialIndex
        : 0;

    const stdin = process.stdin;
    stdin.setRawMode(true);
    stdin.resume();
    stdin.setEncoding("utf8");

    function render() {
      clearScreen();
      log(ASCII_ART);
      printWizardSummary();
      process.stdout.write(`\n  ${question}\n`);
      process.stdout.write(`  \x1b[2m(Up/Down to navigate, Enter to confirm)\x1b[0m\n\n`);
      for (let i = 0; i < choices.length; i++) {
        const pointer = i === cursor ? "\x1b[36m❯\x1b[0m" : " ";
        process.stdout.write(`    ${pointer} ${choices[i]}\n`);
      }
    }

    render();

    function onData(key) {
      if (key === "\u0003") {
        stdin.setRawMode(false);
        stdin.removeListener("data", onData);
        process.exit(130);
      }

      if (key === "\r" || key === "\n") {
        stdin.setRawMode(false);
        stdin.removeListener("data", onData);
        stdin.pause();
        clearScreen();
        log(ASCII_ART);
        printWizardSummary();
        process.stdout.write(
          `\n  \x1b[32m✓\x1b[0m ${question.replace(":", "")}: \x1b[1m${choices[cursor]}\x1b[0m\n`,
        );
        resolve(cursor);
        return;
      }

      if (key === "\x1b[A") cursor = (cursor - 1 + choices.length) % choices.length;
      if (key === "\x1b[B") cursor = (cursor + 1) % choices.length;

      render();
    }

    stdin.on("data", onData);
  });
}

function askQuestion(question, defaultVal = "") {
  return new Promise((resolve) => {
    clearScreen();
    log(ASCII_ART);
    printWizardSummary();

    const display = defaultVal ? `${question} [${defaultVal}]` : question;
    const promptStr = `\n  ${display}: `;

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      terminal: true,
    });

    rl.question(promptStr, (answer) => {
      rl.close();
      const result = answer.trim() || defaultVal;
      resolve(result);
    });
  });
}

// ---------------------------------------------------------------------------
// State, harness, and manifest helpers (matching vespyr/bin/cli.js)
// ---------------------------------------------------------------------------

function detectState(targetDir) {
  const agentsPath = path.join(targetDir, ".agents");
  const versionPath = path.join(agentsPath, ".vancy-version");

  const agentsExists = fs.existsSync(agentsPath);

  if (agentsExists && fs.existsSync(versionPath)) {
    return "installed";
  }

  if (agentsExists) {
    if (isEmptyDir(agentsPath)) {
      return "fresh";
    }
    if (isVancyAgentsDir(agentsPath)) {
      return "repair";
    }
    return "foreign";
  }

  return "fresh";
}

function isVancyAgentsDir(agentsPath) {
  const markers = [
    ".vancy-manifest.json",
    "manifest.json",
    path.join("agents", "career-consultant.json"),
    path.join("agents", "career-consultant", "prompt.md"),
    path.join("skills", "cv-builder", "SKILL.md"),
  ];
  return markers.some((rel) => {
    try {
      return fs.existsSync(path.join(agentsPath, rel));
    } catch {
      return false;
    }
  });
}

function isEmptyDir(dirPath) {
  try {
    const entries = fs.readdirSync(dirPath).filter((f) => f !== ".DS_Store");
    return entries.length === 0;
  } catch {
    return false;
  }
}

function backupExistingAgentsDir(targetDir) {
  const agentsPath = path.join(targetDir, ".agents");
  const backupPath = path.join(targetDir, `.agents.backup.${Date.now()}`);
  if (R.dryRun) {
    logDry(`Would back up existing non-Vancy .agents/ to ${path.basename(backupPath)}`);
    return backupPath;
  }
  fs.renameSync(agentsPath, backupPath);
  return backupPath;
}

function detectInstalledHarnesses(targetDir, isGlobal) {
  const out = [];
  for (const adapter of HARNESS_ADAPTERS) {
    let paths = [];
    try {
      paths = adapter.detectPaths({ targetDir }) || [];
    } catch {
      paths = [];
    }
    const found = paths.some((relOrAbs) => {
      const check = isGlobal ? getGlobalPath(adapter.id) : relOrAbs;
      if (!check) return false;
      try {
        fs.lstatSync(check);
        return true;
      } catch {
        return false;
      }
    });
    if (found) out.push(adapter.id);
  }
  return out;
}

function detectMethod(targetDir, isGlobal) {
  const checkPaths = HARNESS_ADAPTERS.flatMap((a) => {
    let probes = [];
    try {
      probes = a.methodProbePaths({ targetDir }) || [];
    } catch {
      probes = [];
    }
    return probes.map((p2) => (isGlobal ? getGlobalPath(a.id) : p2)).filter(Boolean);
  });

  let sawReal = false;
  for (const p of checkPaths) {
    let stat;
    try {
      stat = fs.lstatSync(p);
    } catch {
      continue;
    }
    if (stat.isSymbolicLink()) return "symlink";
    sawReal = true;
  }
  if (sawReal) return "copy";
  return "symlink";
}

const MANIFEST_EXCLUDE_FILES = new Set([".DS_Store", "manifest.json"]);
const MANIFEST_EXCLUDE_DIRS = new Set(["node_modules", ".git", ".bak", "__pycache__", "autoharness"]);

function isBackupLitter(name) {
  return name.includes(".bak-") || name.includes(".backup.") || name === ".bak";
}

function buildSourceManifest(srcDir) {
  const manifest = [];
  function walk(d, rel) {
    let entries;
    try {
      entries = fs.readdirSync(d, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (MANIFEST_EXCLUDE_FILES.has(entry.name)) continue;
      if (MANIFEST_EXCLUDE_DIRS.has(entry.name)) continue;
      if (isBackupLitter(entry.name)) continue;
      if (entry.isSymbolicLink()) continue;
      const relPath = rel ? `${rel}/${entry.name}` : entry.name;
      if (entry.isDirectory()) {
        walk(path.join(d, entry.name), relPath);
      } else {
        manifest.push(relPath);
      }
    }
  }
  walk(srcDir, "");
  return manifest;
}

function writeManifest(targetDir) {
  if (R.dryRun) {
    logDry(`Would write manifest file in ${path.join(targetDir, ".agents")}`);
    return;
  }
  const manifest = buildSourceManifest(AGENTS_SRC);
  fs.writeFileSync(
    path.join(targetDir, ".agents", ".vancy-manifest.json"),
    JSON.stringify(manifest),
  );
}

function backupAndRemoveFile(target, agentsTarget, bakDir) {
  const rel = path.relative(agentsTarget, target);
  const today = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  const relDir = path.dirname(rel);
  const bakDstDir = path.join(bakDir, relDir);
  fs.mkdirSync(bakDstDir, { recursive: true });
  const baseName = path.basename(rel);
  let bakPath = path.join(bakDstDir, `${baseName}.bak-${today}`);
  let n = 1;
  while (fs.existsSync(bakPath)) {
    bakPath = path.join(bakDstDir, `${baseName}.bak-${today}-${n++}`);
    if (n > 100) break;
  }
  try {
    fs.copyFileSync(target, bakPath);
  } catch {}
  fs.rmSync(target, { recursive: true, force: true });
}

function removeStaleManifestFiles(targetDir) {
  const agentsTarget = path.join(targetDir, ".agents");
  if (!fs.existsSync(agentsTarget)) return;
  const bakDir = path.join(agentsTarget, ".bak");

  let prevList = null;
  const hashedPath = path.join(agentsTarget, "manifest.json");
  try {
    if (fs.existsSync(hashedPath)) {
      const hashed = JSON.parse(fs.readFileSync(hashedPath, "utf8"));
      if (hashed && typeof hashed.files === "object") {
        prevList = Object.keys(hashed.files);
      }
    }
  } catch {}
  if (!prevList) {
    const manifestPath = path.join(agentsTarget, ".vancy-manifest.json");
    if (fs.existsSync(manifestPath)) {
      try {
        const parsed = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
        if (Array.isArray(parsed)) prevList = parsed;
      } catch {}
    }
  }

  if (!Array.isArray(prevList)) return;

  const next = buildSourceManifest(AGENTS_SRC);
  const nextSet = new Set(next);

  for (const rel of prevList) {
    if (nextSet.has(rel)) continue;
    if (rel === ".vancy-version" || rel === ".vancy-manifest.json") continue;
    const base = rel.split("/").pop();
    if (MANIFEST_EXCLUDE_FILES.has(base) || isBackupLitter(base)) continue;
    const target = path.resolve(agentsTarget, rel);
    if (!target.startsWith(agentsTarget + path.sep)) continue;
    let st;
    try {
      st = fs.lstatSync(target);
    } catch {
      continue;
    }

    try {
      if (st.isFile()) {
        backupAndRemoveFile(target, agentsTarget, bakDir);
      } else {
        fs.rmSync(target, { recursive: true, force: true });
      }
    } catch {}
  }
}

function generateManifestData(targetDir) {
  const agentsTarget = path.join(targetDir, ".agents");
  if (!fs.existsSync(agentsTarget)) {
    throw new Error(".agents directory not found");
  }
  const files = {};
  function hashFile(filePath) {
    const st = fs.lstatSync(filePath);
    if (st.isSymbolicLink()) {
      throw new Error(`refusing to hash symlink: ${filePath}`);
    }
    const buffer = fs.readFileSync(filePath);
    return crypto.createHash("sha256").update(buffer).digest("hex");
  }
  function walk(dir, rel) {
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const ent of entries) {
      if (MANIFEST_EXCLUDE_FILES.has(ent.name)) continue;
      if (MANIFEST_EXCLUDE_DIRS.has(ent.name)) continue;
      if (isBackupLitter(ent.name)) continue;
      const full = path.join(dir, ent.name);
      const relPath = rel ? `${rel}/${ent.name}` : ent.name;
      if (ent.isSymbolicLink()) continue;
      if (ent.isDirectory()) {
        walk(full, relPath);
      } else {
        try {
          files[relPath] = hashFile(full);
        } catch {}
      }
    }
  }
  walk(agentsTarget, "");
  return {
    version: VERSION,
    generated_at: new Date().toISOString(),
    file_count: Object.keys(files).length,
    files,
  };
}

function performGenerateManifest(targetDir, flags = {}) {
  const manifestPath = path.join(targetDir, ".agents", "manifest.json");
  if (R.dryRun) {
    logDry(`Would refresh .vancy-manifest.json and write manifest to ${manifestPath}`);
    return;
  }
  try {
    writeManifest(targetDir);
  } catch (e) {
    logWarn(`Could not refresh .vancy-manifest.json before hashing: ${e.message}`);
  }
  const manifestData = generateManifestData(targetDir);
  fs.writeFileSync(manifestPath, JSON.stringify(manifestData, null, 2) + "\n", "utf8");
  if (flags.json) {
    console.log(
      JSON.stringify({ ok: true, manifest: manifestPath, file_count: manifestData.file_count }),
    );
  } else {
    log(`[OK] Generated manifest at ${manifestPath} (${manifestData.file_count} files).`);
  }
}

function performVerify(targetDir, flags = {}) {
  const agentsTarget = path.join(targetDir, ".agents");
  const manifestPath = path.join(agentsTarget, "manifest.json");
  const jsonMode = Boolean(flags.json);

  const failClosed = (message) => {
    if (jsonMode) {
      process.stdout.write(JSON.stringify({ exit: 2, fault: message }) + "\n");
    } else {
      console.error(`FAIL-CLOSED: ${message}`);
    }
    process.exitCode = 2;
  };

  if (!fs.existsSync(agentsTarget)) {
    failClosed(".agents directory not found");
    return;
  }

  if (!fs.existsSync(manifestPath)) {
    failClosed(
      "FAULT-5: manifest missing (.agents/manifest.json) — refusing to verify without a pinned baseline. Create one explicitly via `vancy manifest`.",
    );
    return;
  }

  let manifest;
  try {
    manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  } catch (e) {
    failClosed(`FAULT-4: Corrupt manifest (${e.message})`);
    return;
  }

  if (!manifest || typeof manifest.files !== "object") {
    failClosed("FAULT-4: Invalid manifest schema");
    return;
  }

  const mismatches = [];
  const missing = [];
  const extra = [];
  let verifiedCount = 0;

  for (const [relPath, expectedHash] of Object.entries(manifest.files)) {
    const fullPath = path.resolve(agentsTarget, relPath);
    if (!fullPath.startsWith(agentsTarget + path.sep) && fullPath !== agentsTarget) {
      mismatches.push({ path: relPath, expected: expectedHash, actual: "path-escape" });
      continue;
    }
    let st;
    try {
      st = fs.lstatSync(fullPath);
    } catch {
      missing.push(relPath);
      continue;
    }
    if (st.isSymbolicLink()) {
      extra.push({
        path: relPath,
        detail: "undeclared symlink at pinned path (forward-walk guard)",
      });
      continue;
    }
    if (!st.isFile()) {
      missing.push(relPath);
      continue;
    }
    let buffer;
    try {
      buffer = fs.readFileSync(fullPath);
    } catch (e) {
      mismatches.push({
        path: relPath,
        expected: expectedHash,
        actual: `unreadable:${e.code || e.message}`,
      });
      continue;
    }
    const actualHash = crypto.createHash("sha256").update(buffer).digest("hex");
    if (actualHash !== expectedHash) {
      mismatches.push({ path: relPath, expected: expectedHash, actual: actualHash });
    } else {
      verifiedCount++;
    }
  }

  let walkFault = null;
  const walkExtra = (dir, rel) => {
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch (e) {
      walkFault = `unreadable directory during verification: ${rel || ".agents/"} (${e.code || e.message})`;
      return;
    }
    for (const ent of entries) {
      const full = path.join(dir, ent.name);
      const relPath = rel ? `${rel}/${ent.name}` : ent.name;
      if (ent.isSymbolicLink()) {
        extra.push({
          path: relPath,
          detail: "undeclared symlink inside .agents/ (anchor-swap guard)",
        });
        continue;
      }
      if (MANIFEST_EXCLUDE_FILES.has(ent.name)) continue;
      if (MANIFEST_EXCLUDE_DIRS.has(ent.name)) continue;
      if (isBackupLitter(ent.name)) continue;
      if (ent.isDirectory()) {
        walkExtra(full, relPath);
      } else if (!Object.prototype.hasOwnProperty.call(manifest.files, relPath)) {
        extra.push({ path: relPath, detail: "not in manifest" });
      }
    }
  };
  walkExtra(agentsTarget, "");

  if (walkFault) {
    failClosed(walkFault);
    return;
  }

  const isClean = mismatches.length === 0 && missing.length === 0 && extra.length === 0;

  if (jsonMode) {
    process.stdout.write(
      JSON.stringify(
        {
          exit: isClean ? 0 : 1,
          verified: verifiedCount,
          missing,
          mismatches,
          extra,
        },
        null,
        2,
      ) + "\n",
    );
  } else if (isClean) {
    log(`[OK] All ${verifiedCount} files verified against manifest.`);
  } else {
    if (missing.length > 0) {
      console.error(`[FAIL] ${missing.length} missing file(s):`);
      for (const m of missing) console.error(`  - missing: ${m}`);
    }
    if (mismatches.length > 0) {
      console.error(`[FAIL] ${mismatches.length} hash mismatch(es):`);
      for (const m of mismatches) console.error(`  - tampered/modified: ${m.path}`);
    }
    if (extra.length > 0) {
      console.error(`[FAIL] ${extra.length} file(s) not in manifest:`);
      for (const m of extra) {
        console.error(`  - unplanted/unlisted: ${m.path}${m.detail ? ` (${m.detail})` : ""}`);
      }
    }
  }

  process.exitCode = isClean ? 0 : 1;
}

// ---------------------------------------------------------------------------
// List command & Action menu
// ---------------------------------------------------------------------------

function readSkillSummary(skillDir) {
  const mdPath = path.join(skillDir, "SKILL.md");
  try {
    const raw = fs.readFileSync(mdPath, "utf8");
    const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    if (!m) return "";
    const desc = m[1].match(/^description:\s*(.+)$/m);
    return desc ? desc[1].trim().replace(/^["']|["']$/g, "") : "";
  } catch {
    return "";
  }
}

function listAvailableSkills() {
  if (!fs.existsSync(SKILLS_SRC)) return [];
  return fs
    .readdirSync(SKILLS_SRC, { withFileTypes: true })
    .filter((d) => d.isDirectory() && fs.existsSync(path.join(SKILLS_SRC, d.name, "SKILL.md")))
    .map((d) => d.name)
    .sort();
}

function performList() {
  const skills = listAvailableSkills();
  log(`\nvancy v${VERSION}\n`);
  log(`Core Agent Directory (.agents/ — always installed):`);
  const agentJsonPath = path.join(AGENTS_SRC, "agents", "career-consultant.json");
  if (fs.existsSync(agentJsonPath)) {
    try {
      const meta = JSON.parse(fs.readFileSync(agentJsonPath, "utf8"));
      log(`  Agent: ${meta.name.padEnd(26)} ${meta.description}`);
    } catch {
      log(`  Agent: career-consultant`);
    }
  }
  log(`\nSkills (${skills.length}):`);
  for (const name of skills) {
    const summary = readSkillSummary(path.join(SKILLS_SRC, name));
    const short = summary.length > 78 ? `${summary.slice(0, 75)}...` : summary;
    log(`  ${name.padEnd(30)} ${short}`);
  }
  log(`\nHarness Integrations (--harness <names>):`);
  for (const h of HARNESS_OPTIONS) {
    log(`  ${h.id.padEnd(14)} ${h.label.padEnd(18)} ${h.description}`);
  }
  log("");
}

async function showActionMenu(targetDir, flags) {
  log(`\n============================================================`);
  log(`   VANCY v${VERSION} — Career Consultant CLI`);
  log(`============================================================`);
  log(`Vancy is already configured in this directory.\n`);

  if (flags.yes) {
    await performUpdate(targetDir, flags);
    return;
  }

  const choice = await askSingleChoice("Select an action:", [
    "Update Vancy (Sync latest agent prompts, workflow, and skills)",
    "Reconfigure (Re-run interactive setup / add or remove harnesses)",
    "Uninstall Vancy (Cleanly remove all Vancy folders and files)",
  ]);

  if (choice === 0) {
    await performUpdate(targetDir, flags);
  } else if (choice === 1) {
    await performReconfigure(targetDir, flags);
  } else if (choice === 2) {
    if (!flags.yes) {
      const ok = await askSingleChoice(`Uninstall Vancy from ${targetDir}?`, [
        "Yes, uninstall (core files removed, artifacts/ preserved)",
        "Cancel (keep everything as-is)",
      ]);
      if (ok !== 0) {
        log("  Uninstall cancelled.\n");
        return;
      }
    }
    await performUninstall(targetDir);
  }
}

// ---------------------------------------------------------------------------
// Argument parsing & help
// ---------------------------------------------------------------------------

function parseFlags(argv) {
  const args = argv.slice(2);
  const flags = {
    dryRun: false,
    yes: false,
    target: null,
    harnesses: [],
    method: null,
    noArtifacts: false,
    version: false,
    help: false,
    verify: false,
    manifest: false,
    uninstall: false,
    reconfigure: false,
    list: false,
    json: false,
    command: null,
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "init" || arg === "install") {
      flags.command = "init";
    } else if (arg === "update") {
      flags.command = "update";
    } else if (arg === "reconfigure") {
      flags.reconfigure = true;
      flags.command = "reconfigure";
    } else if (arg === "uninstall" || arg === "remove") {
      flags.uninstall = true;
      flags.command = "uninstall";
    } else if (arg === "verify" || arg === "--verify") {
      flags.verify = true;
      flags.command = "verify";
    } else if (arg === "manifest" || arg === "--manifest") {
      flags.manifest = true;
      flags.command = "manifest";
    } else if (arg === "list" || arg === "--list") {
      flags.list = true;
      flags.command = "list";
    } else if (arg === "--json") {
      flags.json = true;
    } else if (arg === "--dry-run") {
      flags.dryRun = true;
    } else if (arg === "--yes" || arg === "-y") {
      flags.yes = true;
    } else if (arg === "--copy") {
      flags.method = "copy";
    } else if (arg === "--symlink") {
      flags.method = "symlink";
    } else if (arg === "--method") {
      const val = args[++i];
      if (val !== "symlink" && val !== "copy") {
        console.error(`Invalid --method value: ${val}. Expected "symlink" or "copy".`);
        process.exit(2);
      }
      flags.method = val;
    } else if (arg === "--no-artifacts") {
      flags.noArtifacts = true;
    } else if (arg === "--target" || arg === "-t") {
      const val = args[++i];
      if (val === undefined || val.startsWith("-")) {
        console.error("Missing value for flag: --target");
        process.exit(2);
      }
      flags.target = val;
    } else if (arg === "--harness" || arg === "-H") {
      const val = args[++i];
      if (val === undefined || val.startsWith("-")) {
        console.error("Missing value for flag: --harness");
        process.exit(2);
      }
      const rawItems = val
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const resolved = [];
      for (const h of rawItems) {
        if (h === "all") {
          for (const opt of HARNESS_OPTIONS) {
            if (!resolved.includes(opt.id)) resolved.push(opt.id);
          }
          continue;
        }
        const adapter = getHarnessAdapter(h);
        if (!adapter) {
          console.error(
            `Unknown harness: ${h}. Available: ${HARNESS_OPTIONS.map((o) => o.id).join(", ")}`,
          );
          process.exit(2);
        }
        if (adapter.dormant) {
          console.error(
            `Harness "${h}" is dormant in this release (cleanup-only, no install path). Available: ${HARNESS_OPTIONS.map((o) => o.id).join(", ")}`,
          );
          process.exit(2);
        }
        if (!resolved.includes(adapter.id)) resolved.push(adapter.id);
      }
      flags.harnesses = resolved;
    } else if (arg === "--version" || arg === "-v") {
      flags.version = true;
    } else if (arg === "--help" || arg === "-h" || arg === "help") {
      flags.help = true;
    } else {
      console.error(`Unknown flag: ${arg}`);
      process.exit(2);
    }
  }

  return flags;
}

const SUBCOMMAND_HELPS = {
  init: `vancy init — Fresh install into target workspace

Usage: npx vancy init [options]

Options:
  --target <path>       Target directory (default: current directory)
  --yes, -y             Skip prompts, use defaults
  --harness <names>     Pre-select harnesses (opencode,claude,github,kiro or all)
  --symlink / --copy    Harness link method (.agents/ core is always copied)
  --no-artifacts        Do not scaffold artifacts/{input,output}/
  --dry-run             Preview installation without creating files
  --help, -h            Show this help message
`,
  update: `vancy update — Update an existing Vancy installation

Usage: npx vancy update [options]

Options:
  --target <path>       Target directory with existing .agents/ (default: current directory)
  --yes, -y             Non-interactive update
  --dry-run             Preview changes without modifying files
  --help, -h            Show this help message
`,
  reconfigure: `vancy reconfigure — Reconfigure harness integrations and link method

Usage: npx vancy reconfigure [options]

Options:
  --target <path>       Target directory (default: current directory)
  --harness <names>     Update harness selection (opencode,claude,github,kiro)
  --symlink / --copy    Harness link method (.agents/ core is always copied)
  --yes, -y             Non-interactive reconfigure
  --help, -h            Show this help message
`,
  uninstall: `vancy uninstall — Remove Vancy core and harness files safely

Usage: npx vancy uninstall [options]

Options:
  --target <path>       Target directory (default: current directory)
  --yes, -y             Confirm uninstall without prompting
  --help, -h            Show this help message
`,
  verify: `vancy verify — Check file integrity against pinned manifest

Usage: npx vancy verify [options]

Options:
  --target <path>       Target directory (default: current directory)
  --json                Output machine-readable JSON verification result
  --help, -h            Show this help message
`,
  manifest: `vancy manifest — Generate or regenerate workspace checksums manifest

Usage: npx vancy manifest [options]

Options:
  --target <path>       Target directory (default: current directory)
  --json                Output manifest status as JSON
  --help, -h            Show this help message
`,
};

// ---------------------------------------------------------------------------
// Main entry
// ---------------------------------------------------------------------------

async function main() {
  resetRuntimeState();
  const flags = parseFlags(process.argv);
  setState({ dryRun: flags.dryRun });

  if (flags.version) {
    console.log(VERSION);
    process.exit(0);
  }

  if (flags.help) {
    if (flags.command && SUBCOMMAND_HELPS[flags.command]) {
      console.log(SUBCOMMAND_HELPS[flags.command]);
      process.exit(0);
    }
    console.log(`
vancy v${VERSION} — Career Consultant Agent & Skills Installer

Usage: npx vancy [command] [options]

Commands:
  init                 Fresh install into --target (backs up a non-Vancy .agents/)
  update               Update an existing install (errors on fresh directories)
  reconfigure          Re-run setup on an existing install (add or remove harnesses)
  uninstall            Remove Vancy core and harness files (artifacts/ preserved)
  verify               Verify integrity of .agents/ against pinned manifest
  manifest             Generate .agents/manifest.json checksums file
  list                 List bundled agent, skills, and supported harnesses

Options:
  --dry-run            Preview all actions without making changes
  --yes, -y            Skip all interactive prompts, use defaults
  --target, -t <path>  Specify installation directory
  --harness, -H <ids>  Pre-select harness(es), comma-separated (${HARNESS_OPTIONS.map((o) => o.id).join(", ")}, or all)
  --symlink            Link harness directories to .agents/ (default)
  --copy               Copy harness files instead of symlinking
  --no-artifacts       Skip scaffolding artifacts/{input,output}/
  --json               Output machine-readable JSON results (verify/manifest)
  --version, -v        Print version and exit
  --help, -h           Print usage and exit

Harnesses:
  Core (.agents/)      Always installed (.agents/agents/career-consultant + .agents/skills/*)
  opencode             .opencode -> .agents symlink/copy
  claude               .claude -> .agents symlink/copy + CLAUDE.md
  github               .github/copilot-instructions.md + .github/skills -> ../.agents/skills
  kiro                 .kiro/steering/ + .kiro/skills + .kiro/agents/career-consultant

Examples:
  npx vancy                                 Interactive install wizard
  npx vancy init --yes                      Fresh install with defaults (.agents/ core)
  npx vancy init --harness opencode,claude  Install core + OpenCode & Claude Code harnesses
  npx vancy reconfigure                     Interactive harness reconfiguration
  npx vancy update --yes                    Update existing install
  npx vancy verify                          Check integrity against manifest
  npx vancy uninstall                       Cleanly remove Vancy (preserves artifacts/)
`);
    process.exit(0);
  }

  if (flags.list) {
    performList();
    return;
  }

  const targetDir = flags.target ? path.resolve(flags.target) : process.cwd();

  if (flags.verify) {
    performVerify(targetDir, flags);
    return;
  }

  if (flags.manifest) {
    performGenerateManifest(targetDir, flags);
    return;
  }

  if (IS_TTY) log(ASCII_ART);

  const state = detectState(targetDir);

  if (flags.command === "init" && state === "installed") {
    log(`Already installed — refreshing via update path (idempotent re-init).`);
    try {
      await performUpdate(targetDir, flags);
    } catch (err) {
      logError(`Re-init refresh failed: ${err.message}`);
      process.exit(1);
    }
    try {
      if (typeof teardownSignalHandler === "function") teardownSignalHandler();
    } catch {}
    return;
  }

  if (flags.command === "update" && state === "fresh") {
    logError("Nothing to update — directory is fresh. Use `vancy init` first.");
    process.exit(2);
  }
  if (flags.command === "update" && state === "foreign") {
    logError(
      "No Vancy installation found — .agents/ belongs to another tool. Use `vancy init` to back it up and install, not `update`.",
    );
    process.exit(2);
  }
  if (flags.command === "reconfigure" && state !== "installed" && state !== "repair") {
    logError("Cannot reconfigure — no Vancy installation found. Use `vancy init` first.");
    process.exit(2);
  }

  try {
    if (flags.command === "init") {
      if (state === "foreign") {
        await performForeignConflict(targetDir, flags);
      } else if (state === "repair") {
        await performRepair(targetDir, flags);
      } else {
        log(`\n============================================================`);
        log(`   VANCY v${VERSION} — Career Consultant Installer`);
        log(`============================================================\n`);
        await performFreshInstall(targetDir, flags);
      }
    } else if (flags.command === "update") {
      await performUpdate(targetDir, flags);
    } else if (flags.command === "uninstall") {
      if (!flags.yes && (state === "installed" || state === "repair")) {
        if (!process.stdin.isTTY) {
          logError("Uninstall needs confirmation — re-run with --yes for non-interactive use.");
          process.exit(2);
        }
        const ok = await askSingleChoice(`Uninstall Vancy from ${targetDir}?`, [
          "Yes, uninstall (core files removed, artifacts/ preserved)",
          "Cancel (keep everything as-is)",
        ]);
        if (ok !== 0) {
          log("  Uninstall cancelled.\n");
          try {
            if (typeof teardownSignalHandler === "function") teardownSignalHandler();
          } catch {}
          return;
        }
      }
      await performUninstall(targetDir);
    } else if (flags.command === "reconfigure") {
      await performReconfigure(targetDir, flags);
    } else if (state === "installed") {
      await showActionMenu(targetDir, flags);
    } else if (state === "foreign") {
      await performForeignConflict(targetDir, flags);
    } else if (state === "repair") {
      await performRepair(targetDir, flags);
    } else {
      log(`\n============================================================`);
      log(`   VANCY v${VERSION} — Career Consultant Installer`);
      log(`============================================================\n`);
      await performFreshInstall(targetDir, flags);
    }
    try {
      if (typeof teardownSignalHandler === "function") teardownSignalHandler();
    } catch {}
  } catch (err) {
    if (err.code === "EACCES" || err.code === "EPERM") {
      logError(
        `Permission denied. Try running with appropriate privileges or check directory ownership.`,
      );
    } else if (err.code === "ENOSPC") {
      logError(`Not enough disk space to complete installation.`);
    } else if (err.code === "ENOENT") {
      logError(
        `The specified path does not exist. Create it first or choose a different directory.`,
      );
    } else {
      logError(`Installation failed: ${err.message}. Run with --dry-run to debug.`);
    }

    if (!R.dryRun && R.installed) {
      const agentsTarget = path.join(targetDir, ".agents");
      if (path.resolve(agentsTarget) !== path.resolve(AGENTS_SRC)) {
        try {
          fs.lstatSync(agentsTarget);
          fs.rmSync(agentsTarget, { recursive: true, force: true });
        } catch {}
      }
      for (const link of R.createdLinks) {
        try {
          fs.lstatSync(link);
          fs.unlinkSync(link);
        } catch {}
        try {
          const st = (() => {
            try {
              return fs.lstatSync(link);
            } catch {
              return null;
            }
          })();
          if (st && st.isDirectory() && !st.isSymbolicLink()) {
            fs.rmSync(link, { recursive: true, force: true });
          }
        } catch {}
      }
    }
    try {
      if (typeof teardownSignalHandler === "function") teardownSignalHandler();
    } catch {}
    try {
      process.stdin.setRawMode(false);
    } catch {}

    process.exit(1);
  }
}

const isMain =
  process.argv[1] &&
  (() => {
    try {
      return fs.realpathSync(process.argv[1]) === fs.realpathSync(__filename);
    } catch {
      return path.resolve(process.argv[1]) === __filename;
    }
  })();

if (isMain) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}

export {
  parseFlags,
  detectState,
  isVancyAgentsDir,
  backupExistingAgentsDir,
  backupExistingArtifactsDir,
  performForeignConflict,
  createLinkOrCopy,
  scaffoldArtifacts,
  bootstrapRootDocs,
  writeVersionFile,
  getInstalledVersion,
  printSummary,
  handleConflict,
  performUninstall,
  surgicallyCleanupAgentsDir,
  removeDirIfEmpty,
  uninstallHarnesses,
  performReconfigure,
  performUpdate,
  performGlobalInstall,
  detectInstalledHarnesses,
  detectMethod,
  buildSourceManifest,
  writeManifest,
  performGenerateManifest,
  removeStaleManifestFiles,
  performVerify,
  ASCII_ART,
  VERSION,
  HARNESS_OPTIONS,
};
