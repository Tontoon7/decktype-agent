# Intentional bleed (format 0.25.0)

`"bleed": true` on an element envelope means that it extends beyond the canvas ON PURPOSE:
a diagonal stripe, a circle cropped by the edge, a full-frame photo extending outside.
The `off_canvas` rule in `deck lint` no longer flags it, even when entirely outside.

## What the field does and does not do

- Omitted when `false`: an unmarked element emits no `bleed` key
  and retains its element JSON. The bundle does change on save:
  `format_version` moves to the version announced by `deck capabilities --json` and `meta.json` (generator, timestamp)
  is rewritten, as on every save.
- No effect on rendering, hit-testing or export (PNG, PDF, PPTX).
- Only `off_canvas` reads it. Other lint rules (dashes, empty blocks, breathing
  room, contrast) apply to a marked element as they do to any other.
- A `decor` is already exempt from `off_canvas` without a marker: it is a texture
  intended to be cropped by the canvas.

## Free element

Write the field in `elements`, alongside `opacity` and `locked`:

```json
{"id": "<ULID>",
 "transform": {"x": -340.0, "y": 430.0, "w": 2600.0, "h": 220.0, "rotation": -12.0},
 "opacity": 1.0, "locked": false, "bleed": true,
 "kind": {"type": "shape", "shape": "rectangle",
          "fill": {"r": 200, "g": 40, "b": 40, "a": 255}, "stroke": null}}
```

## Bound element (with a `template_key`)

NEVER write `bleed` in `elements`: `deck regenerate` rebuilds
the element from the template and removes the marker (`deck validate` reports
the divergence). Use an override, reapplied on every regeneration:

```json
{"key": "<template_key>", "prop": "bleed", "value": true}
```

Then run `deck regenerate` and `deck validate`, as for any override.

## When not to mark an element

Never mark content (text, numbers, logos, charts, tables) just to silence
`off_canvas`: content cropped by the edge is unreadable. Reposition it.
Only mark a graphic element whose cropping is intentional.

## Older readers

A reader older than 0.25.0 ignores the field and renders identically, but
loses it on rewrite: a free element loses its marker; a bound element
recovers it on the next `deck regenerate` thanks to its override.
