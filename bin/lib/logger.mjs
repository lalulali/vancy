/**
 * CLI logging primitives. logDry honors the runtime dry-run flag owned by lib/state.mjs.
 * Follows vespyr/bin/lib/logger.js.
 */
import { R } from "./state.mjs";

export function log(msg) {
  console.log(msg);
}

export function logDry(msg) {
  if (R.dryRun) {
    console.log(`[DRY RUN] ${msg}`);
  }
}

export function logError(msg) {
  console.error(`Error: ${msg}`);
}

export function logWarn(msg) {
  console.warn(`Warning: ${msg}`);
}
