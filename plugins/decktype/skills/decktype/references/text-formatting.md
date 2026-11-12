# Underline, highlight, lists and paragraph spacing (format 0.34.0)

These text fields are read, clamped and kept by every 0.34.0 reader, but
rendering, PDF/PPTX export and the editor do not draw them yet: do not rely
on their visual effect before the CLI announces it. Absent fields keep the
exact previous rendering; never write them with their default value.

Block (`kind` of a `text` element):

- `underline`: boolean, default false.
- `highlight`: Color behind the glyphs, absent = none.
- `paragraphs`: one object per `\n`-separated paragraph of the text, in
  order. A missing entry is the default; an extra entry is kept, without
  effect. `{}` keeps the block behavior for that paragraph.

```json
{"type": "text", "content": "Objectifs\nCroissance\nMarge",
 "font_family": "Inter", "font_size": 28.0, "weight": "regular",
 "color": {"r": 24, "g": 27, "b": 41, "a": 255}, "align": "left",
 "paragraphs": [{"line_spacing": {"points": 40.0}},
                {"list": {"kind": "bullet", "level": 1}},
                {"list": {"kind": "number", "scheme": "roman_upper_period", "start": 2}}]}
```

- `list`: `{"kind": "bullet", "glyph": "•", "family"?: "<font>"}` (glyph
  default `•`, family default = the block font) or `{"kind": "number",
  "scheme": "arabic_period", "start": 1}`; `scheme` is one of
  `arabic_period`, `arabic_paren`, `alpha_lower_period`, `alpha_upper_period`,
  `roman_lower_period`, `roman_upper_period`. `level` 0..8 (default 0),
  `start` 1..32767.
- `line_spacing`: `{"points": n}` (absolute, 1..1584) or `{"proportion": n}`
  (multiple of the font's natural line height, 0.25..10). It wins over the
  block `line_height`, which stays a multiple of `font_size`.
- Out-of-range values are clamped on read; an unknown `kind`, `scheme` or
  spacing key is read as absent, never an error.

Runs (`runs[]`): `underline` true/false (absent = inherit the block);
`highlight` has three states: absent inherits the block highlight, `null`
removes it on this span, a Color sets it.

Bound elements: write run attributes through the complete `runs` override.
Block styles have their own overrides (0.34.0): `italic`, `underline`,
`tracking`, `line_height`, `valign`, `highlight` and a COMPLETE `paragraphs`
list, literal and in slide points, never scaled by the template.
Template schema 0.19.0 accepts the same fields on template texts: `highlight`
takes a `$colors.*` token, `paragraphs` are literal and their `points`
scale with the slide.
