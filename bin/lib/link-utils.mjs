/**
 * Symlink/copy installation primitives with conflict handling.
 * Follows vespyr/bin/lib/link-utils.js.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { R } from "./state.mjs";
import { logDry, logWarn } from "./logger.mjs";

export function handleConflict(linkPath, name, targetDir, method = "symlink") {
  try {
    const stat = fs.lstatSync(linkPath);
    if (stat.isSymbolicLink()) {
      const target = fs.readlinkSync(linkPath);
      const normTarget = target.replace(/\\/g, "/");
      const home = os.homedir().replace(/\\/g, "/");
      if (
        method === "symlink" &&
        (normTarget === ".agents" ||
          normTarget.endsWith("/.agents") ||
          normTarget.includes(".agents/") ||
          normTarget === `${home}/.agents` ||
          normTarget === `${home}/.agents/skills` ||
          normTarget === `${home}/.agents/agents`)
      ) {
        try {
          if (!fs.existsSync(linkPath)) {
            logWarn(`Removing dangling ${name} symlink to recreate it.`);
            if (!R.dryRun) fs.unlinkSync(linkPath);
          } else {
            return;
          }
        } catch {
          return;
        }
        return;
      }
      logWarn(`Removing existing symlink ${name} to configure with ${method}.`);
      if (!R.dryRun) fs.unlinkSync(linkPath);
    } else {
      if (method === "copy" && stat.isDirectory()) {
        return;
      }
      const backupPath = `${linkPath}.backup.${Date.now()}`;
      logWarn(`Existing ${name} found. Backing up to ${path.basename(backupPath)}`);
      if (!R.dryRun) {
        fs.renameSync(linkPath, backupPath);
      }
    }
  } catch (e) {
    if (e.code !== "ENOENT") {
      throw e;
    }
  }
}

export function createLinkOrCopy(target, linkPath, type = "dir", method = "symlink") {
  if (R.dryRun) {
    logDry(`Would create ${type} ${method}: ${linkPath} -> ${target}`);
    return;
  }

  const sourcePath = path.isAbsolute(target)
    ? target
    : path.resolve(path.dirname(linkPath), target);

  if (method === "copy") {
    if (type === "dir") {
      fs.cpSync(sourcePath, linkPath, { recursive: true, dereference: true });
      if (!R.createdLinks.includes(linkPath)) R.createdLinks.push(linkPath);
    } else {
      fs.copyFileSync(sourcePath, linkPath);
      if (!R.createdLinks.includes(linkPath)) R.createdLinks.push(linkPath);
    }
  } else {
    if (fs.existsSync(linkPath)) {
      try {
        const stat = fs.lstatSync(linkPath);
        if (stat.isSymbolicLink()) {
          const existing = fs.readlinkSync(linkPath);
          const normExisting = existing.replace(/\\/g, "/");
          const normTarget = target.replace(/\\/g, "/");
          const normRel = path.relative(path.dirname(linkPath), target).replace(/\\/g, "/");
          const normSource = sourcePath.replace(/\\/g, "/");
          if (
            normExisting === normTarget ||
            normExisting === normRel ||
            normExisting === normSource
          ) {
            return;
          }
        }
      } catch {
        /* ignore */
      }
    }

    try {
      const symlinkType = process.platform === "win32" && type === "dir" ? "junction" : type;
      const symlinkTarget =
        process.platform === "win32" && symlinkType === "junction" ? sourcePath : target;

      fs.symlinkSync(symlinkTarget, linkPath, symlinkType);
      R.createdLinks.push(linkPath);
    } catch (err) {
      if (
        err.code === "EPERM" ||
        err.code === "EACCES" ||
        err.code === "UNKNOWN" ||
        err.code === "EXDEV" ||
        err.code === "ENOSYS" ||
        err.code === "EROFS" ||
        err.code === "ENOTSUP" ||
        process.platform === "win32"
      ) {
        if (type === "dir") {
          fs.cpSync(sourcePath, linkPath, { recursive: true, dereference: true });
          logWarn(
            `Symlink failed (${err.code || "unsupported"}), copied directory instead: ${linkPath}`,
          );
        } else {
          fs.copyFileSync(sourcePath, linkPath);
          logWarn(
            `Symlink failed (${err.code || "unsupported"}), copied file instead: ${linkPath}`,
          );
        }
        if (!R.createdLinks.includes(linkPath)) R.createdLinks.push(linkPath);
      } else {
        throw err;
      }
    }
  }
}
