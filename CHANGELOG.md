# Changelog

## 0.2.3 - 2026-09-08

- Consolidate execution and stopping rules into a smaller entrypoint; load detailed diagnosis and ownership guidance only when needed.
- Preserve disproven hypotheses, failed approaches, and the next distinguishing experiment for recurring defects; return to the active task after status questions.
- Prefer repository-defined continuity files over a competing Silverlocks snapshot and keep implementation plus affected verification with one owner.
- Add reproducible behavioral fixtures for recurring failures, in-flight status questions, and diagnosis-only boundaries.

## 0.2.2 - 2026-09-07

- Treat contextual defect reports as requests to act; finish authorized work through implementation and verification instead of ending with explanations or offers.
- Require an available authorized next action to be executed before ending an action task, while preserving analysis-only requests and concrete access or decision blockers.
- Refresh loaded skill instructions after successful updates and publish a higher version so existing installations can receive these workflow fixes.

## 0.2.1 - 2026-09-06

- Separated proportional planning from approval: carry existing authorization forward and ask only for material missing choices or authority.
- Preserved the active objective when follow-up questions and corrections arrive.
- Reject incomplete updates with missing, empty, symlinked or directory-shaped required files, including the three workflow references.
- Added regression cases proving rejected updates preserve the installed revision and version.

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
