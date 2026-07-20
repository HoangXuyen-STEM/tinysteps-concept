// Validate the public configuration needed for a sellable production deployment.
// Prints variable names and validation errors only; never prints values.

const required = [
  "NEXT_PUBLIC_SUPABASE_URL",
  "NEXT_PUBLIC_SUPABASE_ANON_KEY",
  "NEXT_PUBLIC_AUDIO_BASE_URL",
  "NEXT_PUBLIC_ASSET_BASE_URL",
  "NEXT_PUBLIC_SITE_URL",
  "NEXT_PUBLIC_BANK_CODE",
  "NEXT_PUBLIC_BANK_ACCOUNT",
  "NEXT_PUBLIC_BANK_HOLDER",
  "NEXT_PUBLIC_CONTACT_URL",
  "NEXT_PUBLIC_CONTACT_LABEL",
];

const errors = [];

for (const name of required) {
  if (!process.env[name]?.trim()) errors.push(`${name}: missing`);
}

for (const name of [
  "NEXT_PUBLIC_SUPABASE_URL",
  "NEXT_PUBLIC_AUDIO_BASE_URL",
  "NEXT_PUBLIC_ASSET_BASE_URL",
  "NEXT_PUBLIC_SITE_URL",
  "NEXT_PUBLIC_CONTACT_URL",
]) {
  const value = process.env[name]?.trim();
  if (!value) continue;
  try {
    const url = new URL(value);
    if (url.protocol !== "https:") errors.push(`${name}: must use https`);
  } catch {
    errors.push(`${name}: invalid URL`);
  }
}

for (const name of ["NEXT_PUBLIC_AUDIO_BASE_URL", "NEXT_PUBLIC_ASSET_BASE_URL"]) {
  const value = process.env[name]?.replace(/\/+$/, "");
  if (value && !value.endsWith("/storage/v1/object/public")) {
    errors.push(`${name}: must end at /storage/v1/object/public (no bucket suffix)`);
  }
}

if (process.env.NEXT_PUBLIC_OFFER_STAGE && !["early_bird", "standard"].includes(process.env.NEXT_PUBLIC_OFFER_STAGE)) {
  errors.push("NEXT_PUBLIC_OFFER_STAGE: must be early_bird or standard");
}

if (errors.length > 0) {
  console.error("Launch configuration is not ready:");
  errors.forEach((error) => console.error(`  - ${error}`));
  process.exit(1);
}

console.log("Launch configuration is ready.");
