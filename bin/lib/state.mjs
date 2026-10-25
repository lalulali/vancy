/**
 * Mutable runtime install state shared across CLI layers.
 * Follows vespyr/bin/lib/state.js.
 */
export const R = {
  createdLinks: [],
  installed: false,
  dryRun: false,
};

export function setState(patch) {
  Object.assign(R, patch);
}

export function resetRuntimeState() {
  R.createdLinks = [];
  R.installed = false;
  R.dryRun = false;
}

export function snapshotRuntimeState() {
  return {
    createdLinks: [...R.createdLinks],
    installed: R.installed,
    dryRun: R.dryRun,
  };
}
