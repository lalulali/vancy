/**
 * Claude Code harness adapter — .claude -> .agents symlink (+ CLAUDE.md doc
 * generated separately by bootstrapRootDocs in the installer layer).
 * Follows vespyr/bin/lib/harnesses/claude-code.js.
 */
import fs from "node:fs";
import path from "node:path";
import { getGlobalPath } from "./index.mjs";

export default {
  id: "claude",
  label: "Claude Code",
  description: "scaffolds .claude -> .agents symlink + CLAUDE.md",

  detectPaths({ targetDir }) {
    return [`${targetDir}/.claude`];
  },

  globalPath({ home }) {
    return `${home}/.claude`;
  },

  methodProbePaths({ targetDir }) {
    return [`${targetDir}/.claude`];
  },

  install(ctx) {
    const { targetDir, agentsTarget, method, handleConflict, createLinkOrCopy } = ctx;
    const linkPath = path.join(targetDir, ".claude");
    handleConflict(linkPath, ".claude", targetDir, method);
    if (!fs.existsSync(linkPath)) {
      createLinkOrCopy(
        path.relative(targetDir, agentsTarget),
        linkPath,
        "dir",
        method,
      );
    }
  },

  summaryLines() {
    return [
      `    ✓ .claude -> .agents              (Claude Code harness)`,
      `    ✓ CLAUDE.md                       (Claude Code project memory)`,
    ];
  },

  uninstall(ctx) {
    const { targetDir, isGlobal, surgicallyCleanupAgentsDir } = ctx;
    const claudePath = isGlobal ? getGlobalPath("claude") : path.join(targetDir, ".claude");
    try {
      const stat = fs.lstatSync(claudePath);
      if (stat.isSymbolicLink()) {
        fs.unlinkSync(claudePath);
        return;
      }
    } catch {
      return;
    }
    surgicallyCleanupAgentsDir(claudePath);
  },
};
