# Theme Compiler: agent-first workflow

Use this workflow to create or modify a complete theme from a presentation,
a website or both. A complete theme contains an identity, verified assets,
an immutable revision and its own template gallery.

The normal path uses the user's tokens and their agent's capabilities. It
stays local, does not consume the Decktype AI engine and calls no
`theme-generations` route.

## Invariants

- The installed theme is private by default.
- Workspace sharing is an explicit, separate, later action.
- An accepted revision is immutable.
- Several themes and revisions can coexist in one deck.
- Changing the active theme does not modify existing slides.
- A new linked slide always carries `theme_id` and `theme_revision_id`.
- A raw presentation, its notes and business text never leave the machine
  through this local path.
- Output files are never silently overwritten.

Start by checking `deck --version` and `deck theme --help`. The CLI output
and its current schemas are authoritative.

## 1. Choose sources

Accept a local `.deck` or `.pptx` presentation, a public URL or both.
Presentation format is detected from bytes, not the extension. Never convert
content into a prompt. For a website, reject localhost, private, link-local
or credential-bearing origins.

## 2. Capture a website without source text

First request the current contract:

```text
deck theme schema --kind site-capture --json
```

Using the available browser tool, inspect public pages and create a
`site-capture.json` conforming to the report's `schema` member. Keep only
established design facts: hashed provenance, colors, font families and weights,
layout geometries and recurring public assets. Exclude page titles, copy,
section names, business content, HTML, raw CSS and screenshots.

For each declared asset, store bytes in
`site-capture.json.assets/<sha256>`. Hash, MIME type and size must match the
JSON. Never use a symlink or parent path.

## 3. Analyze locally

Choose the command matching the sources:

```text
deck theme analyze --presentation source.pptx --out evidence.json --json
deck theme analyze --site-evidence site-capture.json --out evidence.json --json
deck theme analyze --presentation source.deck --site-evidence site-capture.json --out evidence.json --json
```

The report must have `schema_version`, `operation`, absolute paths in
`outputs`, `warnings` and `diagnostics`. Code `1` means invalid content;
code `2` means a usage, reading or rendering error.

## 4. Inspect evidence

Read `evidence.json` before any generation. Verify sources, confidence levels,
dominant colors and fonts, recurring assets, layout clusters and `conflicts`.
When presentation and website diverge, resolve according to the user's
request; never hide the conflict.

To check the contract without duplicating it here:

```text
deck theme schema --kind evidence --json
```

## 5. Create the canonical draft

```text
deck theme scaffold --evidence evidence.json --id client --name "Client" --out client-draft.json --json
deck theme schema --kind draft --json
```

The scaffold creates fifteen required bases: `cover`, `section`, `statement`,
`editorial`, `two-columns`, `cards`, `process`, `timeline`, `kpi`, `chart`,
`table`, `comparison`, `quote`, `hero-image` and `closing`.

For a client PowerPoint template, preparation and installation take two
commands (read the evidence between them):

```text
deck theme analyze --presentation modele.pptx --out evidence.json --json
deck theme scaffold --evidence evidence.json --id client --name Client --logo logo.png --out client-draft.json --package client.decktheme --install --json
```

Analysis prefers visible styles in slides, layouts and masters over Office
values. The scaffold applies their metrics, logos and banners to the fifteen
bases. `--logo` is optional: it replaces the logo at the observed frame;
otherwise a top-right frame is reported. `--install` requires `--package`;
preview creation requires the GPU. If it fails, the report names the retained
draft without installing it. Inspect all fifteen package previews.
These bases are ready: do not write or copy templates by hand to compose the
presentation. The requested family remains explicit; a font fallback does
not prove typographic fidelity.

## 6. Complete with the user's agent

Edit the draft according to the current schema. Correct style tokens,
description, asset usages and templates from the inspected evidence.
Use the user's own capabilities and tokens. Do not replace the fifteen bases;
variants can be added with `variant_of`.

Each draft asset lives in `client-draft.json.assets/<chemin-manifest>` and must
exactly match declared hash, size and type. Keep all paths relative and normalized.

## 7. Validate and repair

```text
deck theme validate client-draft.json --json
```

Fix diagnostics at their cause. Perform at most two repair loops per candidate.
If a candidate stays invalid, discard it and explain diagnostics; never weaken
the validator or remove a required base.

The CLI measures `THEME_TEMPLATE_OVERFLOW` with the actual style and fonts from
sidecars or package before GPU previews. Supply declared bytes before
validating: a fallback does not attest to the requested family's dimensions.
The Node validator remains structural without a measurement engine; the browser
validates with registered fonts and all assets when finalizing the builder.
Before declared font bytes are transferred, its JSON validation skips text
measurement and emits a warning; it does not reject the draft for this
incomplete measurement alone. Builder finalization measures the real assets.

## 8. Render and inspect the fifteen bases

```text
deck theme render client-draft.json --out client-preview --json
```

Open each PNG with the available image viewer. Check hierarchy, contrast,
typography, overflows, assets, consistency and distinct layouts. Successful
rendering alone is insufficient. Validate and render again after any draft fix.

## 9. Package and install privately

```text
deck theme package client-draft.json --out client.decktheme --json
deck theme validate client.decktheme --json
deck theme import client.decktheme --json
deck theme list --json
deck theme show client --json
```

Preserve the `theme_id` and `revision_id` returned by reports. Importing a valid
package installs that revision privately and remains idempotent. Repackaging
an installed revision reuses its bytes; an edited draft requires a new
`revision_id`. To transport the exact revision:

```text
deck theme export client --revision <revision_id> --out client.decktheme --json
```

If the `brand_kits.unlimited` entitlement is present, offer private Cloud
synchronization. Do not run it without agreement and do not confuse private
synchronization with sharing.

## 10. Activate without changing existing slides

```text
deck theme activate client --revision <revision_id> --deck presentation.deck --json
```

Activation changes the active pair and its compatibility mirror, then embeds
the exact gallery and its assets. It regenerates no slides. Every new binding
copies both `theme_id` and `theme_revision_id`; every existing binding keeps
its exact pair.

```text
deck templates list --deck presentation.deck --json
deck templates show <pack_exact>/editorial --deck presentation.deck --json
```

Use the returned qualified pack and skeleton, never a reconstructed pack.
Embedded templates take priority and remain available without a local library.
`show --slide <id>` uses that slide's own revision. For new slides, also use
that revision's background (visible in `deck inspect`): activation preserves
existing backgrounds and `regenerate` does not recalculate them. Replace
`new`'s empty scaffold with linked content.

## 11. Share only on request

Offer workspace sharing only after private installation or synchronization.
Sharing is never automatic and its control remains unchecked by default.
Ask for explicit confirmation of the target and revision. Local activation,
import or private synchronization never authorizes sharing.

## Decktype managed mode

The `--engine cloud` option is reserved for an explicit request for managed
generation in Autonomous mode. It is never an implicit fallback, including
after local failure, missing quota or an invalid asset. In all other cases,
stay with this agent-first workflow using the user's tokens.

The managed engine always requires JSON evidence already inspected and
corrected. Resolve all conflicts before the call, then retain sources matching
the evidence's exact provenance:

```text
$ deck theme generate --engine cloud --evidence evidence.json --presentation source.pptx --id client --name Client --json
$ deck theme generate --engine cloud --evidence evidence.json --site https://example.com --id client --name Client --json
$ deck theme generate --engine cloud --evidence evidence.json --presentation source.pptx --site https://example.com --id client --name Client --json
```

The presentation is reread locally only to reconstruct redacted previews
around the corrected evidence. For a website alone, corrected evidence is
uploaded as JSON and the public URL is used only to recapture redacted
screenshots. Never run `generate` directly from unreviewed evidence.

## Final check

Before delivery, confirm: valid package, fifteen inspected previews, exact
revision installed, private status, no unrequested sharing, no source text in
evidence, draft, package, reports or logs. Never display asset bytes,
presentation content, a prompt, secret or token.
