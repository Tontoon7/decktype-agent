# Decktype Agent — repository guide

## Produit

Public plugin (MIT) that teaches Claude Code and Codex to build, revise, render, and export editable Decktype presentations through the local `deck` CLI installed by the Decktype app (Apple silicon Mac, macOS 11+). One plugin, two marketplaces: Claude Code (`.claude-plugin/marketplace.json`) and Codex (`.agents/plugins/marketplace.json`). No hooks, MCP server, or bundled executable.

## Carte du code

- `.claude-plugin/marketplace.json` — Claude Code marketplace `decktype-agent`, one entry `decktype`.
- `.agents/plugins/marketplace.json` — Codex marketplace pointing at the same plugin folder.
- `plugins/decktype/.claude-plugin/plugin.json`, `plugins/decktype/.codex-plugin/plugin.json` — plugin manifests.
- `plugins/decktype/skills/decktype/` — generated copy of the complete Decktype agent skill shipped with the app. Never edit this directory by hand; make corrections in `skills/decktype/` in `Tontoon7/decktype`.
- `plugins/decktype/examples/` — example `.deck` and its four rendered slides.
- `docs/directory-submission.md` — English and French texts for the plugin directories.
- `tests/test_release.py` — release contract; `tests/fixtures/deck-cli-1.3.2.json` — public commands and options of the published `deck` CLI.

## Commandes

```sh
python3 -m unittest discover -s tests          # release tests (needs `deck` on PATH)
claude plugin validate --strict plugins/decktype
claude plugin validate --strict .
# Isolated install test, without touching the real configuration:
CLAUDE_CONFIG_DIR="$TMPDIR/cc-home" claude plugin marketplace add "$PWD"
CLAUDE_CONFIG_DIR="$TMPDIR/cc-home" claude plugin install decktype@decktype-agent
CLAUDE_CONFIG_DIR="$TMPDIR/cc-home" claude plugin list
mkdir -p "$TMPDIR/codex-home"
CODEX_HOME="$TMPDIR/codex-home" codex plugin marketplace add "$PWD"
CODEX_HOME="$TMPDIR/codex-home" codex plugin add decktype@decktype-agent
CODEX_HOME="$TMPDIR/codex-home" codex plugin list
```

## Conventions

- On every app release, the plugin version matches the Decktype app version: root and entry `version` of `.claude-plugin/marketplace.json`, plus both `plugin.json` files. Tests validate the shared `X.Y.Z` value without fixing it.
- The marketplace entry and the Claude `plugin.json` share the same description; all manifests share the same keywords.
- Keep maintained repository documentation's `deck` commands and options aligned with `tests/fixtures/deck-cli-*.json`, sourced from `deck --help` and `deck <command> --help` of the published CLI; mark a command newer than the oldest supported CLI with `"requires"`. The generated skill follows the matching app release and is checked for required commands and privacy markers, not against the historical fixture.
- The generated skill may describe the complete app, including Decktype Cloud, image generation, premium packs, and its public format guidance. Keep descriptions factual and derived from Decktype's published skill.
- Prices and platforms must match decktype.com (pricing and download pages); the website is the reference.
- Links to decktype.com from the README carry `utm_source=github&utm_medium=plugin&utm_campaign=claude_code_plugin_launch`.

## Livraison

Changes go through a reviewed pull request. A version tag on this public repository is a release: it is created by the maintainer after the merge, never by an agent or in a pull request. Directory submissions are made by the maintainer from `docs/directory-submission.md`.

## Travail dans l'usine

Do not commit, push, tag, or publish. Run the release tests and both `claude plugin validate --strict` commands before handing over. Test installs only in a throwaway `CLAUDE_CONFIG_DIR` or `CODEX_HOME` under `$TMPDIR`.

## Pièges connus

- The `deck` on a machine's `PATH` can be older than the published CLI; check `deck --version`. The published CLI ships inside the app at `/Applications/Decktype.app/Contents/Resources/agent-tools/bin/deck.zip` (unzip into `$TMPDIR` and put it first on `PATH` to test against it).
- The app installs the CLI in `~/Library/Application Support/Decktype/bin` and does not add it to `PATH`; the skill exports it first.
- `deck export` exits with status 3 and writes nothing without a signed-in Pro or Autonomous plan: never use it as test evidence. `deck pdf` (1.3.2+) works without an account.
- `tests/test_release.py` scans every generated skill file for personal paths, Kairia markers, and existing secret patterns. It deliberately allows the full skill's Cloud and image commands; fixture checks apply to maintained README and `docs/` content.
- decktype.com is not reachable from the factory sandbox; verify prices and platforms in the website source (`src/content.ts`, `src/lib/trust-pages.ts`) and leave the live check to review.
- `codex` 0.159 has no `plugin validate`: validate the Codex side with an isolated `codex plugin marketplace add` + `codex plugin add`; `CODEX_HOME` must exist beforehand (`mkdir -p`), otherwise every command fails with `failed to resolve CODEX_HOME`.
- `deck render` and the app renderer need a GPU (`no compatible wgpu device` in a sandbox); `deck validate`, `deck lint`, and `deck pdf` do not.
