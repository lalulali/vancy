/**
 * Cursor harness adapter — DORMANT (cleanup-only, follows vespyr/bin/lib/harnesses/cursor.js).
 * Note: Cursor natively discovers .agents/skills/ and root AGENTS.md.
 */
import fs from "node:fs";
import path from "node:path";
import { getGlobalPath } from "./index.mjs";

export default {
  id: "cursor",
  label: "Cursor Rules",
  description: "scaffolds .cursor/rules/*.mdc rules with metadata",
  dormant: true,
  legacyCleanupOnly: true,

  detectPaths({ targetDir }) {
    return [`${targetDir}/.cursor/rules`, `${targetDir}/.cursor/skills`];
  },

  globalPath({ home, platform }) {
    return platform === "darwin"
      ? path.join(home, "Library", "Application Support", "Cursor", "User", "globalRules")
      : path.join(home, ".config", "Cursor", "User", "globalRules");
  },

  methodProbePaths({ targetDir } = {}) {
    const base = targetDir || process.cwd();
    return [`${base}/.cursor/rules`, `${base}/.cursor/skills`];
  },

  uninstall(ctx) {
    const { targetDir, isGlobal, agentsSrc, removeDirIfEmpty } = ctx;
    const getPath = (localRel) =>
      isGlobal ? getGlobalPath("cursor") : path.join(targetDir, localRel);
    const cursorTargetDir = getPath(".cursor");
    try {
      const cstat = fs.lstatSync(cursorTargetDir);
      if (cstat.isSymbolicLink()) {
        fs.unlinkSync(cursorTargetDir);
      } else if (cstat.isDirectory()) {
        for (const sub of ["rules", "skills"]) {
          const subDir = path.join(cursorTargetDir, sub);
          try {
            const stat = fs.lstatSync(subDir);
            if (stat.isSymbolicLink()) {
              fs.unlinkSync(subDir);
            } else if (stat.isDirectory()) {
              const skillsSrcDir = path.join(agentsSrc, "skills");
              if (fs.existsSync(skillsSrcDir)) {
                for (const skill of fs.readdirSync(skillsSrcDir)) {
                  const p = path.join(subDir, skill);
                  if (fs.existsSync(p)) fs.rmSync(p, { recursive: true, force: true });
                }
              }
              removeDirIfEmpty(subDir);
            }
          } catch {}
        }
        removeDirIfEmpty(cursorTargetDir);
      }
    } catch {}
  },
};
