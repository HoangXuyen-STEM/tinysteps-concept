import manifest from "@/public/illustrations/match/manifest.json";

type IllustrationAsset = {
  path: string;
  alt: string;
};

export type ResolvedIllustration = IllustrationAsset & {
  assetKey: string;
  src: string;
};

const assets = manifest.assets as Record<string, IllustrationAsset>;

export function matchIllustrationKey(
  lessonId: string,
  exerciseIndex: number,
  itemIndex: number,
): string {
  return `match/${lessonId}/exercise-${exerciseIndex}/item-${itemIndex}`;
}

/**
 * Resolve a QA-approved Match illustration. Manifest paths already start with
 * "illustrations/", so the production base must be the Storage public root and
 * must not include the bucket name a second time.
 */
export function resolveMatchIllustration(
  lessonId: string,
  exerciseIndex: number,
  itemIndex: number,
): ResolvedIllustration | null {
  const assetKey = matchIllustrationKey(lessonId, exerciseIndex, itemIndex);
  const asset = assets[assetKey];
  if (!asset) return null;

  const baseUrl = process.env.NEXT_PUBLIC_ASSET_BASE_URL?.replace(/\/+$/, "");
  return {
    ...asset,
    assetKey,
    src: baseUrl ? `${baseUrl}/${asset.path}` : `/${asset.path}`,
  };
}

export const getIllustrationCount = () => Object.keys(assets).length;
