/**
 * GitHub Copilot harness adapter:
 * Emits .github/copilot-instructions.md (pointer stub to root AGENTS.md) and
 * .github/skills -> ../.agents/skills symlink (or copy).
 * Follows vespyr/bin/lib/harnesses/github-copilot.js.
 */
import fs from "node:fs";
import path from "node:path";
import { getGlobalPath } from "./index.mjs";

const COPILOT_INSTRUCTIONS_STUB = `<!-- Vancy-managed — removed on uninstall. Canonical source: ./AGENTS.md -->
# Career Consultant Skills

This project uses Career Consultant Skills (.agents/). Read \`AGENTS.md\` at the repository root as the instruction baseline before responding. Skills live in \`.agents/skills/\` (linked here as \`.github/skills/\`) and the custom agent lives in \`.agents/agents/\`.
`;

export default {
  id: "github",
  label: "GitHub Copilot",
  description: "scaffolds .github/copilot-instructions.md & .github/skills/ symlink",

  detectPaths({ targetDir }) {
    return [`${targetDir}/.github/copilot-instructions.md`, `${targetDir}/.github/skills`];
  },

  globalPath({ home }) {
    return path.join(home, ".config", "github-copilot");
  },

  methodProbePaths({ targetDir }) {
    return [`${targetDir}/.github/skills`];
  },

  install(ctx) {
    const { targetDir, agentsTarget, method, handleConflict, createLinkOrCopy, log } = ctx;
    const githubDir = path.join(targetDir, ".github");
    if (ctx.dryRun) {
      ctx.logDry(`Would create ${path.relative(targetDir, githubDir) || ".github"}/`);
    } else {
      fs.mkdirSync(githubDir, { recursive: true });
    }

    const instructionsPath = path.join(githubDir, "copilot-instructions.md");
    if (!fs.existsSync(instructionsPath)) {
      if (ctx.dryRun) {
        ctx.logDry(`Would create ${path.relative(targetDir, instructionsPath)}`);
      } else {
        fs.writeFileSync(instructionsPath, COPILOT_INSTRUCTIONS_STUB);
      }
    }

    const skillsPath = path.join(githubDir, "skills");
    handleConflict(skillsPath, ".github/skills", targetDir, method);
    if (!fs.existsSync(skillsPath)) {
      createLinkOrCopy(
        path.relative(githubDir, agentsTarget + path.sep + "skills"),
        skillsPath,
        "dir",
        method,
      );
    }
    if (ctx.dryRun) {
      ctx.logDry(
        "Would emit .github/copilot-instructions.md + .github/skills -> .agents/skills.",
      );
    } else {
      log(
        "  GitHub Copilot: emitted .github/copilot-instructions.md + .github/skills -> .agents/skills.",
      );
    }
  },

  summaryLines() {
    return [
      `    ✓ .github/copilot-instructions.md (GitHub Copilot project instructions)`,
      `    ✓ .github/skills -> .agents/skills (GitHub Copilot agent skills)`,
    ];
  },

  uninstall(ctx) {
    const { targetDir, isGlobal, removeDirIfEmpty } = ctx;
    const getPath = (localRel) =>
      isGlobal ? getGlobalPath("github") : path.join(targetDir, localRel);
    const githubTargetDir = getPath(".github");
    if (!fs.existsSync(githubTargetDir)) return;

    const skillsDir = path.join(githubTargetDir, "skills");
    try {
      const stat = fs.lstatSync(skillsDir);
      if (stat.isSymbolicLink()) {
        fs.unlinkSync(skillsDir);
      } else if (stat.isDirectory() && fs.readdirSync(skillsDir).length === 0) {
        fs.rmdirSync(skillsDir);
      }
    } catch {}

    const copilotInstructions = path.join(githubTargetDir, "copilot-instructions.md");
    try {
      const st = fs.lstatSync(copilotInstructions);
      if (st.isSymbolicLink()) {
        fs.unlinkSync(copilotInstructions);
      } else if (st.isFile()) {
        let owned = false;
        try {
          const text = fs.readFileSync(copilotInstructions, "utf8");
          owned =
            text.includes("Vancy-managed") ||
            text.includes("Career-Consultant-Skills managed");
        } catch {}
        if (owned) {
          fs.unlinkSync(copilotInstructions);
        }
      }
    } catch {}
    removeDirIfEmpty(githubTargetDir);
  },
};
