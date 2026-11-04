# Shipped template packs

`premium` provides 25 unbranded compositions for a new presentation using theme
roles. Prefer this pack when no gallery is prescribed; usages, slots and budget
measurement: [premium-templates.md](premium-templates.md). `standard` remains
the restrained fallback, with its ten compositions detailed below. Backgrounds
alternate background/text roles: choose a contrasting pair and inspect the result.

Pack `standard`: 10 templates embedded in the `deck` binary (template files use
`format_version` 0.2.0, `graphique` 0.14.0, `tableau` 0.15.0). The reference deck
format version is the title of [format-cheatsheet.md](format-cheatsheet.md),
separate from template file versions.

Slot tables and ready-to-fill bindings in this file are generated from
`deck templates list --json` and `deck templates show standard/<id> --json`,
then enriched with usage, appearance and advice. Generation uses an empty,
isolated profile and verifies the 10 `standard` and 25 `premium` templates
against the shipped assets. Every embedded result has `source: "standard"`,
including the premium pack. Never generate this catalogue from a user library.
When in doubt or after a binary update, CLI output is authoritative: rerun
these commands rather than trusting this file.

**This file is not the machine's catalogue.** `standard` is the guaranteed
baseline everywhere; a user-installed pack or revisioned theme gallery adds
templates this file does not and will never describe. Count packs using
`deck templates list --json` before composing a deck, and never announce the
number of available templates based on this document.

**Measure budgets on the current deck before writing.** If
`template.budgets.measured` exists, use
`deck templates show standard/<id> --deck source.deck --json`, with
`--slide <slide-id>` for an existing slide and its exact revision. Slot and list
field budgets use an indicative corpus with the deck's resolved fonts; read
fallback warnings and retain a margin. Figures below are historical guidelines
with the default theme. No template clips or shrinks text. `deck lint --visual`
and `deck check` measure actual overflows; also inspect the PNG before delivery.

## Revisioned themes and provenance

This catalogue describes shipped packs `standard` and `premium`. A complete
theme has its own gallery with fifteen canonical archetypes and possible
variants. When a revisioned theme is selected, use that exact revision's
gallery; do not merge it with shipped packs or replace a missing template
with a fallback from another revision.

A new linked slide must copy the active pair into its binding: `theme_id` and
`theme_revision_id` are present together. An existing slide always retains its
pair. Activating another revision changes the suggested choice for future
slides without recoloring or regenerating existing ones. A deck can therefore
mix several themes and revisions without losing provenance.

To create and inspect a revisioned gallery, follow
`references/theme-compiler.md` directly from `SKILL.md`.

## Overview

| Template | Name | Required slots | Optional slots |
| --- | --- | --- | --- |
| `standard/titre` | Title | `titre` | `eyebrow`, `sous-titre` |
| `standard/statement` | Statement | `phrase` | `eyebrow` |
| `standard/contenu` | Content | `points`, `titre` | `corps`, `eyebrow` |
| `standard/cartes` | Cards | `cartes`, `titre` | `eyebrow` |
| `standard/process` | Process | `etapes`, `titre` | `eyebrow` |
| `standard/kpi` | KPI | `chiffres` | `eyebrow`, `titre` |
| `standard/graphique` | Chart | `donnees`, `titre` | `eyebrow` |
| `standard/tableau` | Table | `lignes`, `titre` | `entetes`, `eyebrow` |
| `standard/citation` | Quote | `auteur`, `citation` | `role` |
| `standard/cloture` | Closing | `etapes`, `message` | `contact`, `eyebrow` |

Typical deck skeleton (6 slides): `titre`, `statement` or `contenu` (the problem),
`cartes` (the offer), `process` (the method), `kpi` (evidence), `cloture` (decision).
Avoid using the same template twice consecutively when content allows variety.

The 25 shipped premium compositions are documented separately in
[premium-templates.md](premium-templates.md):

`premium/title-image`, `premium/statement`, `premium/takeaway-list`, `premium/approach-arch`, `premium/three-pillars`, `premium/image-full`, `premium/loop`, `premium/statement-light`, `premium/method-image`, `premium/cta-image`, `premium/section-divider`, `premium/content-text`, `premium/content-two-cols`, `premium/card-grid`, `premium/comparison`, `premium/before-after`, `premium/big-number`, `premium/stats`, `premium/quote`, `premium/case-study`, `premium/timeline`, `premium/roadmap`, `premium/checklist`, `premium/matrix-2x2`, `premium/process`.

## `standard/titre`: Title

Opening slide: eyebrow, large title and optional subtitle. The first slide of a deck.

**Appearance.** Light stone background. Small blue rule and blue mono eyebrow at
top left, very large bold left-aligned title in the center, discreet gray subtitle below.

**When to use.** Always slide 1, never elsewhere. The eyebrow carries context
(recipient, date, meeting type); the title carries the deck's promise.

| Slot | Type | Required | Bounds | Item fields / columns |
| --- | --- | --- | --- | --- |
| `eyebrow` | text | no |  |  |
| `sous-titre` | text | no |  |  |
| `titre` | text | yes |  |  |

Ready-to-fill binding (`binding_skeleton`):
```json
{
  "id": "titre",
  "pack": "standard",
  "slots": {
    "eyebrow": "",
    "sous-titre": "",
    "titre": ""
  }
}
```

**Advice.** Title: 2 lines is a hard ceiling, not a target. The box is 320 px high
for 128 px type: a third line runs under the subtitle and makes it unreadable.
With the default theme, two lines fit around 43 characters and break around 46,
depending on word length (word count predicts nothing: wrapping decides).
Inspect slide 1's PNG before any other check. Subtitle: one line. Eyebrow:
4 words maximum (e.g. “Proposal · July 2026”).

## `standard/statement`: Statement

A conviction in very large type, alone on the slide. To state a thesis or mark a transition.

**Appearance.** Light stone background. Blue rule and blue mono eyebrow, then a
huge bold statement over 1 to 2 lines. Plenty of space: the statement stands alone.

**When to use.** For the deck's thesis, a narrative pivot or a section divider.
One idea, expressed as a conviction.

| Slot | Type | Required | Bounds | Item fields / columns |
| --- | --- | --- | --- | --- |
| `eyebrow` | text | no |  |  |
| `phrase` | text | yes |  |  |

Ready-to-fill binding (`binding_skeleton`):
```json
{
  "id": "statement",
  "pack": "standard",
  "slots": {
    "eyebrow": "",
    "phrase": ""
  }
}
```

**Advice.** Statement: 15 words maximum, with a final period. No second sentence.

## `standard/contenu`: Content

Title, body text and a list of 1 to 5 key points. The general-purpose argument slide.

**Appearance.** Blue eyebrow and bold title at top left. Gray body in the left
column, points in the right column, each preceded by a small blue dash.

**When to use.** The default for arguments: findings, challenges, scope,
recommendations. If points are symmetrical objects (offers, options, pillars),
prefer `cartes`; if they form a sequence, prefer `process`.

| Slot | Type | Required | Bounds | Item fields / columns |
| --- | --- | --- | --- | --- |
| `corps` | text | no |  |  |
| `eyebrow` | text | no |  |  |
| `points` | list | yes | 1 to 5 | `texte` (required) |
| `titre` | text | yes |  |  |

Ready-to-fill binding (`binding_skeleton`):
```json
{
  "id": "contenu",
  "pack": "standard",
  "slots": {
    "corps": "",
    "eyebrow": "",
    "points": [
      {
        "texte": ""
      }
    ],
    "titre": ""
  }
}
```

**Advice.** Body: 1 to 2 sentences. Points: 8 words maximum each, preferably
3 to 4 points rather than 5. A point is not a sentence: no final period.

## `standard/cartes`: Cards

Row of 2 to 4 cards (label and optional detail) beneath a title. For offers, pillars or options.

**Appearance.** Bold title at top left. Row of white rounded cards, each with a
small blue rule, bold label and gray detail. Cards share width equally:
2 wide cards, 4 narrow cards.

**When to use.** Symmetrical comparable objects: parts of an offer, options,
pillars, before/after (2 cards), a team (name as label, role as detail).

| Slot | Type | Required | Bounds | Item fields / columns |
| --- | --- | --- | --- | --- |
| `cartes` | list | yes | 2 to 4 | `detail`, `label` (required) |
| `eyebrow` | text | no |  |  |
| `titre` | text | yes |  |  |

Ready-to-fill binding (`binding_skeleton`):
```json
{
  "id": "cartes",
  "pack": "standard",
  "slots": {
    "cartes": [
      {
        "detail": "",
        "label": ""
      },
      {
        "detail": "",
        "label": ""
      }
    ],
    "eyebrow": "",
    "titre": ""
  }
}
```

**Advice.** Label: 1 to 3 words. Detail: 2 short sentences maximum (even shorter
with 4 cards). Omit `detail` rather than adding filler: the card stays clean.

## `standard/process`: Process

Row of 2 to 6 numbered steps (number, label, optional detail). For a sequence, method or schedule.

**Appearance.** Bold title above. Row of steps: large blue mono number,
horizontal rule, bold label, gray detail below. Restrained, without cards.

**When to use.** Anything ordered in time: method, rollout plan, schedule,
engagement steps. The `numero` field is free text: “1”, “01”, “S1”, “J+30” work.

| Slot | Type | Required | Bounds | Item fields / columns |
| --- | --- | --- | --- | --- |
| `etapes` | list | yes | 2 to 6 | `detail`, `label` (required), `numero` (required) |
| `eyebrow` | text | no |  |  |
| `titre` | text | yes |  |  |

Ready-to-fill binding (`binding_skeleton`):
```json
{
  "id": "process",
  "pack": "standard",
  "slots": {
    "etapes": [
      {
        "detail": "",
        "label": "",
        "numero": ""
      },
      {
        "detail": "",
        "label": "",
        "numero": ""
      }
    ],
    "eyebrow": "",
    "titre": ""
  }
}
```

**Advice.** 3 to 4 steps is optimal. At 5 or 6, shorten labels (2 words) and
limit details to half a line, otherwise the row becomes unreadable.

## `standard/kpi`: KPI

Row of 2 to 4 large figures (value, label, optional detail). For results or metrics.

**Appearance.** Optional title above. Row of blocks: small blue rule, very large
numeric value, blue label, gray detail. White space does the work.

**When to use.** Quantified evidence: observed results, target metrics, orders
of magnitude. Every figure must be defensible aloud. If none is defensible
(generic offer deck, no client or pilot), do not invent one: replace the `kpi`
slide with `contenu` (benefits) or `statement`.

| Slot | Type | Required | Bounds | Item fields / columns |
| --- | --- | --- | --- | --- |
| `chiffres` | list | yes | 2 to 4 | `detail`, `label` (required), `valeur` (required) |
| `eyebrow` | text | no |  |  |
| `titre` | text | no |  |  |

Ready-to-fill binding (`binding_skeleton`):
```json
{
  "id": "kpi",
  "pack": "standard",
  "slots": {
    "chiffres": [
      {
        "detail": "",
        "label": "",
        "valeur": ""
      },
      {
        "detail": "",
        "label": "",
        "valeur": ""
      }
    ],
    "eyebrow": "",
    "titre": ""
  }
}
```

**Advice.** Value: short and typographic (“30 %”, “x3”, “4 sem.”), never a sentence.
Label: 2 to 3 words. Three figures tell a better story than one or four.

## `standard/graphique`: Chart

Title above a bar chart fed by a data slot (one category, one series).
For a quantified result or trend.

**Appearance.** Optional eyebrow, title, then a full-width vertical bar chart.
Series colors come from the theme palette, accent first, then `colors.extra`
(0.30.0, `"theme_palette": true` set by the app; no colors to assign);
the `serie_colors` override fixes one without changing the template and survives
regeneration. Values display without decimals. To add a unit on a linked slide,
add or edit the `graphe/value_labels` override with `suffix: " %"` or
`suffix: " €"`; suffixes do not convert numbers (full recipe in SKILL).
Labels use the theme's `colors.text` ink and `fonts.body` font, following theme
changes. The template retains the decimal point: in a `fr` deck, set binding
`"chart_labels": {"label_color": "$colors.text", "font_family":
"$fonts.body", "decimal_separator": ","}` (“3,4”), which the app sets from its gallery.

**When to use.** Changes or comparisons between figures ARE the message (one
series across categories: quarters, segments, years). For 2 to 4 separate key
figures, `kpi` remains better. For a richer chart (multiple series, lines, pie),
add a free `chart` element (see SKILL, Charts section).

Fill `donnees` like a `list` slot: an array of rows, each a `column -> string`
object. `categorie` carries the label; `valeur` the number (stored as a string,
parsed at instantiation). Fill `categorie`/`valeur`, add up to 12 rows.

| Slot | Type | Required | Bounds | Item fields / columns |
| --- | --- | --- | --- | --- |
| `donnees` | data | yes | 1 to 12 | `categorie` (category), `valeur` (series) |
| `eyebrow` | text | no |  |  |
| `titre` | text | yes |  |  |

Ready-to-fill binding (`binding_skeleton`):
```json
{
  "id": "graphique",
  "pack": "standard",
  "slots": {
    "donnees": [
      {
        "categorie": "",
        "valeur": "0"
      }
    ],
    "eyebrow": "",
    "titre": ""
  }
}
```

**Advice.** NEVER invent figures: data comes from the user. Short categories
(“T1”, “2024”). The template chart is single-series; to compare several series,
add a free `chart` element.

## `standard/tableau`: Table

Template schema 0.17.0 adds optional literal merge anchors and row weights.
Shipped copies keep their historical version. On a bound slide use full
`rows` cell objects and `row_weights` overrides to customize merges and heights.

Title above a table fed by a row slot (item, value, optional detail).
For budgets, schedules or structured comparisons.

**Appearance.** Optional eyebrow, title, then a full-width table: header row on
surface background (Poste / Valeur / Détail by default), discreet rules,
right-aligned value column. Cells contain TEXT (never converted into numbers:
“12 000”, “x3” and “4 sem.” pass through unchanged).

**When to use.** Naturally tabular content: budget, schedule, option comparison,
simple matrix. For figures to emphasize, `kpi`; for a trend, `graphique`.

| Slot | Type | Required | Bounds | Item fields / columns |
| --- | --- | --- | --- | --- |
| `entetes` | text_list | no | exactly 3 strings |  |
| `eyebrow` | text | no |  |  |
| `lignes` | list | yes | 2 to 10 | `detail`, `poste` (required), `valeur` (required) |
| `titre` | text | yes |  |  |

Ready-to-fill binding (`binding_skeleton`):
```json
{
  "id": "tableau",
  "pack": "standard",
  "slots": {
    "eyebrow": "",
    "lignes": [
      {
        "detail": "",
        "poste": "",
        "valeur": ""
      },
      {
        "detail": "",
        "poste": "",
        "valeur": ""
      }
    ],
    "titre": ""
  }
}
```

To customize the header, add `"entetes": ["Levier","Impact","Délai"]` to
`slots`. Without `entetes`, the fallback is “Poste / Valeur / Détail”; the
skeleton omits it. `titre` stays required. A present list must contain exactly
three strings; otherwise `deck validate` identifies the slot to fix. Do not set
a `rows` override: editing `lignes` then regenerating updates the body while
preserving headers. An old embedded template still takes priority: to use this
slot, explicitly replace only `templates/standard/tableau.json` with the new
template, then fill the slot and regenerate. Preserve existing human overrides.

**Advice.** NEVER invent figures. Short items, typographic values (“12 000”,
“2 semaines”). A missing `detail` leaves the cell empty. For a richer table
(column alignment, weights, per-cell style), add a free `table` element
(see the cheatsheet, Table element section).

## `standard/citation`: Quote

Highlighted quote with author and optional role. For testimonials or social proof.

**Appearance.** Large blue quotation marks at top left, large regular quote,
a blue rule below followed by bold author and gray role.

**When to use.** Client wording, testimonial, a phrase heard in a workshop.
The author is a real person or entity, never a generic phrase (“Our thesis”
is not an author). Verify permission before naming a client in a quote.

| Slot | Type | Required | Bounds | Item fields / columns |
| --- | --- | --- | --- | --- |
| `auteur` | text | yes |  |  |
| `citation` | text | yes |  |  |
| `role` | text | no |  |  |

Ready-to-fill binding (`binding_skeleton`):
```json
{
  "id": "citation",
  "pack": "standard",
  "slots": {
    "auteur": "",
    "citation": "",
    "role": ""
  }
}
```

**Advice.** Quote: 20 words maximum, direct speech, no quotation marks in the
text (the template draws them). Role: position + organization if useful.

## `standard/cloture`: Closing

Inverted closing slide: message, 1 to 3 next steps and optional contact.
The final slide of a deck.

**Appearance.** The pack's only dark slide: charcoal background, blue rule,
very large light message, next steps preceded by small blue dashes, blue
contact at the bottom.

**When to use.** Always the last slide, never elsewhere. No “Thank you” slide:
the message carries the requested decision; steps say what happens next.

| Slot | Type | Required | Bounds | Item fields / columns |
| --- | --- | --- | --- | --- |
| `contact` | text | no |  |  |
| `etapes` | list | yes | 1 to 3 | `texte` (required) |
| `eyebrow` | text | no |  |  |
| `message` | text | yes |  |  |

Ready-to-fill binding (`binding_skeleton`):
```json
{
  "id": "cloture",
  "pack": "standard",
  "slots": {
    "contact": "",
    "etapes": [
      {
        "texte": ""
      }
    ],
    "eyebrow": "",
    "message": ""
  }
}
```

**Advice.** Message: an action-oriented sentence (“We start with the audit.”).
Steps: concrete and dated if possible. Contact: an email, not a full signature.
