# `.deck` format cheatsheet (0.32.0)

Minimal copyable schemas. The title version is the mandatory reference for the entire skill: `capabilities.format_version` must be at least this version before using these recipes. The minimal `deck.json` example carries this version; other document examples do not exceed it. Template file versions are separate, and feature introduction versions remain historical.

## Bundle anatomy

A `.deck` is a zip archive:

```text
mon-deck.deck (zip)
├── deck.json      # single source of truth: deck, theme revisions, slides, elements
├── meta.json      # informational only, never required
├── templates/     # every embedded template, bound or unused (`deck templates remove`)
│   └── standard/cartes.json
└── assets/        # binaries (PNG, JPEG) referenced by image elements
    ├── logo.png
    └── fonts/     # embedded fonts (.ttf/.otf), auto-registered on open
        └── inter.ttf
```

Rendering reads only `slides[].elements`; `deck regenerate` explicitly materializes template bindings.
`assets/.decktype/` preserves the [outline (0.20)](story-outline.md), protections (0.21) and CSV snapshots `data-sources.json` (0.22). Keep their bytes, including unknown schemas: opening/regenerating never rereads a CSV. Recipes remap only known identities. [CSV: preview/resolve/apply](data-refresh.md) covers slot, chart, table and, since 0.31.0, text/text_slot with aggregate (sum/mean/min/max/count, format.decimals 0..12, format.decimal point/comma).

## Manipulate the zip

The working `deck.json` copy extracted beside the bundle is SINGLE-USE.
`deck regenerate` rewrites the bundle: the local copy immediately becomes
stale. Reading it again makes it seem that `regenerate` did nothing; zipping it
again injects the old `elements` over the bundle and recreates the divergence on
every iteration. Deleting it immediately after `zip` prevents this trap:

```bash
deck new mon-deck.deck --title "Titre du deck"   # 1 empty slide, brand: --background --text --accent --font
unzip -p mon-deck.deck deck.json > deck.json     # single-use working copy
# ... edit deck.json with the file tools ...
zip -q mon-deck.deck deck.json                   # replace the entry in the zip
rm deck.json                                     # the working copy dies here
deck regenerate mon-deck.deck                    # ALWAYS after a JSON patch
# NB: regenerate embeds a standard template missing from templates/ (slide added by patch)
deck validate mon-deck.deck --json
deck render mon-deck.deck --out slides-png
```

Read all state from the bundle (`deck inspect mon-deck.deck --json`, then
`unzip -p mon-deck.deck deck.json`), never from a local copy: extract again for every edit.

Work in the bundle's directory: `zip` puts the `deck.json` entry at the zip
root only when the relative path is the bare filename.

**Recognize this symptom.** `deck validate` repeatedly reports “materialized elements diverge”
although `deck regenerate` just announced `slide N: regenerated`, or a materialized
element retains old text after a slot patch: this is a stale working copy zipped
over the bundle, not the CLI. Extract again from the bundle
and start there; never conclude that `regenerate` is broken without rereading the bundle.

Add a local image (preferred to zip manipulation: its type is read from the
bytes, content is deduplicated, and the entry to copy into `asset` is displayed):

```bash
deck image add mon-deck.deck photo.png    # -> assets/photo.png, entry displayed
deck image list mon-deck.deck --json      # entries, dimensions, slides, missing assets
```

Embed a font (preferred to zip manipulation: the command displays the
family read from the file, which is the value to write in `font_family`):

```bash
deck fonts add mon-deck.deck police.ttf   # -> assets/fonts/police.ttf, family displayed
deck fonts list mon-deck.deck --json      # entries, families, uncovered families
```

## Generate a ULID

Every slide or free element `id` is a ULID (26 characters, Crockford alphabet,
without I, L, O, U). Never invent one manually or change an existing ID:

```bash
python3 -c "
import os, time
alph = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
t = int(time.time() * 1000)
ts = ''.join(alph[(t >> (5 * i)) & 31] for i in range(9, -1, -1))
print(ts + ''.join(alph[b & 31] for b in os.urandom(16)))"
```

Element `id` values on a bound slide are set by `deck regenerate`: do not write them.

## Minimal `deck.json` (output of `deck new`)

```json
{
  "format_version": "0.32.0",
  "id": "01KWJ0HRS9B4PS1PD2R50G3PG3",
  "title": "Essai",
  "language": "fr",
  "size": {"w": 1920.0, "h": 1080.0},
  "theme": {
    "id": "default", "name": "Default",
    "colors": {"background": {"r": 245, "g": 242, "b": 234, "a": 255},
               "surface": {"r": 255, "g": 255, "b": 255, "a": 255},
               "text": {"r": 24, "g": 27, "b": 41, "a": 255},
               "accent": {"r": 15, "g": 98, "b": 254, "a": 255}},
    "fonts": {"display": "Sora", "body": "Inter", "mono": "JetBrains Mono"}
  },
  "active_theme_id": "default",
  "active_theme_revision_id": "01KZ513V000DEFA7THEME00000",
  "theme_revisions": [
    {"theme_id": "default", "revision_id": "01KZ513V000DEFA7THEME00000",
     "style": {
       "id": "default", "name": "Default",
       "colors": {"background": {"r": 245, "g": 242, "b": 234, "a": 255},
                  "surface": {"r": 255, "g": 255, "b": 255, "a": 255},
                  "text": {"r": 24, "g": 27, "b": 41, "a": 255},
                  "accent": {"r": 15, "g": 98, "b": 254, "a": 255}},
       "fonts": {"display": "Sora", "body": "Inter", "mono": "JetBrains Mono"}}}
  ],
  "slides": [
    {
      "id": "01KWJ0HRSA0ZM01JQ5EM21JQA1",
      "size": {"w": 1920.0, "h": 1080.0},
      "background": {"color": {"r": 245, "g": 242, "b": 234, "a": 255}},
      "elements": [],
      "notes": null
    }
  ]
}
```

## Template-bound slide (write this yourself)

The exact shape to insert into `slides`: filled binding, empty `elements`, `background`
and theme IDs copied from the deck. `deck regenerate` materializes the elements.

```json
{
  "id": "<ULID neuf>",
  "size": {"w": 1920.0, "h": 1080.0},
  "background": {"color": {"r": 245, "g": 242, "b": 234, "a": 255}},
  "elements": [],
  "notes": null,
  "template": {
    "pack": "standard",
    "id": "cartes",
    "theme_id": "<active_theme_id du deck>",
    "theme_revision_id": "<active_theme_revision_id du deck>",
    "slots": {
      "titre": "Notre offre",
      "cartes": [
        {"label": "Audit", "detail": "Cartographier les usages."},
        {"label": "Formation"}
      ]
    }
  }
}
```

Slot values: a `text` slot takes a string (`\n` is allowed), a `list` slot
takes an array of objects; `text_list` takes an array of strings. An absent optional
slot does not instantiate the element (clean); an empty string instantiates an empty element.

`data` slot (`standard/graphique`, feeds a `chart`): **same shape as a `list`**, an array of rows. `category` carries the label, `series` the numbers as strings; a nonnumeric cell becomes `0` (warning).
This template shows values with no decimal places; other charts keep their invisible default. Example `donnees`:

```json
"slots": {
  "titre": "Chiffre d'affaires",
  "donnees": [
    {"categorie": "T1", "valeur": "12"},
    {"categorie": "T2", "valeur": "18"},
    {"categorie": "T3", "valeur": "15"}
  ]
}
```

Unit on a bound slide: add to `template.overrides` (without erasing existing edits) `{"key":"graphe","prop":"value_labels","value":{"visible":true,"decimals":0,"suffix":" %"}}`. The suffix is displayed without conversion; replace `" %"` with `" €"` if needed.

## Slot patches (content edits)

To change the text, icon name or image of a slot-fed element
(`content`, `name`, `asset`), edit THE SLOT VALUE in `template.slots` (or
the list item field), never the materialized field (a rendering cache, overwritten
on regeneration), never a `content`/`name`/`asset` override (which would mask the slot).

```json
"slots": {"titre": "Notre offre revisee"}
```

Then `zip`, `deck regenerate`, `deck render`.

## Overrides (`template.overrides`)

An override records a style or position edit, or deletion, on an instantiated
element identified by its key (`titre`, `cartes[1].fond`...). Two forms:

```json
{"key": "cartes[1].fond", "prop": "fill", "value": {"r": 15, "g": 98, "b": 254, "a": 255}}
```

```json
{"key": "cartes[0].detail", "deleted": true}
```

**Closed list of overridable props** (any other prop is preserved but inert):

| `prop` | Applies to | Value |
| --- | --- | --- |
| `transform` | all | COMPLETE Transform object (`x`, `y`, `w`, `h`, `rotation`) |
| `opacity` | all | number 0.0 to 1.0 |
| `locked` | all | boolean |
| `group` | all | group ULID, or null to ungroup (0.18.0: the ONLY way to group a bound element; see “Groups and clipping”) |
| `bleed` | all | boolean, intentional bleed (0.25.0: the ONLY way to mark a bound element); see [intentional bleed](bleed.md) |
| `content` | text | string (only an element NOT bound to a slot) |
| `runs` | text | COMPLETE TextRun[] (0.27.0): explicit literal text and attributes, slots masked; absent attributes inherited from the block, whose color and font can follow the theme; `content` = their text unless overridden by `content`; for a fixed template segment, edit a slot-fed segment in its slot |
| `font_family` | text | string |
| `font_size` | text | number |
| `weight` | text | "light", "regular", "medium", "semibold", "bold" |
| `align` | text | "left", "center", "right" |
| `justify` | text | boolean, default false (0.19.0); see [alignment](text-alignment.md) for the atomic patch and older-reader fallback |
| `color` | text, icon | Color |
| `fill` | shape | Color or null |
| `fill_gradient` | shape | complete Gradient object, or null to remove the gradient (0.23.0); see [template gradients](gradient-overrides.md), independent of `fill` |
| `stroke` | shape | `{"color": Color, "width": f64}` or null |
| `corner_radius` | shape, image (0.25.0) | number; on an image, null or <= 0 clears it |
| `shadow` | shape | `{"color": Color, "blur": f64, "dx": f64, "dy": f64}` or null (drop shadow; shadow opacity is the alpha of `color`) |
| `path` | shape | `{"commands": [...]}` box-normalized 0..1 (0.18.0): replaces a template `path`'s geometry, the only way to straighten a misoriented connector (`transform` supports neither mirroring nor negative scaling); never null |
| `stroke_dash` | shape | `[on, off]` in points, or null for a solid stroke (0.18.0) |
| `link` | text, shape, image | URL `http://`, `https://`, `mailto:`, or `null` to remove the link (0.29.0) |
| `asset`, `fit`, `crop`, `mask` | image | asset: string `assets/...`; since 0.25.0: fit `cover`/`contain`/`fill`, crop Rect normalized to 0..1 (positive size) or null, mask `circle`/`none` |
| `name` | icon | string, registry name (0.18.0) |
| `stroke_width` | icon | absolute number in points (0.18.0) |
| chart props | chart | `chart_kind`, `orientation`, `stacking`, `categories`, `series`, `serie_colors` ((Color or null)[] by series index, 0.30.0: recolors without freezing slot data, applied after `series`, null keeps the palette), `bar_width_ratio`, `corner_radius`, `inner_ratio`, `area`, `area_opacity`, `value_labels`, `label_size`, `label_color` (Color or null), `font_family`, `decimal_separator` (0.24.0), `legend`, `axis_x`, `axis_y` (values: contract, sections 4.6 and 5.3; full object and array payloads) |

`transform` is a complete object: copy all 5 fields from the materialized element and change only what moves. A partial object is invalid.

An override whose key has disappeared (shortened list) is orphaned: preserved and inert, it applies again if the key returns.
Never remove an existing override you did not create yourself: these are the human's manual edits.

### Correct a template connector
On a BOUND element, `from`/`to` have no effect: regeneration erases them. A
misplaced connector is corrected with overrides, never in `elements`, against the
bundle's EMBEDDED template (which takes priority over the library). Diagnostics, existing
overrides and verification: [template connectors](template-connectors.md).

For a `line`: a `transform` override at full precision (rounding moves the ends):

    w = hypot(to.x - from.x, to.y - from.y)          h = 24 (grab band)
    rotation = degrees(atan2(to.y - from.y, to.x - from.x))
    x = (from.x + to.x)/2 - w/2                      y = (from.y + to.y)/2 - h/2

For an old two-point `path`: `transform` = segment bounding box (rotation 0,
`w`/`h` floored at 8), plus `path` placing the ends in `0..1`. From (1500, 900) to (975, 845):

```json
{"key": "conn2", "prop": "transform",
 "value": {"x": 975.0, "y": 845.0, "w": 525.0, "h": 55.0, "rotation": 0.0}},
{"key": "conn2", "prop": "path", "value": {"commands": [
  {"op": "move_to", "x": 1.0, "y": 1.0}, {"op": "line_to", "x": 0.0, "y": 0.0}]}}
```

## Free slides and free elements

A slide without a `template` field is free: its elements are handwritten
(each with a fresh ULID). An element without `template_key` on a bound slide
is also free: regeneration never touches it.

```json
{
  "id": "<ULID neuf>",
  "transform": {"x": 160.0, "y": 640.0, "w": 1600.0, "h": 160.0, "rotation": 0.0},
  "opacity": 1.0, "locked": false,
  "kind": {
    "type": "text",
    "content": "Lancement produit",
    "font_family": "Inter",
    "font_size": 64.0,
    "weight": "bold",
    "color": {"r": 24, "g": 27, "b": 41, "a": 255},
    "align": "left"
  }
}
```

The seven `kind` values: `text` (above), `shape`, `image` and `icon` (below; names
and placement rules in `icons.md`), `chart` and `table` (next sections), `decor` (contract 4.5):

```json
{"type": "shape", "shape": "rectangle",
 "fill": {"r": 255, "g": 255, "b": 255, "a": 255},
 "stroke": {"color": {"r": 15, "g": 98, "b": 254, "a": 255}, "width": 2.0},
 "corner_radius": 12.0}
```

```json
{"type": "image", "asset": "assets/logo.png", "link": "https://example.com"}
```

```json
{"type": "icon", "name": "check", "color": {"r": 15, "g": 98, "b": 254, "a": 255}, "stroke_width": 2.0}
```

`shape` accepts `rectangle`, `ellipse`, `line`, `triangle` (isosceles, pointing up),
`arrow` (right-pointing arrow, shaft + head filling the box) and `star` (five-pointed
star inscribed in the box). An unknown tag is never an error: it is
preserved unchanged and rendered as a neutral placeholder (dashed box).
The `elements` array order is the painting order (first is underneath).

A `line` is a segment between two points: write `"from"` and `"to"` in
slide points, never a length and angle.

```json
{"type": "shape", "shape": "line",
 "from": {"x": 200.0, "y": 300.0},
 "to": {"x": 900.0, "y": 700.0},
 "stroke": {"color": {"r": 24, "g": 27, "b": 41, "a": 255}, "width": 3.0}}
```

The two points are authoritative: `transform` is recalculated from them on open,
so any plausible box suffices (the segment bounding box is the obvious choice). They come as a pair: `from` without `to` is ignored and `deck validate`
reports it. Height `h` remains the editor's grab band, with no effect on the stroke.
Dashes `stroke_dash` `[on, off]` (`line`, `path`): each dash gains a round cap of half the stroke width on either side, so `[0, 2*epaisseur]` gives round dots and `[epaisseur, epaisseur]` touching dashes (identical in rendering and PPTX).

A shape accepts an optional `"shadow"` field (drop shadow, format 0.13.0): `{"color": {"r": 0, "g": 0, "b": 0, "a": 64},
"blur": 24.0, "dx": 0.0, "dy": 8.0}`; opacity = alpha of `color` (subtle below ~a: 80). It is the blurred and offset box
(exact for `rectangle`, rounded halo for `ellipse`, approximate otherwise); it does not rotate with the shape.
Links (format 0.29.0): optional `"link"` field on a `text`, `shape`, `image` or a run in `runs`
(`{"text": "le site", "link": "https://example.com"}`; bound: `{"key": "titre", "prop": "runs", "value": [{"text": "le site", "link": "https://example.com"}]}`). Only `https://`, `http://` and `mailto:` are accepted, without spaces;
any other scheme is a `deck validate` error. No visual effect: style linked text yourself (`color`, `weight`).
Clickable in presentation without advancing, PDF annotation, PPTX link. Bound element: `link` override, never in `elements`; linked segments through a complete `runs` override. `runs[].link` takes precedence over `kind.link`.

### Groups and clipping (format 0.15.0; `group` on a bound element in 0.18.0)

Two optional envelope fields the agent MAY write on a FREE
element. On an element with `template_key`, NEVER write them in `elements` (regeneration
would lose them; `deck validate` reports this for `group`): since 0.18.0,
a bound element is grouped through one `{"key": "<template_key>", "prop": "group",
"value": "<ULID>"}` override per member, reapplied on every regeneration; `clip` remains
reserved for free elements. Z-contiguity is guaranteed only for an entirely free group.

- `"group": "<ULID>"`: slide elements sharing this ULID form
  a group (the app selects, moves and scales them together). The
  `elements` list stays flat and z-order is unchanged. Generate ONE ULID per
  group and apply it to at least two elements (`deck validate` reports
  a single-member group).
- `"clip": {"commands": [...]}`: a box-normalized clipping path (0..1 within the
  element's box, same `move_to`/`line_to`/`cubic_to`/`close` grammar as
  a shape's `path` field). The element is rendered only inside
  the path (star-shaped photo, text in a circle...). An empty path clips
  nothing (validation warning).

`deck inspect --json` exposes `groups` and `clipped` per slide. Boolean operations
(shape union/subtraction) have no format representation: do not simulate them.

## Chart element

A minimal chart takes 4 lines of `kind` (all styling has defaults, including
colors: the contract's fixed palette by series index; a bound chart uses the theme palette):

```json
{"type": "chart", "kind": "bars",
 "categories": ["T1", "T2", "T3"],
 "series": [{"label": "CA", "values": [12.0, 18.0, 15.0]}]}
```

Complete example: lines with area, 2 styled series, percentage value labels,
bottom legend, bounded Y axis and title:

```json
{
  "id": "<ULID neuf>",
  "transform": {"x": 200.0, "y": 260.0, "w": 1520.0, "h": 640.0, "rotation": 0.0},
  "opacity": 1.0, "locked": false,
  "kind": {
    "type": "chart",
    "kind": "lines",
    "categories": ["Jan", "Fev", "Mar", "Avr"],
    "series": [
      {"label": "Croissance", "values": [2.1, 3.4, 4.0, 5.2],
       "points_visible": true, "point_size": 10.0},
      {"label": "Objectif", "values": [2.5, 3.0, 3.5, 4.0], "dash": "dashed",
       "color": {"r": 82, "g": 82, "b": 82, "a": 255}, "stroke_width": 2.0}
    ],
    "area": true, "area_opacity": 0.2,
    "label_color": {"r": 24, "g": 27, "b": 41, "a": 255}, "font_family": "Inter", "decimal_separator": ",",
    "value_labels": {"visible": true, "decimals": 1, "suffix": " %"},
    "legend": {"visible": true, "position": "bottom"},
    "axis_y": {"visible": true, "title": "Croissance", "min": 0.0, "max": 6.0, "grid": true}
  }
}
```

Families and options: “Charts” section in `SKILL.md` (`pie` = one SERIES per
slice, `scatter` = `points` instead of `values`); exhaustive fields: contract 4.6.
Labels (0.24.0): copy theme `colors.text`/`fonts.body` into `label_color`/
`font_family`, and `"decimal_separator": ","` in a `fr` deck (otherwise 3.4); a chart
binding carries `"chart_labels"` ($colors.text, $fonts.body, "," in `fr`, `"theme_palette": true`, contract 6.3). Each
template chart field is overridden by prop (5.3; COMPLETE `series` and objects).

## Table element (format 0.14.0)
`standard/tableau`: required `titre`, body `lignes` (2 to 10 poste/valeur/detail objects), optional `"entetes": ["Levier","Impact","Délai"]`, exactly three strings (`text_list`). Without this slot: “Poste / Valeur / Détail”. Editing `lignes` then regenerating preserves the header without a `rows` override. Template 0.15.0: `labels: "$slots.entetes"`, `labels_default` for fallback; materialized cells stay in `rows`. A present invalid value does not use the fallback.
A minimal table takes three lines of `kind`: columns (optional,
derived from rows when absent) and rows of text cells. All styling has
defaults; the first row is the header (`header_rows` defaults to 1):

```json
{"type": "table",
 "columns": [{"weight": 2.0}, {"weight": 1.0, "align": "right"}],
 "rows": [
   [{"text": "Poste"}, {"text": "Budget"}],
   [{"text": "Audit"}, {"text": "12 000"}]
 ]}
```

Guidelines:

- Minimal cell: `{"text": "..."}`. Optional styling: `align` (overrides column), `emphasis` (header weight), `fill` (background), `text_color` (cell ink, otherwise its band's ink; 0.24.0).
- Cells contain TEXT: “12 000”, “x3”, “4 sem.” pass through unchanged, with no numeric conversion.
- Rectangular invariant: every row has `columns.length` cells; the
  reader normalizes on open (short rows padded, long rows truncated),
  but write a rectangular table from the start.
- Widths: relative `weight` values normalized to the element width. Optional `row_weights` distribute its height proportionally; absent or empty means equal rows.
- Since 0.32.0 anchors carry `col_span`/`row_span` (default 1); other positions remain with `covered: true`. Only anchors own visible text/style. `deck validate` warns on repairs.
- Header example: `[{"text":"Summary","col_span":3},{"text":"","covered":true},{"text":"","covered":true}]`.
- Element styling: `border` (`{color, width}`, absent = no rules),
  `header_fill`, `body_fill`, `header_text_color`, `text_color`, `font_family`
  (empty = sans generic), `font_size` (18), `cell_padding` (8), `header_rows` (1),
  `header_cols` (0).
- On a template table element, override props are `rows`,
  `columns`, `row_weights`, `header_rows`, `header_cols`, `border`, `header_fill`, `body_fill`,
  `header_text_color`, `cell_padding`, `font_family`, `font_size`, `text_color`
  (complete payload, contract section 5.3). Full details: section 4.7 of the
  contract (`docs/format/deck-v0.md`).

## Custom theme

The active theme is the root `theme` mirror, identified by `active_theme_id` and
`active_theme_revision_id`. The `theme_revisions` registry contains
`{theme_id, revision_id, style}` snapshots. Multiple themes and multiple revisions of
the same theme can coexist in one deck.

A new bound slide must always copy both active IDs into
`template.theme_id` and `template.theme_revision_id`. An existing slide keeps its
exact pair. Changing the active theme never recolors or regenerates any slide.
`deck regenerate` resolves each binding's exact pair; an unknown pair
is an error, never a fallback to the active theme. Old bindings
without both fields use the root mirror for compatibility.

Each `style` has 4 color roles (`background`, `surface`, `text`, `accent`), 3 font roles
(`display`, `body`, `mono`) and, in 0.30.0, `colors.extra`: at most 8 `{"name", "color"}` entries, read with `$colors.extra.<name>`
(accent fallback and warning if missing). Editing the active revision's style then regenerating recolors only slides bound to that exact revision.

Also change `slides[].background.color`: slide backgrounds are not re-derived from
the theme by regeneration (only elements are).

## `deck validate` diagnostics

Exit code 1 if at least one error; warnings leave code 0. `--json` output:

```json
{"file": "bad.deck", "valid": false, "errors": 2, "warnings": 0,
 "diagnostics": [
   {"file": "deck.json", "path": "/slides/0/template/slots/cartes",
    "severity": "error",
    "message": "slot \"cartes\" has 1 item(s), expected between 2 and 4"}
 ]}
```

Errors (always fix): empty required slot, wrong type, out-of-bounds list, missing required
item field, missing or invalid template, visible image missing from the bundle, rejected `link` (element or `link`/`runs` override).

Common warnings: “materialized elements diverge from the template binding” means
`deck regenerate` is missing after a patch. Unknown slot key, orphaned override, inert prop
or “unknown field” (lost on rewrite): data with no effect; check for a typo.

## Custom template packs

A user pack lives in `~/Library/Application Support/Decktype/templates/<pack>/`,
one JSON file per template (`<id>.json`, file `id` equal to the name). The grammar
is in spec section 6: typed slots, parameterized elements with
`$colors.*` (including `$colors.extra.<name>`), `$fonts.*`, `$slots.*`, `$item.*` references, equally distributed repeated zones.
Start from a standard template: `deck templates show standard/cartes --json`
returns its slots, and `deck templates list` lists the installed catalogue.

Check a new pack: `deck templates list` must show it, then create a test deck bound to
the new template, run `deck validate`, `deck regenerate`, `deck render` and inspect the PNG. A saved
bundle embeds a template copy: the deck remains portable even if the pack is not installed elsewhere.

## Essential semantics

- **Opening never regenerates.** Every `deck.json` patch must be followed by
  `deck regenerate`, otherwise rendering shows the old state.
- **A binding keeps its exact theme.** Never remove its
  `theme_id` and `theme_revision_id` or replace them with the active pair.
- **Changing the active theme touches no slide.** Only new bindings
  capture the new active pair.
- **The slot value is authoritative.** Materialized `content` is only a cache.
- **Free elements survive everything.** Regeneration never touches them.
- **Overrides survive regeneration.** This is the human/agent round-trip
  contract: the app writes overrides, the skill writes slots, neither
  overwrites the other.
- **A deleted element** (`deleted: true`) stays deleted while its override exists.
