// The real "server-only" package throws on import outside a React Server Component,
// which blocks unit-testing any server module that guards itself with it. Vitest aliases
// the package to this no-op so those modules can be imported directly by tests; the
// guard still applies to the real build, where the alias does not exist.
export {};
