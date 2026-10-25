/**
 * Windsurf harness adapter — DORMANT (cleanup-only, follows vespyr/bin/lib/harnesses/windsurf.js).
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { getGlobalPath } from "./index.mjs";

export default {
  id: "windsurf",
  label: "Windsurf",
  description: "scaffolds .windsurf/workflows symlink & .windsurfrules symlink",
  dormant: true,
  legacyCleanupOnly: true,

  detectPaths({ targetDir }) {
    return [`${targetDir}/.windsurf/workflows`, `${targetDir}/.windsurf/skills`];
  },

  globalPath({ home }) {
    return `${home}/.windsurf`;
  },

  methodProbePaths({ targetDir }) {
    return [`${targetDir}/.windsurf/workflows`, `${targetDir}/.windsurf/skills`];
  },

  uninstall(ctx) {
    const { targetDir, isGlobal, agentsSrc, removeDirIfEmpty } = ctx;
    const home = os.homedir();
    const getPath = (localRel) =>
      isGlobal ? getGlobalPath("windsurf") : path.join(targetDir, localRel);
    const windsurfTargetDir = getPath(".windsurf");
    try {
      const wstat = fs.lstatSync(windsurfTargetDir);
      if (wstat.isSymbolicLink()) {
        fs.unlinkSync(windsurfTargetDir);
      } else if (wstat.isDirectory()) {
        for (const sub of ["workflows", "skills"]) {
          const subDir = path.join(windsurfTargetDir, sub);
          try {
            const stat = fs.lstatSync(subDir);
            if (stat.isSymbolicLink()) {
              fs.unlinkSync(subDir);
            } else if (stat.isDirectory()) {
              const skillsSrcDir = path.join(agentsSrc, "skills");
              if (fs.existsSync(skillsSrcDir)) {
                for (const skill of fs.readdirSync(skillsSrcDir)) {
                  const skillPath = path.join(subDir, skill);
                  if (fs.existsSync(skillPath)) {
                    fs.rmSync(skillPath, { recursive: true, force: true });
                  }
                }
              }
              removeDirIfEmpty(subDir);
            }
          } catch {}
        }
        removeDirIfEmpty(windsurfTargetDir);
      }
    } catch {}
    const windsurfRulesPath = isGlobal
      ? path.join(home, ".windsurfrules")
      : path.join(targetDir, ".windsurfrules");
    try {
      const st = fs.lstatSync(windsurfRulesPath);
      if (st.isSymbolicLink()) {
        fs.unlinkSync(windsurfRulesPath);
      } else if (st.isFile()) {
        try {
          const content = fs.readFileSync(windsurfRulesPath, "utf8");
          if (content.includes("Vancy-managed") || content.includes(".agents/")) {
            fs.unlinkSync(windsurfRulesPath);
          }
        } catch {}
      }
    } catch {}
  },
};
