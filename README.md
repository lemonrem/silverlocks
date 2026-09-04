# Silverlocks

[简体中文](README.zh-CN.md)

Silverlocks is a lightweight, hook-free Codex Skill that scales the development workflow to the task. Small changes stay direct. Risky or cross-cutting work gets a deliberate plan. Verification, restarts, specialist skills, and continuity records are used only when they add value.

It is a standalone Skill, not a plugin. Installing it does not start a daemon, register a Hook, add an MCP server, or send telemetry.

## What it changes

- Automatically applies to software-development tasks through its skill description and `allow_implicit_invocation: true` metadata.
- Keeps small, clear, reversible changes in a direct workflow.
- Uses a Plan Gate for cross-module work, contracts, persisted data, security, deployment boundaries, material ambiguity, or likely cross-session work.
- Preserves every relevant specialist Skill instead of replacing or suppressing it.
- Uses focused tests and component-scoped restarts instead of habitual full regression and full builds.
- Keeps resumable state in one compact, replace-only `.silverlocks/CURRENT.md` file.
- Creates intentional local archives and requires a tracked Markdown recovery record for Git commits and releases.

## Why no Hooks?

A Hook runs because an event occurred. That makes sense for deterministic enforcement that must happen independently of model judgment, but it adds latency and operational complexity when used only to announce routing, reread state, or force generic checks.

Silverlocks keeps those decisions in the Skill instructions. Codex loads the workflow when a development request matches the description; the helper script runs only when continuity state is actually needed. There is no background execution.

## Install

### With the built-in installer

Ask Codex:

```text
$skill-installer Install the skill from https://github.com/lemonrem/silverlocks
```

### Manually

Codex's current user-level Skill directory is `~/.agents/skills`:

```bash
git clone https://github.com/lemonrem/silverlocks.git ~/.agents/skills/silverlocks
```

Codex detects Skill changes automatically. If Silverlocks does not appear in `/skills`, restart Codex. The official locations and loading behavior are documented in [Build skills](https://learn.chatgpt.com/docs/build-skills).

If another broad workflow Skill is already installed, disable one of them to avoid duplicate routing. A Skill can be disabled without deleting it in `~/.codex/config.toml`:

```toml
[[skills.config]]
path = "/absolute/path/to/the/other-skill/SKILL.md"
enabled = false
```

Restart Codex after changing this configuration.

## Use and update

Silverlocks is eligible for implicit use on development tasks. Explicit invocation also works:

```text
$silverlocks diagnose this failure and implement the smallest safe fix
```

Update a manual Git installation with:

```bash
git -C ~/.agents/skills/silverlocks pull --ff-only
```

The installed checkout is what Codex loads; a newer GitHub revision is not active until the local copy is updated. If an update is not detected, restart Codex.

## What a teammate gets after installation

Silverlocks is user-scoped and repository-independent. A teammate can open any Git repository and use the same workflow without copying files from this repository into the project. It does not depend on the author's application repository, a particular framework, a fixed directory layout, or a pre-existing `AGENTS.md`.

On the first development request in a new conversation, Codex uses the installed Skill's helper to locate the current repository. If a resumable task already has `<that-repository>/.silverlocks/CURRENT.md`, Codex can read it once. If substantial work is likely to cross a conversation boundary and no snapshot exists, Codex can create it with the helper. Small tasks that finish in one turn do not create one.

The state always belongs to the teammate's current workspace:

```text
any-project/
└── .silverlocks/
    ├── CURRENT.md
    └── archive/work/
```

Git is used only to discover the repository root and record an optional revision. Non-Git workspaces are also supported when their root is passed to the helper explicitly. Project-specific `AGENTS.md` rules, when present, remain authoritative and are composed with Silverlocks rather than required by it.

## Continuity model

Silverlocks checks for `.silverlocks/CURRENT.md` once on the first development turn for a workspace in a new conversation. It reads an eligible snapshot once, compares the saved objective with the current request, and ignores unrelated state.

`CURRENT.md` is not a log. It is an at-most-8-KiB snapshot containing verified progress, one exact next action, durable constraints, and minimal evidence. Every update atomically replaces the whole file. Completed or superseded state moves to `.silverlocks/archive/work/` only when needed.

The local `.silverlocks/` directory should normally remain untracked. A user-requested Git commit or release must also include a repository-tracked Markdown recovery record under the repository's existing convention, or under `docs/versions/` when no convention exists. See [continuity.md](references/continuity.md) for the exact policy and helper commands.

## Repository layout

```text
silverlocks/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── continuity.md
│   └── planning-and-verification.md
├── scripts/continuity.py
└── tests/test_continuity.py
```

## Privacy and permissions

- No network calls, telemetry, update checks, background services, or Hooks.
- The helper reads and writes only the selected workspace's `.silverlocks` state.
- Secret material is explicitly prohibited from continuity and archive files.
- Silverlocks does not grant permission to commit, push, deploy, message people, or mutate external systems.
- Workspace instructions and the user's current request remain authoritative.

## Development and validation

Requirements: Python 3.10 or newer. Git is optional; when present, the helper records the current revision.

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py .
```

## License and origin

Silverlocks is released under the MIT License. It is an independent, hook-free adaptation inspired by [Goldilocks](https://github.com/blackstone2333/goldilocks); see [NOTICE.md](NOTICE.md). It is not affiliated with OpenAI.
