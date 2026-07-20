// Build the runtime illustration manifest from human-QA'd batch reports.
//
// Reads every docs/generated-illustrations/batch-*-report.md, keeps only rows whose
// "qa" column is exactly "Approved", cross-checks the file actually exists on disk
// (a report claiming a file exists is not proof — verified false once already, see
// batch-01), and writes tinysteps-app/public/illustrations/match/manifest.json.
//
// This is the ONLY thing that decides what the app can render — an image existing on
// disk with no Approved row in a report never reaches the manifest.
import { readdir, readFile, writeFile, access } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const appDirectory = join(fileURLToPath(import.meta.url), "..", "..");
const repositoryDirectory = join(appDirectory, "..");
const reportsDir = join(repositoryDirectory, "docs", "generated-illustrations");
const manifestPath = join(appDirectory, "public", "illustrations", "match", "manifest.json");

const ROW_PATTERN = /^\|\s*(match\/\S+?)\s*\|(.*)\|(.*)\|(.*)\|(.*)\|\s*$/;

async function fileExists(path) {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

async function parseReport(filePath) {
  const text = await readFile(filePath, "utf8");
  const rows = [];
  for (const line of text.split("\n")) {
    const match = line.match(ROW_PATTERN);
    if (!match) continue;
    const [, assetKey, imageHint, outputPath, , qa] = match;
    if (assetKey === "Asset Key") continue; // header row
    rows.push({
      assetKey: assetKey.trim(),
      imageHint: imageHint.trim(),
      outputPath: outputPath.trim(),
      qa: qa.trim(),
    });
  }
  return rows;
}

async function main() {
  let reportFiles = [];
  try {
    reportFiles = (await readdir(reportsDir)).filter((f) => f.endsWith("-report.md"));
  } catch {
    console.log(`No reports directory at ${reportsDir} — empty manifest.`);
  }

  const assets = {};
  let approved = 0;
  let approvedButMissingFile = 0;

  for (const file of reportFiles) {
    const rows = await parseReport(join(reportsDir, file));
    for (const row of rows) {
      if (!row.qa.startsWith("Approved")) continue;

      const absolutePath = join(repositoryDirectory, row.outputPath);
      if (!(await fileExists(absolutePath))) {
        approvedButMissingFile++;
        console.error(`APPROVED but file missing on disk, skipping: ${row.assetKey} (${row.outputPath})`);
        continue;
      }

      // Manifest stores the path relative to public/, matching how audio-manifest.ts
      // stores audio's relative paths — a future illustrationUrl() prepends the same
      // NEXT_PUBLIC_*_BASE_URL pattern already used for audio.
      const relativeToPublic = row.outputPath.replace(/^tinysteps-app\/public\//, "");
      assets[row.assetKey] = { path: relativeToPublic, alt: row.imageHint };
      approved++;
    }
  }

  const manifest = { version: 1, generatedAt: new Date().toISOString(), assets };
  await writeFile(manifestPath, JSON.stringify(manifest, null, 2) + "\n");

  console.log(`Manifest written: ${approved} approved assets.`);
  if (approvedButMissingFile > 0) {
    console.error(`${approvedButMissingFile} approved rows had no file on disk — check reports above.`);
    process.exit(1);
  }
}

main();
