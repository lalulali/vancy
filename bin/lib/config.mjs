/**
 * Standing language and paper-size preference: `<target>/.vancy/config.json`.
 *
 * Every document renderer reads this file after the command line and the
 * document's own front matter, and before its built-in fallback. The installer
 * writes it during setup so the user picks once instead of per document.
 */
import fs from "node:fs";
import path from "node:path";

export const CONFIG_DIR = ".vancy";
export const CONFIG_REL = path.join(CONFIG_DIR, "config.json");
export const DEFAULT_LANG = "en-US";
export const DEFAULT_PAGE = "a4";

const LANG_TAG_RE = /^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*$/;

/**
 * Installer choices. Language and paper size are independent: US spelling on
 * A4 paper is a real combination (international applicants, remote roles).
 */
export const LANGUAGE_CHOICES = [
  { lang: "ar", label: "Arabic" },
  { lang: "zh-CN", label: "Chinese (Simplified)" },
  { lang: "zh-TW", label: "Chinese (Traditional)" },
  { lang: "nl-NL", label: "Dutch" },
  { lang: "en-GB", label: "English (UK)" },
  { lang: "en-US", label: "English (US)" },
  { lang: "fil-PH", label: "Filipino" },
  { lang: "fr-FR", label: "French" },
  { lang: "de-DE", label: "German" },
  { lang: "hi-IN", label: "Hindi" },
  { lang: "id-ID", label: "Indonesian" },
  { lang: "it-IT", label: "Italian" },
  { lang: "ja-JP", label: "Japanese" },
  { lang: "ko-KR", label: "Korean" },
  { lang: "ms-MY", label: "Malay" },
  { lang: "pl-PL", label: "Polish" },
  { lang: "pt-PT", label: "Portuguese (Portugal)" },
  { lang: "ru-RU", label: "Russian" },
  { lang: "es-ES", label: "Spanish (Spain)" },
  { lang: "th-TH", label: "Thai" },
  { lang: "tr-TR", label: "Turkish" },
  { lang: "vi-VN", label: "Vietnamese" },
];

export const PAPER_CHOICES = [
  { page: "a4", label: "A4 — most of the world" },
  { page: "letter", label: "Letter — US, Canada, Mexico, Philippines" },
];

/** Markets whose documents conventionally use Letter paper. */
export const LETTER_MARKETS = new Set(["en-US", "en-CA", "es-MX", "fil-PH"]);

export function configFile(targetDir) {
  return path.join(targetDir, CONFIG_REL);
}

export function validateLang(value) {
  if (typeof value !== "string" || !LANG_TAG_RE.test(value.trim())) {
    throw new Error(`Invalid language ${JSON.stringify(value)}: use a BCP 47 tag such as en-US or en-GB.`);
  }
  // Canonical casing: language lowercase, script Titlecase, region uppercase.
  return value
    .trim()
    .split("-")
    .map((part, i) => {
      if (i === 0) return part.toLowerCase();
      if (part.length === 4) return part[0].toUpperCase() + part.slice(1).toLowerCase();
      if (part.length === 2) return part.toUpperCase();
      return part.toLowerCase();
    })
    .join("-");
}

export function validatePage(value) {
  const page = String(value).trim().toLowerCase();
  if (page !== "a4" && page !== "letter") {
    throw new Error(`Invalid paper size ${JSON.stringify(value)}: use a4 or letter.`);
  }
  return page;
}

/** Read the file. Returns {} when it does not exist; throws on a malformed file. */
export function readConfig(targetDir) {
  const file = configFile(targetDir);
  if (!fs.existsSync(file)) return {};
  let data;
  try {
    data = JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (err) {
    throw new Error(`${file} is not valid JSON: ${err.message}`);
  }
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    throw new Error(`${file} must contain a JSON object such as {"lang": "en-US", "page": "a4"}.`);
  }
  return data;
}

/**
 * Merge and write. Unknown keys already in the file are preserved, so a future
 * version can add settings without this one deleting them.
 */
export function writeConfig(targetDir, patch = {}) {
  const data = readConfig(targetDir);
  if (patch.lang !== undefined && patch.lang !== null) data.lang = validateLang(patch.lang);
  if (patch.page !== undefined && patch.page !== null) data.page = validatePage(patch.page);
  const file = configFile(targetDir);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(data, null, 2)}\n`, "utf8");
  return { file, data };
}

export function describeConfig(targetDir) {
  const data = readConfig(targetDir);
  return {
    lang: data.lang || `${DEFAULT_LANG} (default)`,
    page: data.page || `${DEFAULT_PAGE} (default)`,
  };
}
