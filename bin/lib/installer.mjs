/**
 * Installer orchestration: fresh install, update, global install,
 * reconfigure, artifact scaffolding, harness dispatch, uninstall sweeps.
 * Follows vespyr/bin/lib/installer.js.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { R } from "./state.mjs";
import { handleConflict, createLinkOrCopy } from "./link-utils.mjs";
import {
  ADAPTERS as HARNESS_ADAPTERS,
  HARNESS_OPTIONS,
  REGISTRY as HARNESS_REGISTRY,
  getAdapter as getHarnessAdapter,
  getGlobalPath,
} from "./harnesses/index.mjs";

const ARTIFACTS_README = `# artifacts

Working folders for the career-consultant agent.

- \`input/\`  - put your source material here: current CV, LinkedIn export, job ads (paste into .txt or .md),
  notes, offer letters. The agent reads these and never edits them.
- \`output/\` - everything the agent produces lands here: job briefs, CVs, cover letters (.md + .docx),
  story banks, PM prep sheets, negotiation plans, and the application tracker CSV.

These folders hold personal data (and possibly referees' details). \`.gitignore\` in this folder
keeps them out of git; do not remove it.
`;

const ARTIFACTS_GITIGNORE = `# Personal job-search data: CVs, letters, referees, offers, tracker. Keep out of git.
*
!.gitignore
!README.md
`;

export function createInstaller(deps) {
  const {
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
  } = deps;

  function backupExistingArtifactsDir(targetDir) {
    const artifactsPath = path.join(targetDir, "artifacts");
    const backupPath = path.join(targetDir, `artifacts.backup.${Date.now()}`);
    if (R.dryRun) {
      logDry(`Would back up existing artifacts/ to ${path.basename(backupPath)}`);
      return backupPath;
    }
    fs.renameSync(artifactsPath, backupPath);
    return backupPath;
  }

  function scaffoldArtifacts(targetDir, mode = "fresh") {
    const artifactsDir = path.join(targetDir, "artifacts");

    if (mode === "fresh" && fs.existsSync(artifactsDir)) {
      // Ensure input/ and output/ exist inside existing artifacts/ without clobbering
      if (!R.dryRun) {
        fs.mkdirSync(path.join(artifactsDir, "input"), { recursive: true });
        fs.mkdirSync(path.join(artifactsDir, "output"), { recursive: true });
        if (!fs.existsSync(path.join(artifactsDir, ".gitignore"))) {
          fs.writeFileSync(path.join(artifactsDir, ".gitignore"), ARTIFACTS_GITIGNORE);
        }
        if (!fs.existsSync(path.join(artifactsDir, "README.md"))) {
          fs.writeFileSync(path.join(artifactsDir, "README.md"), ARTIFACTS_README);
        }
      }
      log("  Existing artifacts/ found (input/ and output/ verified).");
      return;
    }

    if (mode === "fresh-install" && fs.existsSync(artifactsDir)) {
      const backupPath = backupExistingArtifactsDir(targetDir);
      if (!R.dryRun) {
        log(`  Backed up existing artifacts/ to ${path.basename(backupPath)}`);
      }
    }

    if (R.dryRun) {
      logDry(`Would create artifacts/input and artifacts/output directory tree in ${targetDir}`);
      return;
    }

    fs.mkdirSync(path.join(artifactsDir, "input"), { recursive: true });
    fs.mkdirSync(path.join(artifactsDir, "output"), { recursive: true });

    const gitignorePath = path.join(artifactsDir, ".gitignore");
    const readmePath = path.join(artifactsDir, "README.md");
    if (mode !== "merge" || !fs.existsSync(gitignorePath)) {
      fs.writeFileSync(gitignorePath, ARTIFACTS_GITIGNORE);
    }
    if (mode !== "merge" || !fs.existsSync(readmePath)) {
      fs.writeFileSync(readmePath, ARTIFACTS_README);
    }

    log("  Scaffolded artifacts/input and artifacts/output directory tree.");
  }

  function bootstrapRootDocs(targetDir, projectName, selectedHarnesses) {
    const canonicalFile = fs.existsSync(
      path.join(targetDir, ".agents", "templates", "system", "AGENTS.md.canonical"),
    )
      ? path.join(targetDir, ".agents", "templates", "system", "AGENTS.md.canonical")
      : fs.existsSync(
          path.join(targetDir, ".agents", "templates", "system", "agent.md.canonical"),
        )
      ? path.join(targetDir, ".agents", "templates", "system", "agent.md.canonical")
      : fs.existsSync(
          path.join(AGENTS_SRC, "templates", "system", "AGENTS.md.canonical"),
        )
      ? path.join(AGENTS_SRC, "templates", "system", "AGENTS.md.canonical")
      : fs.existsSync(
          path.join(AGENTS_SRC, "templates", "system", "agent.md.canonical"),
        )
      ? path.join(AGENTS_SRC, "templates", "system", "agent.md.canonical")
      : path.join(AGENTS_SRC, "agents", "career-consultant", "prompt.md");

    const rawContent = fs.existsSync(canonicalFile)
      ? fs.readFileSync(canonicalFile, "utf8").replace(/\{Project Name\}/g, projectName)
      : "";

    const canonicalContent = rawContent
      ? `<!-- Vancy-managed — removed on uninstall -->\n` + rawContent
      : "";

    const agentsMd = canonicalContent;
    const agentMd = canonicalContent;
    const claudeMd = canonicalContent.replace(/\.agents\//g, ".claude/");

    const agentsPath = path.join(targetDir, "AGENTS.md");
    const agentPath = path.join(targetDir, "agent.md");

    if (R.dryRun) {
      if (!fs.existsSync(agentsPath)) logDry(`Would create AGENTS.md`);
      if (!fs.existsSync(agentPath)) logDry(`Would create agent.md`);
      if (selectedHarnesses.includes("claude")) logDry(`Would create CLAUDE.md`);
      return;
    }

    if (!fs.existsSync(agentsPath)) fs.writeFileSync(agentsPath, agentsMd);
    if (!fs.existsSync(agentPath)) fs.writeFileSync(agentPath, agentMd);

    if (selectedHarnesses.includes("claude")) {
      const claudePath = path.join(targetDir, "CLAUDE.md");
      if (!fs.existsSync(claudePath)) fs.writeFileSync(claudePath, claudeMd);
    }
  }

  function writeVersionFile(targetDir, extra = {}) {
    const versionPath = path.join(targetDir, ".agents", ".vancy-version");
    if (R.dryRun) {
      logDry(`Would write version file: ${versionPath}`);
      return;
    }
    const data = { version: VERSION, installed: new Date().toISOString(), ...extra };
    fs.writeFileSync(versionPath, JSON.stringify(data, null, 2));
  }

  function getInstalledVersion(targetDir) {
    const versionPath = path.join(targetDir, ".agents", ".vancy-version");
    if (!fs.existsSync(versionPath)) return null;
    try {
      const data = JSON.parse(fs.readFileSync(versionPath, "utf8"));
      return data.version || null;
    } catch {
      return null;
    }
  }

  async function installHarnesses(targetDir, selections, method) {
    const agentsTarget = path.join(targetDir, ".agents");
    const ctx = {
      targetDir,
      agentsTarget,
      method,
      selections,
      dryRun: R.dryRun,
      handleConflict,
      createLinkOrCopy,
      log,
      logDry,
      logWarn,
    };

    for (const id of selections) {
      const adapter = getHarnessAdapter(id);
      if (adapter && adapter.dormant) {
        throw new Error(
          `Harness "${id}" is dormant in this release (cleanup-only). Remove it from --harness or use uninstall to sweep a legacy install.`,
        );
      }
    }

    for (const adapter of HARNESS_ADAPTERS) {
      if (selections.includes(adapter.id)) {
        await adapter.install(ctx);
      }
    }

    for (const adapter of HARNESS_ADAPTERS) {
      if (typeof adapter.postInstall === "function") {
        await adapter.postInstall(selections, ctx);
      }
    }
  }

  function uninstallHarnesses(targetDir, harnesses, isGlobal) {
    const ctx = {
      targetDir,
      isGlobal,
      agentsSrc: AGENTS_SRC,
      surgicallyCleanupAgentsDir,
      removeDirIfEmpty,
    };
    for (const h of harnesses) {
      const adapter = getHarnessAdapter(h);
      if (adapter && typeof adapter.uninstall === "function") {
        adapter.uninstall(ctx);
      }
    }
  }

  function surgicallyCleanupAgentsDir(agentsTarget) {
    try {
      const stat = fs.lstatSync(agentsTarget);
      if (stat.isSymbolicLink()) {
        fs.unlinkSync(agentsTarget);
        return;
      }
    } catch {
      return;
    }

    if (!fs.existsSync(agentsTarget)) return;

    // Remove legacy singular symlink if present
    try {
      const singularLink = path.join(agentsTarget, "agent");
      if (fs.lstatSync(singularLink).isSymbolicLink()) {
        fs.unlinkSync(singularLink);
      }
    } catch {}

    // Delete core agents
    const agentsSrcDir = path.join(AGENTS_SRC, "agents");
    const targetAgentsDir = path.join(agentsTarget, "agents");
    if (fs.existsSync(agentsSrcDir) && fs.existsSync(targetAgentsDir)) {
      try {
        const coreAgents = fs.readdirSync(agentsSrcDir);
        for (const agent of coreAgents) {
          const targetAgentPath = path.join(targetAgentsDir, agent);
          try {
            fs.lstatSync(targetAgentPath);
          } catch {
            continue;
          }
          try {
            fs.rmSync(targetAgentPath, { recursive: true, force: true });
          } catch {}
        }
        removeDirIfEmpty(targetAgentsDir);
      } catch {}
    }

    // Delete core skills
    const skillsSrcDir = path.join(AGENTS_SRC, "skills");
    const targetSkillsDir = path.join(agentsTarget, "skills");
    if (fs.existsSync(skillsSrcDir) && fs.existsSync(targetSkillsDir)) {
      try {
        const coreSkills = fs.readdirSync(skillsSrcDir);
        for (const skill of coreSkills) {
          const targetSkillPath = path.join(targetSkillsDir, skill);
          try {
            fs.lstatSync(targetSkillPath);
          } catch {
            continue;
          }
          try {
            fs.rmSync(targetSkillPath, { recursive: true, force: true });
          } catch {}
        }
        removeDirIfEmpty(targetSkillsDir);
      } catch {}
    }

    // Delete core files
    const coreFiles = [
      ".vancy-version",
      ".vancy-manifest.json",
      "manifest.json",
      ".DS_Store",
    ];
    for (const file of coreFiles) {
      const filePath = path.join(agentsTarget, file);
      try {
        const st = fs.lstatSync(filePath);
        if (st.isDirectory() && !st.isSymbolicLink()) continue;
        fs.unlinkSync(filePath);
      } catch {}
    }

    // Sweep backup litter (*.bak-*, *.backup.*, .bak)
    try {
      const sweep = (dir) => {
        let entries;
        try {
          entries = fs.readdirSync(dir, { withFileTypes: true });
        } catch {
          return;
        }
        for (const ent of entries) {
          const full = path.join(dir, ent.name);
          if (ent.name === ".bak" && ent.isDirectory()) {
            try {
              fs.rmSync(full, { recursive: true, force: true });
            } catch {}
          } else if (ent.isDirectory() && !ent.isSymbolicLink()) {
            sweep(full);
          } else if (
            ent.isFile() &&
            (ent.name.includes(".bak-") || ent.name.includes(".backup."))
          ) {
            try {
              fs.unlinkSync(full);
            } catch {}
          }
        }
      };
      if (fs.existsSync(agentsTarget)) sweep(agentsTarget);
    } catch {}

    removeDirIfEmpty(agentsTarget);
  }

  function removeDirIfEmpty(dirPath) {
    try {
      if (fs.existsSync(dirPath)) {
        const stat = fs.lstatSync(dirPath);
        if (stat.isDirectory()) {
          const files = fs.readdirSync(dirPath).filter((f) => f !== ".DS_Store");
          if (files.length === 0) {
            fs.rmSync(dirPath, { recursive: true, force: true });
          }
        }
      }
    } catch {}
  }

  const COPY_EXCLUDE_NAMES = new Set([
    ".DS_Store",
    "__pycache__",
    ".bak",
    "autoharness",
  ]);

  function copyAgentsFilter(src) {
    const base = path.basename(src);
    if (COPY_EXCLUDE_NAMES.has(base)) return false;
    return true;
  }

  function backupCustomizedFiles(agentsTarget, sourceDir) {
    const today = new Date().toISOString().slice(0, 10).replace(/-/g, "");
    const bakDir = path.join(agentsTarget, ".bak");
    let backedUp = 0;
    const walk = (srcDir, relDir) => {
      const entries = fs.readdirSync(srcDir, { withFileTypes: true });
      for (const entry of entries) {
        if (COPY_EXCLUDE_NAMES.has(entry.name)) continue;
        const srcPath = path.join(srcDir, entry.name);
        const relPath = path.join(relDir, entry.name);
        const dstPath = path.join(agentsTarget, relPath);
        if (entry.isDirectory()) {
          walk(srcPath, relPath);
        } else if (entry.isFile()) {
          if (!fs.existsSync(dstPath)) continue;
          try {
            const incoming = fs.readFileSync(srcPath);
            const current = fs.readFileSync(dstPath);
            if (!incoming.equals(current)) {
              const bakDstDir = path.join(bakDir, relDir);
              fs.mkdirSync(bakDstDir, { recursive: true });
              let bakPath = path.join(bakDstDir, `${entry.name}.bak-${today}`);
              let n = 1;
              while (fs.existsSync(bakPath)) {
                try {
                  const prev = fs.readFileSync(bakPath);
                  if (prev.equals(current)) break;
                } catch {}
                bakPath = path.join(bakDstDir, `${entry.name}.bak-${today}-${n++}`);
                if (n > 100) break;
              }
              let needsWrite = true;
              try {
                if (fs.existsSync(bakPath) && fs.readFileSync(bakPath).equals(current)) {
                  needsWrite = false;
                }
              } catch {}
              if (needsWrite) {
                fs.copyFileSync(dstPath, bakPath);
                backedUp++;
              }
            }
          } catch {}
        }
      }
    };
    if (fs.existsSync(agentsTarget)) walk(sourceDir, "");
    return backedUp;
  }

  async function performFreshInstall(targetDir, flags) {
    log(`\n  Installing Vancy v${VERSION} to ${targetDir}...\n`);

    setupSignalHandler(targetDir);

    let selections = flags.harnesses.length > 0 ? flags.harnesses : [];
    let method = flags.method || "symlink";
    wizardState.scope = flags.global ? "Global" : "Project-level";
    wizardState.target = targetDir;
    wizardState.method = method;

    if (!flags.yes && process.stdin.isTTY) {
      let currentStep = 0;
      const steps = ["harnesses", "scope", "path", "method", "confirm"];

      while (currentStep < steps.length) {
        const step = steps[currentStep];

        if (step === "harnesses") {
          const harnessResult = await askChecklist(
            "Select harness integrations to configure:",
            HARNESS_OPTIONS,
            currentStep > 0,
            selections,
          );
          if (harnessResult.back) {
            continue;
          }
          selections = harnessResult;
          currentStep++;
        } else if (step === "scope") {
          const scopeChoice = await askSingleChoice("Select installation scope:", [
            "Project-level (Install in current workspace)",
            "Global (Install in user home/global environment paths)",
            "← Back",
          ]);
          if (scopeChoice === 2) {
            currentStep--;
          } else {
            wizardState.scope = scopeChoice === 0 ? "Project-level" : "Global";
            currentStep++;
          }
        } else if (step === "path") {
          if (wizardState.scope === "Global") {
            currentStep++;
            continue;
          }
          const pathChoice = await askSingleChoice("Select target directory:", [
            "Current directory (.)",
            "Custom path (Enter a custom folder path)",
            "← Back",
          ]);
          if (pathChoice === 2) {
            currentStep--;
          } else if (pathChoice === 1) {
            const customPath = await askQuestion("Enter custom path", ".");
            targetDir = path.resolve(customPath);
            wizardState.target = targetDir;
            currentStep++;
          } else {
            wizardState.target = targetDir;
            currentStep++;
          }
        } else if (step === "method") {
          const methodChoice = await askSingleChoice(
            "Select harness link method (.agents/ core is always copied):",
            [
              "Symlink (Recommended - harness links reference .agents/, updates propagate)",
              "Copy (Static copies of harness files; .agents/ core is still copied)",
              "← Back",
            ],
          );
          if (methodChoice === 2) {
            currentStep--;
            if (wizardState.scope === "Global") currentStep--;
          } else {
            method = methodChoice === 0 ? "symlink" : "copy";
            wizardState.method = method;
            currentStep++;
          }
        } else if (step === "confirm") {
          clearScreen();
          log(ASCII_ART);
          log(`\n  \x1b[2m── Configuration ──\x1b[0m`);
          log(
            `  Harnesses: ${selections.length ? selections.join(", ") : "core only"}`,
          );
          log(`  Scope:     ${wizardState.scope}`);
          log(`  Target:    ${wizardState.scope === "Global" ? os.homedir() : targetDir}`);
          log(`  Method:    ${method}`);
          log(`  \x1b[2m────────────────────\x1b[0m\n`);

          const confirmChoice = await askSingleChoice(
            "Proceed with installation?",
            ["Yes, install now", "← Back to edit", "Cancel installation"],
          );
          if (confirmChoice === 0) {
            break;
          } else if (confirmChoice === 1) {
            currentStep--;
          } else {
            log("\n  Installation cancelled.\n");
            process.exit(0);
          }
        }
      }
    }

    if (wizardState.scope === "Global" || flags.global) {
      await performGlobalInstall(selections, method, flags);
      try {
        if (typeof teardownSignalHandler === "function") teardownSignalHandler();
      } catch {}
      return;
    }

    if (!fs.existsSync(targetDir)) {
      if (R.dryRun) {
        logDry(`Would create directory: ${targetDir}`);
      } else {
        fs.mkdirSync(targetDir, { recursive: true });
      }
    }

    const agentsTarget = path.join(targetDir, ".agents");
    const isSelfSource = path.resolve(agentsTarget) === path.resolve(AGENTS_SRC);

    if (R.dryRun) {
      logDry(`Would copy .agents/ to ${agentsTarget}`);
    } else if (!isSelfSource) {
      if (!fs.existsSync(agentsTarget)) {
        fs.mkdirSync(agentsTarget, { recursive: true });
      } else {
        removeStaleManifestFiles(targetDir);
      }
      fs.cpSync(AGENTS_SRC, agentsTarget, {
          recursive: true,
          dereference: true,
          filter: copyAgentsFilter,
        });
      R.installed = true;
    }

    if (!isSelfSource) {
      writeVersionFile(targetDir);
      performGenerateManifest(targetDir, flags);
    }

    const projectName = path.basename(targetDir);
    if (!flags.noArtifacts) {
      scaffoldArtifacts(targetDir, "fresh");
    }
    bootstrapRootDocs(targetDir, projectName, selections);
    await installHarnesses(targetDir, selections, method);

    if (!R.dryRun) {
      printSummary(targetDir, { harnesses: selections });
    }
    try {
      if (typeof teardownSignalHandler === "function") teardownSignalHandler();
    } catch {}
  }

  async function performUpdate(targetDir, flags) {
    log(`\n  Updating Vancy in ${targetDir}...\n`);

    const agentsTarget = path.join(targetDir, ".agents");
    const isSelfSource = path.resolve(agentsTarget) === path.resolve(AGENTS_SRC);
    const prevVersion = getInstalledVersion(targetDir);

    if (R.dryRun) {
      logDry(`Would overwrite .agents/ with v${VERSION}`);
      logDry(`Would preserve artifacts/ directory`);
      logDry(`Would recompile all harness files`);
      return;
    }

    if (!fs.existsSync(agentsTarget)) {
      fs.mkdirSync(agentsTarget, { recursive: true });
    }

    if (!isSelfSource) {
      const customized = backupCustomizedFiles(agentsTarget, AGENTS_SRC);
      if (customized > 0) {
        log(`  Preserved ${customized} customized file(s) in .agents/.bak/`);
      }

      removeStaleManifestFiles(targetDir);
      fs.cpSync(AGENTS_SRC, agentsTarget, {
          recursive: true,
          dereference: true,
          filter: copyAgentsFilter,
        });

      writeVersionFile(targetDir);
      performGenerateManifest(targetDir, flags);
    }

    const installedHarnesses =
      flags.harnesses && flags.harnesses.length > 0
        ? flags.harnesses
        : detectInstalledHarnesses(targetDir, false);
    const method = flags.method || detectMethod(targetDir, false);

    const projectName = path.basename(targetDir);
    bootstrapRootDocs(targetDir, projectName, installedHarnesses);
    await installHarnesses(targetDir, installedHarnesses, method);

    log(`  Updated from v${prevVersion || "unknown"} to v${VERSION}`);
    log(`  Harnesses recompiled: ${installedHarnesses.join(", ") || "core only"}`);
    log(`  artifacts/ preserved.\n`);
  }

  async function performGlobalInstall(selections, method, flags = {}) {
    const globalAgentsDir = getGlobalPath("agents");
    const home = os.homedir();

    log(`\n  Installing Vancy v${VERSION} globally...\n`);

    if (R.dryRun) {
      logDry(`Would copy .agents/ to ${globalAgentsDir}`);
      for (const h of selections) {
        const gp = getGlobalPath(h);
        if (gp) logDry(`Would create ${h} link at ${gp}`);
      }
      return;
    }

    if (!fs.existsSync(globalAgentsDir)) {
      fs.mkdirSync(globalAgentsDir, { recursive: true });
    }
    fs.cpSync(AGENTS_SRC, globalAgentsDir, {
      recursive: true,
      dereference: true,
      filter: copyAgentsFilter,
    });

    writeVersionFile(home, { global: true });
    performGenerateManifest(home, flags);

    const globalCtx = {
      targetDir: home,
      agentsTarget: globalAgentsDir,
      method,
      selections,
      dryRun: R.dryRun,
      handleConflict,
      createLinkOrCopy,
      log,
      logDry,
      logWarn,
    };

    for (const h of selections) {
      const adapter = getHarnessAdapter(h);
      if (!adapter) continue;
      if (adapter.dormant) {
        logWarn(`Skipping dormant harness "${h}" for global install (cleanup-only).`);
        continue;
      }
      if (typeof adapter.install !== "function") continue;
      if (h === "opencode" || h === "claude") {
        const globalTarget = getGlobalPath(h);
        if (!globalTarget) continue;
        handleConflict(globalTarget, h, home, method);
        let needsCreate = false;
        try {
          fs.lstatSync(globalTarget);
        } catch {
          needsCreate = true;
        }
        if (needsCreate) {
          createLinkOrCopy(globalAgentsDir, globalTarget, "dir", method);
        }
      } else {
        try {
          await adapter.install(globalCtx);
        } catch (e) {
          logWarn(`Global harness "${h}" install failed: ${e.message}`);
        }
      }
    }

    for (const adapter of HARNESS_ADAPTERS) {
      if (typeof adapter.postInstall === "function") {
        try {
          await adapter.postInstall(selections, {
            ...globalCtx,
            agentsTarget: globalAgentsDir,
          });
        } catch {}
      }
    }

    log(`  Global install complete.`);
    log(`  .agents/ installed to: ${globalAgentsDir}`);
    log(`  Harnesses configured: ${selections.join(", ") || "core only"}\n`);
  }

  async function performReconfigure(targetDir, flags) {
    log(`\n  Reconfiguring Vancy in ${targetDir}...\n`);

    const agentsTarget = path.join(targetDir, ".agents");
    const isSelfSource = path.resolve(agentsTarget) === path.resolve(AGENTS_SRC);
    let isGlobal = false;
    const versionPath = path.join(agentsTarget, ".vancy-version");
    if (fs.existsSync(versionPath)) {
      try {
        const data = JSON.parse(fs.readFileSync(versionPath, "utf8"));
        isGlobal = Boolean(data.global);
      } catch {}
    }
    if (!isGlobal && targetDir === os.homedir()) {
      isGlobal = true;
    }

    const prevHarnesses = detectInstalledHarnesses(targetDir, isGlobal);
    let selections = flags.harnesses.length > 0 ? flags.harnesses : prevHarnesses;
    let method = flags.method || detectMethod(targetDir, isGlobal);

    if (!flags.yes && process.stdin.isTTY) {
      selections = await askChecklist(
        "Select harness integrations to configure:",
        HARNESS_OPTIONS,
        false,
        prevHarnesses,
      );

      const methodChoice = await askSingleChoice(
        "Select harness link method (.agents/ core is always copied):",
        [
          "Symlink (Recommended - harness links reference .agents/, updates propagate)",
          "Copy (Static copies of harness files; .agents/ core is still copied)",
        ],
      );
      method = methodChoice === 0 ? "symlink" : "copy";
    }

    // Uninstall deselected harnesses
    const removedHarnesses = prevHarnesses.filter((h) => !selections.includes(h));
    if (removedHarnesses.length > 0) {
      uninstallHarnesses(targetDir, removedHarnesses, isGlobal);
    }

    // Refresh .agents/ core
    if (!R.dryRun && !isGlobal && !isSelfSource) {
      try {
        backupCustomizedFiles(agentsTarget, AGENTS_SRC);
      } catch {}
      removeStaleManifestFiles(targetDir);
      try {
        fs.cpSync(AGENTS_SRC, agentsTarget, {
          recursive: true,
          dereference: true,
          filter: copyAgentsFilter,
        });
      } catch (e) {
        logWarn(`Core refresh during reconfigure failed: ${e.message}`);
      }
      writeVersionFile(targetDir);
      performGenerateManifest(targetDir, flags);
    }

    const projectName = path.basename(targetDir);
    bootstrapRootDocs(targetDir, projectName, selections);
    if (!selections.includes("claude")) {
      const claudePath = path.join(targetDir, "CLAUDE.md");
      try {
        if (fs.existsSync(claudePath)) {
          const content = fs.readFileSync(claudePath, "utf8");
          if (
            content.includes(".claude/") ||
            content.includes(".agents/") ||
            content.includes("Vancy-managed")
          ) {
            if (!R.dryRun) fs.unlinkSync(claudePath);
            else logDry(`Would remove stale CLAUDE.md (claude harness deselected)`);
          }
        }
      } catch {}
    }

    await installHarnesses(targetDir, selections, method);

    log(`  Reconfiguration complete.`);
    log(`  Harnesses: ${selections.join(", ") || "core only"}\n`);
  }

  async function performUninstall(targetDir) {
    log(`\n  Uninstalling Vancy from ${targetDir}...\n`);

    if (R.dryRun) {
      logDry(`Would delete .agents/`);
      logDry(`Would delete all harness symlinks`);
      logDry(`Would delete AGENTS.md, agent.md, CLAUDE.md`);
      logDry(`Would preserve artifacts/`);
      return;
    }

    const uninstallState = detectState(targetDir);
    if (uninstallState === "fresh") {
      log(`  Nothing to uninstall — no Vancy installation found in ${targetDir}.\n`);
      return;
    }
    if (uninstallState === "foreign") {
      logError(
        `Refusing to uninstall — .agents/ here belongs to another tool. Use \`init\` to resolve it first.`,
      );
      process.exitCode = 2;
      return;
    }

    const agentsTarget = path.join(targetDir, ".agents");
    const isSelfSource = path.resolve(agentsTarget) === path.resolve(AGENTS_SRC);
    let isGlobal = false;
    const versionPath = path.join(agentsTarget, ".vancy-version");
    if (fs.existsSync(versionPath)) {
      try {
        const data = JSON.parse(fs.readFileSync(versionPath, "utf8"));
        isGlobal = Boolean(data.global);
      } catch {}
    }
    if (!isGlobal && targetDir === os.homedir()) {
      isGlobal = true;
    }

    if (!isSelfSource) {
      surgicallyCleanupAgentsDir(agentsTarget);
    }

    const allHarnesses = Object.keys(HARNESS_REGISTRY);
    uninstallHarnesses(targetDir, allHarnesses, isGlobal);

    const filesToRemove = ["AGENTS.md", "agent.md", "CLAUDE.md"];
    for (const file of filesToRemove) {
      const filePath = path.join(targetDir, file);
      let managed = false;
      try {
        const st = fs.lstatSync(filePath);
        if (st.isFile() && !st.isSymbolicLink()) {
          const content = fs.readFileSync(filePath, "utf8");
          managed = content.includes("Vancy-managed") || content.includes(".agents/");
        }
      } catch {
        continue;
      }
      if (!managed) {
        log(`  Preserved non-Vancy ${file} (left in place).`);
        continue;
      }
      try {
        const stamp = new Date().toISOString().slice(0, 10).replace(/-/g, "");
        const bakPath = `${filePath}.uninstall-bak-${stamp}`;
        if (!fs.existsSync(bakPath)) {
          try {
            fs.copyFileSync(filePath, bakPath);
          } catch {}
        }
        fs.unlinkSync(filePath);
      } catch {}
    }

    log(`  Uninstall complete. artifacts/ preserved.\n`);
  }

  async function performForeignConflict(targetDir, flags, promptFn = askSingleChoice) {
    log(`\n============================================================`);
    log(`   VANCY v${VERSION} — Existing .agents/ Detected`);
    log(`============================================================`);
    log(`This directory already contains a .agents/ folder that was NOT`);
    log(`created by Vancy (no version marker or Vancy fingerprints).`);
    log(`Vancy will not merge into it silently.\n`);

    if (flags.yes || !process.stdin.isTTY) {
      const backupPath = backupExistingAgentsDir(targetDir);
      if (!R.dryRun) {
        log(`  Backed up existing .agents/ to ${path.basename(backupPath)}`);
      }
      await performFreshInstall(targetDir, flags);
      return;
    }

    const hasSkills = fs.existsSync(path.join(targetDir, ".agents", "skills"));
    const choices = hasSkills
      ? [
          "Merge (Keep existing files, add Vancy files alongside)",
          "Fresh install (Back up existing .agents/ and start fresh)",
          "Cancel (Keep everything as-is)",
        ]
      : [
          "Fresh install (Back up existing .agents/ and start fresh)",
          "Merge (Keep existing files, add Vancy files alongside)",
          "Cancel (Keep everything as-is)",
        ];

    const choice = await promptFn("Select an action:", choices);
    const selected = choices[choice];

    if (selected && selected.startsWith("Fresh install")) {
      const backupPath = backupExistingAgentsDir(targetDir);
      if (!R.dryRun) {
        log(`  Backed up existing .agents/ to ${path.basename(backupPath)}`);
      }
      await performFreshInstall(targetDir, flags);
    } else if (selected && selected.startsWith("Merge")) {
      log(`  Merging Vancy files alongside existing content (collisions backed up as *.bak-*).\n`);
      await performUpdate(targetDir, flags);
      if (!flags.noArtifacts) {
        scaffoldArtifacts(targetDir, "merge");
      }
    } else {
      log(`  Installation cancelled.\n`);
      process.exit(0);
    }
  }

  async function performRepair(targetDir, flags) {
    log(`\n============================================================`);
    log(`   VANCY v${VERSION} — Repairing Installation`);
    log(`============================================================`);
    log(`An existing .agents/ directory was found but the version marker`);
    log(`is missing. Syncing the latest files to repair it.\n`);
    await performUpdate(targetDir, flags);
  }

  return {
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
  };
}
