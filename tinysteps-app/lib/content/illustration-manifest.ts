import matchManifest from "@/public/illustrations/match/manifest.json";
import multipleChoiceManifest from "@/public/illustrations/multiple-choice/manifest.json";

type IllustrationAsset = {
  path: string;
  alt: string;
};

export type ResolvedIllustration = IllustrationAsset & {
  assetKey: string;
  src: string;
};

const matchAssets = matchManifest.assets as Record<string, IllustrationAsset>;
const multipleChoiceAssets = multipleChoiceManifest.assets as Record<string, IllustrationAsset>;

function illustrationKey(
  kind: "match" | "multiple-choice",
  lessonId: string,
  exerciseIndex: number,
  itemIndex: number,
): string {
  return `${kind}/${lessonId}/exercise-${exerciseIndex}/item-${itemIndex}`;
}

// Manifest paths already start with "illustrations/", so the production base must be
// the Storage public root and must not include the bucket name a second time.
function resolve(
  assets: Record<string, IllustrationAsset>,
  assetKey: string,
): ResolvedIllustration | null {
  const asset = assets[assetKey];
  if (!asset) return null;

  const baseUrl = process.env.NEXT_PUBLIC_ASSET_BASE_URL?.replace(/\/+$/, "");
  return {
    ...asset,
    assetKey,
    src: baseUrl ? `${baseUrl}/${asset.path}` : `/${asset.path}`,
  };
}

export function matchIllustrationKey(
  lessonId: string,
  exerciseIndex: number,
  itemIndex: number,
): string {
  return illustrationKey("match", lessonId, exerciseIndex, itemIndex);
}

/** Resolve a QA-approved Match illustration, or null when none exists yet. */
export function resolveMatchIllustration(
  lessonId: string,
  exerciseIndex: number,
  itemIndex: number,
): ResolvedIllustration | null {
  return resolve(matchAssets, matchIllustrationKey(lessonId, exerciseIndex, itemIndex));
}

/**
 * Resolve a multiple-choice illustration, or null when none exists yet. Images are
 * generated in batches, so callers fall back to the item's `image_hint` text cue
 * until the real picture lands.
 */
export function resolveMultipleChoiceIllustration(
  lessonId: string,
  exerciseIndex: number,
  itemIndex: number,
): ResolvedIllustration | null {
  return resolve(
    multipleChoiceAssets,
    illustrationKey("multiple-choice", lessonId, exerciseIndex, itemIndex),
  );
}

export const getIllustrationCount = () => Object.keys(matchAssets).length;
export const getMultipleChoiceIllustrationCount = () =>
  Object.keys(multipleChoiceAssets).length;
