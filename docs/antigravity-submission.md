# Antigravity Marketplace submission

`plugins/decktype-antigravity/` packages the Decktype remote connector for the Antigravity Marketplace (App, IDE and CLI). It bundles no skill, hook, script or executable: one remote MCP server, a manifest, a README and the app icon.

## Listing

| Field | Text |
| --- | --- |
| Name | `decktype` |
| Display name | Decktype |
| Description | Create and revise editable presentations with your agent, preview each slide, then open the deck in the Decktype editor. |
| Starter prompts | See `plugin.json` (three prompts, at most three allowed) |
| Author | Kairia, https://decktype.com |
| Homepage | https://decktype.com/en/connectors |
| Privacy policy | https://decktype.com/en/privacy |
| Terms | https://decktype.com/en/terms |
| Support | https://decktype.com/en/contact |
| Logo | `assets/app-icon.svg`, exact copy of `crates/decktype-app/packaging/appicon.svg` in `Tontoon7/decktype` (dark tile with 10% margin, legible on light and dark themes) |

## Connection

`mcp_config.json` declares `https://api.decktype.com/mcp` without a client identifier: Antigravity signs in by Client ID Metadata Document or Dynamic Client Registration, both accepted by the Decktype server (https://antigravity.google/docs/mcp). Sign-in with Antigravity has not been tested yet.

## Before submitting

```sh
agy plugin validate --strict ./plugins/decktype-antigravity
agy plugin install ./plugins/decktype-antigravity
agy plugin list
```

Then connect a dedicated review account in Antigravity and run cases P1 to P5 and N1 to N3 of `docs/openai-submission.md`. Submit through the Antigravity Marketplace partner intake form (https://antigravity.google/docs/marketplace) once both pass. The plugin is installable without a listing with `agy plugin install https://github.com/Tontoon7/decktype-agent` pointing at this folder.

## Status

Prepared on 2026-11-10. Manifest checked against https://antigravity.google/schemas/v1/plugin.json (no unknown key, all Marketplace fields present). `agy plugin validate --strict`, sign-in and review cases: pending. Not submitted.
