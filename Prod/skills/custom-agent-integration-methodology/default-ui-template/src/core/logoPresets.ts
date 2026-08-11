export type BuilderPublicSiteLogoFamily = 'blue' | 'green' | 'purple' | 'red';

const LOGO_FILES_BY_FAMILY: Record<BuilderPublicSiteLogoFamily, string[]> = {
  blue: [
    'Blue-eat.svg',
    'Blue-enter.svg',
    'Blue-love.svg',
    'Blue-open.svg',
    'Blue-run.svg',
    'Blue-think.svg',
    'Blue.svg',
  ],
  green: [
    'Green-UFO.svg',
    'Green-bag.svg',
    'Green-drink.svg',
    'Green-magnifier.svg',
    'Green-sleep.svg',
    'Green-talk.svg',
  ],
  purple: [
    'Purple-award.svg',
    'Purple-celebrate.svg',
    'Purple-mirror.svg',
    'Purple-sleep.svg',
    'Purple-sweat.svg',
  ],
  red: [
    'Red-ID card.svg',
    'Red-ashbin.svg',
    'Red-backbend.svg',
    'Red-pause.svg',
    'Red-repair.svg',
    'Red-talk.svg',
    'Red-work.svg',
  ],
};

const LOGO_FAMILY_BY_FILE_NAME = new Map(
  Object.entries(LOGO_FILES_BY_FAMILY).flatMap(([family, fileNames]) => (
    fileNames.map((fileName) => [fileName, family as BuilderPublicSiteLogoFamily])
  )),
);

function safeDecodeURIComponent(value: string): string {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

export function normalizeBuilderPublicSiteLogoFileName(logo: string | null | undefined): string | null {
  const trimmed = logo?.trim();
  if (!trimmed) return null;

  try {
    const url = new URL(trimmed);
    const pathParts = url.pathname.split('/').filter(Boolean);
    const fileName = pathParts[pathParts.length - 1];
    return fileName ? safeDecodeURIComponent(fileName) : null;
  } catch {
    const pathWithoutQuery = trimmed.split(/[?#]/)[0];
    const pathParts = pathWithoutQuery.split('/').filter(Boolean);
    const fileName = pathParts[pathParts.length - 1];
    return fileName ? safeDecodeURIComponent(fileName) : null;
  }
}

export function getBuilderPublicSiteLogoFamily(logo: string | null | undefined): BuilderPublicSiteLogoFamily | null {
  const fileName = normalizeBuilderPublicSiteLogoFileName(logo);
  return fileName ? LOGO_FAMILY_BY_FILE_NAME.get(fileName) ?? null : null;
}

export function getBuilderPublicSiteAvatarObjectFit(logo: string | null | undefined): 'cover' | 'contain' {
  return getBuilderPublicSiteLogoFamily(logo) ? 'contain' : 'cover';
}
