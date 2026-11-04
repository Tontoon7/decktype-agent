# Template gradients (format 0.23.0)

On a BOUND shape whose template sets a `fill_gradient`, the gradient takes
precedence when rendered: a `fill` override alone has no visible effect. Edit
or remove the gradient with a `fill_gradient` override, added to
`template.overrides` without changing `elements` or existing edits.

Replace the gradient: complete `kind` + `stops` payload, literal `Color`
values including alpha (`$colors.*` are not resolved in an override).
In the same patch, add a `fill` override equal to the first
stop: this is the fallback for readers that do not render gradients.

```json
[
  {"key": "veil", "prop": "fill_gradient", "value": {
    "kind": {"type": "linear", "angle": 90.0},
    "stops": [
      {"offset": 0.0, "color": {"r": 15, "g": 98, "b": 254, "a": 192}},
      {"offset": 1.0, "color": {"r": 15, "g": 98, "b": 254, "a": 0}}]}},
  {"key": "veil", "prop": "fill", "value": {"r": 15, "g": 98, "b": 254, "a": 192}}
]
```

`angle` is in degrees, clockwise: `0` runs left to right, `90` top to bottom. A
radial gradient uses `"kind": {"type": "radial", "cx": 0.5, "cy": 0.5, "radius": 1.0}`
(center normalized to the box, radius as a fraction of its half-diagonal).

Remove the gradient for a flat color: `null`, plus the desired `fill`.

```json
[{"key": "veil", "prop": "fill_gradient", "value": null},
 {"key": "veil", "prop": "fill", "value": {"r": 15, "g": 98, "b": 254, "a": 255}}]
```

`fill` and `fill_gradient` are independent, regardless of order: changing
one never changes the other. `fill_gradient: null` alone reveals the existing
`fill`; removing this override would restore the template gradient. A
malformed value is preserved but inert; on an element other than `shape`,
the override is inapplicable (`deck validate` warning). A reader older
than 0.23.0 preserves the override and renders the materialized elements, but
ignores it during regeneration.

Then `zip`, `deck regenerate`, `deck validate`, `deck render`, and inspect the PNG.
