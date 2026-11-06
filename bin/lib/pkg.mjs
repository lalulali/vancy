/**
 * Single source of truth for the package version.
 *
 * package.json is the only place a version is written by hand. Everything the
 * CLI, the wizard and the installer display or record (--version, install
 * banners, .agents/.vancy-version, manifest.json) reads it from here, so a
 * `npm version` bump is the only edit needed.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const PKG_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
export const PKG_PATH = path.join(PKG_ROOT, "package.json");

function readVersion() {
  let raw;
  try {
    raw = fs.readFileSync(PKG_PATH, "utf8");
  } catch (err) {
    throw new Error(`Cannot read ${PKG_PATH}: ${err.message}`);
  }

  let pkg;
  try {
    pkg = JSON.parse(raw);
  } catch (err) {
    throw new Error(`${PKG_PATH} is not valid JSON: ${err.message}`);
  }

  if (typeof pkg.version !== "string" || pkg.version.trim() === "") {
    throw new Error(`${PKG_PATH} has no "version" field`);
  }

  return pkg.version.trim();
}

export const VERSION = readVersion();
