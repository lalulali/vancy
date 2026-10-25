/**
 * opencode harness adapter — .opencode -> .agents symlink.
 * Follows vespyr/bin/lib/harnesses/opencode.js.
 */
import fs from "node:fs";
import path from "node:path";
import { getGlobalPath } from "./index.mjs";

export default {
  id: "opencode",
  label: "opencode",
  description: "scaffolds .opencode -> .agents symlink",

  detectPaths({ targetDir }) {
    return [`${targetDir}/.opencode`];
  },

  globalPath({ home }) {
    return `${home}/.opencode`;
  },

  methodProbePaths({ targetDir }) {
    return [`${targetDir}/.opencode`];
  },

  install(ctx) {
    const { targetDir, agentsTarget, method, handleConflict, createLinkOrCopy } = ctx;
    const linkPath = path.join(targetDir, ".opencode");
    handleConflict(linkPath, ".opencode", targetDir, method);
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
    return [`    ✓ .opencode -> .agents            (opencode harness)`];
  },

  uninstall(ctx) {
    const { targetDir, isGlobal, surgicallyCleanupAgentsDir } = ctx;
    const opencodePath = isGlobal ? getGlobalPath("opencode") : path.join(targetDir, ".opencode");
    try {
      const stat = fs.lstatSync(opencodePath);
      if (stat.isSymbolicLink()) {
        fs.unlinkSync(opencodePath);
        return;
      }
    } catch {
      return;
    }
    surgicallyCleanupAgentsDir(opencodePath);
  },
};
