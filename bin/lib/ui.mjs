/**
 * CLI presentation layer: summary rendering, signal handling, screen helpers.
 * Follows vespyr/bin/lib/ui.js.
 */
import fs from "node:fs";
import path from "node:path";
import { R } from "./state.mjs";
import { log } from "./logger.mjs";
import { ADAPTERS as HARNESS_ADAPTERS } from "./harnesses/index.mjs";

export function createUi({
  VERSION,
  ASCII_ART,
  IS_TTY = Boolean(process.stdout && process.stdout.isTTY),
  wizardState = {},
}) {
  function printSummary(targetDir, selections) {
    const skillsDir = path.join(targetDir, ".agents", "skills");
    let count = 0;
    try {
      count = fs.existsSync(skillsDir)
        ? fs
            .readdirSync(skillsDir, { withFileTypes: true })
            .filter((d) => d.isDirectory()).length
        : 0;
    } catch {
      count = 0;
    }

    const createdLines = [];
    const exists = (rel) => {
      try {
        return fs.existsSync(path.join(targetDir, rel));
      } catch {
        return false;
      }
    };

    if (exists(".agents"))
      createdLines.push(`    ✓ .agents/                        (core agent & skills directory)`);
    if (exists("AGENTS.md"))
      createdLines.push(`    ✓ AGENTS.md                       (harness-agnostic guide)`);
    if (exists("agent.md"))
      createdLines.push(`    ✓ agent.md                        (agent quick reference)`);
    if (exists("artifacts"))
      createdLines.push(`    ✓ artifacts/                      (input + output directories)`);

    const lines = [
      `\n============================================================`,
      `   VANCY v${VERSION} — Installation Complete`,
      `============================================================`,
      ``,
      `  Target:       ${targetDir}`,
      `  Harnesses:    ${selections.harnesses.join(", ") || "core only"}`,
      ``,
      `  Created:`,
      ...createdLines,
    ];

    for (const adapter of HARNESS_ADAPTERS) {
      if (
        selections.harnesses.includes(adapter.id) &&
        typeof adapter.summaryLines === "function"
      ) {
        for (const line of adapter.summaryLines({ count })) lines.push(line);
      }
    }

    lines.push(
      ``,
      `  Next steps:`,
      `    1. Drop your CV, LinkedIn export, and job ads into artifacts/input/`,
      `    2. Ask the career-consultant agent (Simonek) to analyze a job ad or tailor your CV`,
      `    3. Find all generated briefs, CVs, letters, and tracker in artifacts/output/`,
      `============================================================`,
    );

    console.log(lines.join("\n"));
  }

  function setupSignalHandler(targetDir) {
    const existedBefore = (() => {
      try {
        fs.lstatSync(path.join(targetDir, ".agents"));
        return true;
      } catch {
        return false;
      }
    })();
    const handler = () => {
      const isFreshSession = !R.dryRun && R.installed && !existedBefore;
      if (isFreshSession) {
        try {
          fs.rmSync(path.join(targetDir, ".agents"), {
            recursive: true,
            force: true,
          });
        } catch {}
      }
      for (const link of R.createdLinks) {
        try {
          fs.lstatSync(link);
          fs.unlinkSync(link);
        } catch {}
      }
      try {
        for (const link of R.createdLinks) {
          try {
            const st = fs.lstatSync(link);
            if (st.isDirectory() && !st.isSymbolicLink()) {
              fs.rmSync(link, { recursive: true, force: true });
            }
          } catch {}
        }
      } catch {}
      if (isFreshSession) {
        console.log("\nInstallation cancelled. Partial fresh-install changes were removed.");
      } else {
        console.log(
          "\nInstallation cancelled. Existing files preserved; partial new files may remain — re-run to repair.",
        );
      }
      process.exit(130);
    };
    process.once("SIGINT", handler);
    setupSignalHandler._handler = handler;
    setupSignalHandler._target = targetDir;
  }

  function teardownSignalHandler() {
    if (setupSignalHandler._handler) {
      try {
        process.removeListener("SIGINT", setupSignalHandler._handler);
      } catch {}
      setupSignalHandler._handler = null;
    }
  }

  function clearScreen() {
    if (IS_TTY) process.stdout.write("\x1b[2J\x1b[H");
  }

  function printWizardSummary() {
    const lines = [];
    if (wizardState.harnesses !== undefined) {
      lines.push(
        `  Harnesses: ${wizardState.harnesses.length ? wizardState.harnesses.join(", ") : "core only"}`,
      );
    }
    if (wizardState.scope !== undefined) {
      lines.push(`  Scope:     ${wizardState.scope}`);
    }
    if (wizardState.target !== undefined) {
      lines.push(`  Target:    ${wizardState.target}`);
    }
    if (wizardState.method !== undefined) {
      lines.push(`  Method:    ${wizardState.method}`);
    }
    if (lines.length > 0) {
      process.stdout.write(`\n  \x1b[2m── Current Selections ──\x1b[0m\n`);
      lines.forEach((l) => process.stdout.write(l + "\n"));
      process.stdout.write(`  \x1b[2m────────────────────────\x1b[0m\n`);
    }
  }

  return {
    printSummary,
    setupSignalHandler,
    teardownSignalHandler,
    clearScreen,
    printWizardSummary,
  };
}

