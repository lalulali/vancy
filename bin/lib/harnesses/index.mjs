/**
 * Harness adapter registry — STATIC import map.
 * Follows vespyr/bin/lib/harnesses/index.js.
 */
import os from "node:os";
import path from "node:path";

import opencode from "./opencode.mjs";
import claude from "./claude-code.mjs";
import kiro from "./kiro.mjs";
import cursor from "./cursor.mjs";
import github from "./github-copilot.mjs";
import windsurf from "./windsurf.mjs";

// Active shapes: installable + selectable in the interactive checklist.
export const ADAPTERS = [opencode, claude, github, kiro];

// NOTE — Codex: intentionally NO adapter.
// Current Codex natively reads root AGENTS.md and scans $REPO_ROOT/.agents/skills
// (+ ~/.agents/skills); support is implicit in the canonical .agents/ store.

// Legacy shapes: retained for detect + uninstall sweeps.
export const LEGACY_CLEANUP_ADAPTERS = [cursor, windsurf];

const ALL = [...ADAPTERS, ...LEGACY_CLEANUP_ADAPTERS];
export const REGISTRY = Object.fromEntries(ALL.map((a) => [a.id, a]));

const ALIASES = {
  "claude-code": "claude",
  "kiro-cli": "kiro",
  "github-copilot": "github",
  copilot: "github",
};

/** Checklist options: active (non-dormant) shapes only. */
export const HARNESS_OPTIONS = ADAPTERS.filter((a) => !a.dormant).map((a) => ({
  id: a.id,
  label: a.label,
  description: a.description,
}));

export function getAdapter(id) {
  if (!id) return null;
  const norm = ALIASES[id.trim().toLowerCase()] || id.trim().toLowerCase();
  return REGISTRY[norm] || null;
}

/**
 * Resolves a harness id (or the special "agents" store) to its global-scope
 * path. Delegates per-shape geometry to the adapter's globalPath().
 */
export function getGlobalPath(id, { home = os.homedir(), platform = process.platform } = {}) {
  if (id === "agents") return path.join(home, ".agents");
  const adapter = getAdapter(id);
  if (!adapter || typeof adapter.globalPath !== "function") return null;
  return adapter.globalPath({ home, platform });
}
