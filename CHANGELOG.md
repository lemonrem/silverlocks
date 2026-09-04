# Changelog

## 0.2.0 - 2026-09-04

- Added a hook-free, once-per-conversation update check with a 24-hour cache.
- Restricted automatic updates to higher versions from the trusted `lemonrem/silverlocks` origin, clean `main` checkouts, and fast-forward-only history.
- Preserved local changes and continued the active development task when an installation is copied, dirty, untrusted, diverged, or temporarily offline.
- Hardened continuity state against symlink escapes, malformed snapshots, quoted-objective mismatches, and destructive failed replacements.
- Added a compact repository-independent engineering loop and focused regression coverage for update and continuity safety.

## 0.1.0 - 2026-09-04

- Published the standalone Silverlocks Skill with implicit development-task routing.
- Added Direct and Plan Gate workflow selection with proportional verification and restarts.
- Added bounded, atomic continuity snapshots and intentional archives.
- Added required tracked Markdown recovery records for Git commits and releases.
- Added English and Simplified Chinese documentation and focused helper tests.
- Verified repository-root discovery, snapshot creation, reading, and archiving from a nested path in an unrelated Git project.
- Added natural-language prompts for autonomous Silverlocks installation, including prior disablement and removal of user-level Superpowers, Goldilocks, and their Hooks.
