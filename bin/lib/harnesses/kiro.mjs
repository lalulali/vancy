/**
 * Kiro harness adapter — hybrid shape: steering markdown emitted from AGENTS.md,
 * .kiro/skills symlink into .agents/skills, and .kiro/agents/ custom agent.
 * Follows vespyr/bin/lib/harnesses/kiro.js.
 */
import fs from "node:fs";
import path from "node:path";
import { getGlobalPath } from "./index.mjs";

function rewriteKiroAgentContent(srcFile, skillsRef) {
  if (!/\.(json|md)$/.test(srcFile)) return null;
  const raw = fs.readFileSync(srcFile, "utf8");
  return raw
    .replace(/skill:\/\/\.agents\/skills/g, `skill://${skillsRef}`)
    .replace(/(?<![~\w.\/])\.agents\/skills\//g, `${skillsRef}/`);
}

function copyAgentDir(src, dest, skillsRef) {
  fs.mkdirSync(dest, { recursive: true });
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, e.name);
    const d = path.join(dest, e.name);
    if (e.isSymbolicLink()) continue;
    if (e.isDirectory()) {
      copyAgentDir(s, d, skillsRef);
      continue;
    }
    const out = rewriteKiroAgentContent(s, skillsRef);
    if (out === null) fs.copyFileSync(s, d);
    else fs.writeFileSync(d, out);
  }
}

export default {
  id: "kiro",
  label: "Kiro Steering & Skills",
  description: "scaffolds .kiro/steering/, .kiro/agents/ & .kiro/skills/ symlink",

  detectPaths({ targetDir }) {
    return [`${targetDir}/.kiro/steering`, `${targetDir}/.kiro/skills`, `${targetDir}/.kiro/agents`];
  },

  globalPath({ home }) {
    return `${home}/.kiro`;
  },

  methodProbePaths({ targetDir }) {
    return [
      `${targetDir}/.kiro/skills`,
      `${targetDir}/.kiro/steering/career-consultant-steering.md`,
    ];
  },

  install(ctx) {
    const { targetDir, agentsTarget, method, dryRun, handleConflict, createLinkOrCopy } = ctx;
    const isGlobal = targetDir === path.dirname(agentsTarget) && path.basename(agentsTarget) === ".agents" && targetDir === process.env.HOME;
    const kiroDir = path.join(targetDir, ".kiro");
    const steeringDir = path.join(kiroDir, "steering");
    const skillsDir = path.join(kiroDir, "skills");
    const agentsDir = path.join(kiroDir, "agents");

    if (!dryRun) {
      fs.mkdirSync(kiroDir, { recursive: true });
    }

    if (fs.existsSync(steeringDir)) {
      try {
        const stat = fs.lstatSync(steeringDir);
        if (stat.isSymbolicLink()) {
          if (!dryRun) fs.unlinkSync(steeringDir);
        }
      } catch {}
    }

    if (!dryRun && !fs.existsSync(steeringDir)) {
      fs.mkdirSync(steeringDir, { recursive: true });
    }

    handleConflict(skillsDir, "kiro skills", targetDir, method);
    if (!fs.existsSync(skillsDir)) {
      createLinkOrCopy(
        path.relative(kiroDir, path.join(agentsTarget, "skills")),
        skillsDir,
        "dir",
        method,
      );
    }

    const steeringAgentsPath = path.join(steeringDir, "career-consultant-steering.md");
    const canonicalSource = fs.existsSync(path.join(targetDir, "AGENTS.md"))
      ? path.join(targetDir, "AGENTS.md")
      : path.join(agentsTarget, "agents", "career-consultant", "prompt.md");

    if (fs.existsSync(canonicalSource)) {
      handleConflict(
        steeringAgentsPath,
        "kiro steering career-consultant-steering.md",
        targetDir,
        method,
      );
      if (!fs.existsSync(steeringAgentsPath)) {
        createLinkOrCopy(
          path.relative(steeringDir, canonicalSource),
          steeringAgentsPath,
          "file",
          method,
        );
      }
    }

    // Emit Kiro custom agent (.kiro/agents/career-consultant.json + career-consultant/)
    const srcAgentsDir = path.join(agentsTarget, "agents");
    if (fs.existsSync(srcAgentsDir)) {
      const skillsRef = isGlobal ? "~/.kiro/skills" : ".kiro/skills";
      if (!dryRun) {
        copyAgentDir(srcAgentsDir, agentsDir, skillsRef);
      }
    }
  },

  summaryLines() {
    return [
      `    ✓ .kiro/steering/career-consultant-steering.md (Kiro steering)`,
      `    ✓ .kiro/skills -> skills          (Kiro skills)`,
      `    ✓ .kiro/agents/career-consultant  (Kiro custom agent)`,
    ];
  },

  uninstall(ctx) {
    const { targetDir, isGlobal, agentsSrc, removeDirIfEmpty } = ctx;
    const getPath = (localRel) =>
      isGlobal ? getGlobalPath("kiro") : path.join(targetDir, localRel);
    const kiroTargetDir = getPath(".kiro");
    try {
      const kstat = fs.lstatSync(kiroTargetDir);
      if (kstat.isSymbolicLink()) {
        fs.unlinkSync(kiroTargetDir);
        return;
      }
    } catch {
      return;
    }

    const skillsDir = path.join(kiroTargetDir, "skills");
    try {
      const stat = fs.lstatSync(skillsDir);
      if (stat.isSymbolicLink()) {
        fs.unlinkSync(skillsDir);
      } else if (stat.isDirectory()) {
        const skillsSrcDir = path.join(agentsSrc, "skills");
        if (fs.existsSync(skillsSrcDir)) {
          const coreSkills = fs.readdirSync(skillsSrcDir);
          for (const skill of coreSkills) {
            const skillPath = path.join(skillsDir, skill);
            if (fs.existsSync(skillPath)) {
              fs.rmSync(skillPath, { recursive: true, force: true });
            }
          }
        }
        removeDirIfEmpty(skillsDir);
      }
    } catch {}

    const steeringDir = path.join(kiroTargetDir, "steering");
    try {
      const stat = fs.lstatSync(steeringDir);
      if (stat.isSymbolicLink()) {
        fs.unlinkSync(steeringDir);
      } else if (stat.isDirectory()) {
        const steeringFile = path.join(steeringDir, "career-consultant-steering.md");
        try {
          const st = fs.lstatSync(steeringFile);
          if (st.isSymbolicLink() || st.isFile()) {
            fs.unlinkSync(steeringFile);
          }
        } catch {}
        removeDirIfEmpty(steeringDir);
      }
    } catch {}

    const agentsDir = path.join(kiroTargetDir, "agents");
    try {
      const stat = fs.lstatSync(agentsDir);
      if (stat.isSymbolicLink()) {
        fs.unlinkSync(agentsDir);
      } else if (stat.isDirectory()) {
        const agentsSrcDir = path.join(agentsSrc, "agents");
        if (fs.existsSync(agentsSrcDir)) {
          for (const entry of fs.readdirSync(agentsSrcDir)) {
            const p = path.join(agentsDir, entry);
            if (fs.existsSync(p)) {
              fs.rmSync(p, { recursive: true, force: true });
            }
          }
        }
        removeDirIfEmpty(agentsDir);
      }
    } catch {}

    removeDirIfEmpty(kiroTargetDir);
  },
};
