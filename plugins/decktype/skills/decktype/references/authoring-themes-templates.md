# Authoring: custom templates and legacy styles

This guide covers two local, manual artifacts: custom template packs
and legacy style files. To compile a complete theme with identity,
assets, immutable revision and its own gallery, follow
`references/theme-compiler.md` directly from `SKILL.md`.

The CLI is authoritative. Commands accept `--json` when their help says so. Exit
codes are `0` for success, `1` for invalid content and `2` for
usage, read or rendering errors.

## Legacy style

`deck theme new` creates a simple style file from the default palette and
overrides passed as flags. This compatibility format contains no assets,
gallery or revision history. Do not use it when the user requests
a complete theme.

```text
deck theme new --id nuit --name "Nuit" \
  --background "#0A0A0A" --surface "#141414" \
  --text "#F5F5F5" --accent "#F5A623" \
  --font-display "Space Grotesk" --font-body "Inter" \
  --font-mono "IBM Plex Mono" --out nuit.json
deck theme validate nuit.json --json
deck theme install nuit.json --json
deck theme list --json
deck theme show nuit --json
```

The ID is a lowercase ASCII slug. Installation stores the style in
the user library. It does not apply it to a deck or share anything.
`--font` sets both display and body fonts; `--font-display` and
`--font-body` take precedence over it.

To create a deck in these colors without installing a style, `deck new` accepts the
same role options: `deck new mon-deck.deck --title "Titre" --accent "#F5A623" --font "Inter"`
(Scaffold step in `SKILL.md`).

## Custom templates

A template is a declarative JSON file: typed slots and a tree of
parameterized elements. Its grammar is closed: token references, slot
bindings and repeated zones. It embeds no executable layout language.

### Tokens-only rule

Literal colors or fonts are forbidden in a template. Use
only the following references in compatible positions:

- colors: `$colors.background`, `$colors.surface`, `$colors.text`,
  `$colors.accent`;
- fonts: `$fonts.display`, `$fonts.body`, `$fonts.mono`.

`deck templates validate` and `deck templates install` reject literals.
Resolution uses the exact revision bound to the slide.

### Starting skeleton

```text
deck templates new --id ma-carte --name "Ma carte" --out ma-carte.json
```

The minimal file contains one required text slot and a title element. Extend it,
then validate it before installation.

### Slots

- `text`: a string, with optional `required`.
- `list`: a repeated zone with `min` and `max` bounds; each item field
  has type `text`.
- `data`: a table for a `chart` element, with category, series and bounds.

Required slots must have a value. Slot keys remain stable after
publication because decks preserve them in their bindings.

### Elements

Each element has a stable `key`, a `transform` in points and a `kind`:

- `text`: literal content, `$slots.<cle>` or `$item.<champ>`, with font
  and color tokens;
- `shape`: rectangle, ellipse, line, triangle, arrow, star or `path`,
  with fill and stroke tokens. Authoring rule: a STRAIGHT connector
  is declared as `line`, never as a stroked `path`. A `line`'s two points
  define its box, so a `transform` override is enough to correct it;
  a misoriented template `path` can only be straightened with a `path` override
  (0.18.0), since `transform` supports neither mirroring nor negative scaling.
  To convert an old `path` connector to `line`, recalculate the box from
  its two points (formula in [template connectors](template-connectors.md),
  `h = 24`), then remove the `path` field. Changing only the tag would paint the
  horizontal midline of the old box. Existing decks keep their embedded
  template copy and are corrected with the `path` recipe;
- `image`: bundle-relative asset path, `$slots.<cle>` or `$item.<champ>`
  (template schema 0.12.0). A missing optional text slot or missing item
  field does not instantiate the element, as with text; an unresolved
  reference (unknown slot, `$item.*` outside a repeated zone, `$colors.*`) makes
  the file invalid;
- `chart`: `$slots.<cle>` reference to a `data` slot.

In a repeated zone, a materialized key becomes `<slot>[i].<key>`. `w` and `h`
may be `"fill"` inside the zone.

### Minimal repeated zone

```json
{"repeat": {
  "slot": "cartes",
  "zone": {"x": 120, "y": 400, "w": 1680, "h": 500},
  "direction": "row",
  "gap": 40,
  "elements": [
    {"key": "fond", "transform": {"x": 0, "y": 0, "w": "fill", "h": "fill"},
     "kind": {"type": "shape", "shape": "rectangle",
              "fill": "$colors.surface", "stroke": null, "corner_radius": 16}},
    {"key": "nom", "transform": {"x": 32, "y": 32, "w": 400, "h": 60},
     "kind": {"type": "text", "content": "$item.nom",
              "font_family": "$fonts.display", "font_size": 36,
              "weight": "semibold", "color": "$colors.text", "align": "left"}},
    {"key": "logo", "transform": {"x": 32, "y": 120, "w": 240, "h": 160},
     "kind": {"type": "image", "asset": "$item.fichier", "fit": "contain"}}
  ]
}}
```

Declare a logo wall this way: the `list` slot has a `fichier` field per
entry, the image element reads it through `$item.fichier`, and the deck writes the `entry`
returned by `deck image add` (never a disk path). The field is optional:
an entry without `fichier` does not instantiate its image; the rest of the card remains.

### Validate, install, discover

```text
deck templates validate ma-carte.json
deck templates install ma-carte.json --pack atelier
deck templates list --json
deck templates show atelier/ma-carte --json
```

The `id` field must match the expected name and `--pack` is a slug. A user
pack takes precedence over a standard pack with the same identity. Never overwrite an
existing template without an explicit request.

## Slide provenance

A new template-bound slide copies the active pair into its binding:

```json
{
  "id": "ma-carte",
  "pack": "atelier",
  "theme_id": "<active_theme_id du deck>",
  "theme_revision_id": "<active_theme_revision_id du deck>"
}
```

`theme_id` and `theme_revision_id` are always present together. An existing
slide keeps its exact pair, even after another revision is activated.
Changing the active theme does not recolor, replace or regenerate any slide.

## Round-trip and verification

Table captures in template schema 0.17.0 keep literal `rows` as strings and add
optional `merges: [{"row":0,"col":0,"col_span":3,"row_span":1}]` and
`row_weights`. Covered positions are inferred from these anchors. For bound
slides, a `rows` override instead carries full cell objects, including spans
and `covered`; `columns` and `row_weights` can also be overridden. Keep unrelated
overrides intact. These overrides are normalized together after application.

Stable `key` values drive regeneration. Do not rename them in a template
already in use: manual overrides and selections would become orphaned.

Mandatory loop after authoring:

1. Validate the template.
2. Install it in a test pack.
3. Create a test deck with a binding carrying both theme IDs.
4. Run `deck validate`, then `deck regenerate` and `deck render`.
5. Inspect every PNG and correct the template, never the materialized cache.
