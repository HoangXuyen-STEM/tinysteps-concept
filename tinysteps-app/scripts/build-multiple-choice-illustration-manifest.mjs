// Build the multiple-choice illustration manifest by reusing the match illustrations.
//
// Every multiple_choice item describes the same scene as the lesson's match item at
// the same item index — their image_hint values are identical across all 175 lessons
// (verified). So instead of generating and uploading a second set of 525 images, each
// multiple-choice item points at the match asset already generated, QA'd, and uploaded
// to Storage. Keys use the multiple-choice exercise's own index so the app resolves
// them exactly like match keys.
//
// Idempotent: rewrites the manifest from source each run.

import { readdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const appDirectory = dirname(dirname(fileURLToPath(import.meta.url)));
const dataDirectory = join(dirname(appDirectory), "tinysteps-data");
const matchManifestPath = join(appDirectory, "public", "illustrations", "match", "manifest.json");
const outputPath = join(appDirectory, "public", "illustrations", "multiple-choice", "manifest.json");
const levels = ["starters", "movers", "flyers", "ket", "pet"];

const matchManifest = JSON.parse(await readFile(matchManifestPath, "utf8"));
const matchAssets = matchManifest.assets;
const outputAssets = {};
let mapped = 0;

for (const level of levels) {
  const lessonsDirectory = join(dataDirectory, "lessons", level);
  const files = (await readdir(lessonsDirectory))
    .filter((file) => /^lesson-\d{3}\.json$/.test(file))
    .sort();

  for (const file of files) {
    const lesson = JSON.parse(await readFile(join(lessonsDirectory, file), "utf8"));
    const matchIndex = lesson.exercises.findIndex((ex) => ex.type === "match");
    const choiceIndex = lesson.exercises.findIndex((ex) => ex.type === "multiple_choice");
    if (matchIndex === -1 || choiceIndex === -1) continue;

    const items = lesson.exercises[choiceIndex].items;
    for (let itemIndex = 0; itemIndex < items.length; itemIndex++) {
      const matchKey = `match/${lesson.id}/exercise-${matchIndex}/item-${itemIndex}`;
      const source = matchAssets[matchKey];
      if (!source) continue; // no generated image for this scene yet — UI shows the text cue
      outputAssets[`multiple-choice/${lesson.id}/exercise-${choiceIndex}/item-${itemIndex}`] = {
        path: source.path,
        alt: source.alt,
      };
      mapped++;
    }
  }
}

await writeFile(outputPath, `${JSON.stringify({ assets: outputAssets }, null, 2)}\n`);
console.log(`Mapped ${mapped} multiple-choice items to existing match illustrations.`);
