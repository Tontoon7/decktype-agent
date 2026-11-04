# Icons: find the name, place the element

The `icon` element (format 0.12.0) places a vector icon from Decktype's embedded
registry (the vendored Lucide library, normalized to paths), stroked in
`color` and centered as a SQUARE in its box (a non-square box does not distort it).
`stroke_width` is absolute, in points, and defaults to 2.0 when omitted, which
is too thin once the box exceeds 32 points: write it explicitly (see the
conventions below).

```json
{"type": "icon", "name": "check", "color": {"r": 15, "g": 98, "b": 254, "a": 255}, "stroke_width": 2.0}
```

## Find the name

The embedded registry contains **the entire vendored Lucide library**, plus old
Lucide names (aliases) that render the renamed icon. There are over a thousand:
no list fits in a reference, and any copied list becomes inaccurate at the
first update. **The command is the source of truth**, never memory:

```sh
deck icons list --query growth --limit 20 --json   # from intent to names
deck icons list --query rocket --limit 5           # human output: name, then tags
deck icons list --json                             # full registry, including provenance
```

The `--json` output contains a `registry` header (source, version, license, count)
and an `icons` array of `{"name": ..., "tags": [...]}`. `name` is the value to
write in the `.deck`, unchanged.

- **Query in ENGLISH.** Tags come from the Lucide package and are English
  (`growth`, `money`, `time`, `warning`, `people`...). A French query returns
  nothing: translate the intent first.
- `--query` filters both names AND tags; it is case-insensitive.
  `matched` gives the number of matching icons, `registry.count` the total in
  the registry, even when `--limit` truncates the output.
- An old Lucide name returns its canonical name (`--query home` returns
  `house`): write that canonical name.
- No matches? Try a synonym or a more general word (`chart` before
  `scatter`, `arrow` before `northeast`). Never invent a name.

An unknown name is never fatal: rendering draws a dashed box and
`deck validate` reports it (warning “is not in the registry”) **suggesting the
closest names**. Read this warning and correct the name: this is the shortest
loop for finding a name.

## Place an icon

Two approaches, in this order of preference.

1. **Through a template slot**, when one is declared (`"icon": {"type": "text"}`
   feeding `"name": "$item.icon"` or `$slots.icon`): write the NAME as the
   slot or item field value, never a path. A missing optional slot
   does not instantiate the element: this is the normal way to omit an icon
   from an entry. Never delete a slot-fed icon, and never
   override its `name` (see below).
2. **Free element** otherwise, including on a bound slide: regeneration never
   touches free elements, so an icon placed next to a template
   survives every `deck regenerate`. Use a complete element with a fresh ULID.

### Size, stroke and color conventions

The icon is centered as a SQUARE in its box: a non-square box does not distort
it, but leaves empty space. Writing a square box avoids incorrect reasoning about
position.

- **Size**: 48 to 96 points per side. App insertion uses 96,
  which is appropriate for an icon conveying an idea on its own; 48 to 64 for
  an icon accompanying a line of text.
- **Stroke**: `stroke_width` is ABSOLUTE, in points; it does not follow
  box resizing (contract 4.5). The product convention is one
  sixteenth of the side: 6.0 for a 96-point box, 3.0 for a 48-point box. Keep
  one ratio throughout a deck so icons have the same visual weight
  across slides. Never reduce the stroke to zero: an icon
  consists ONLY of its stroke, so zero makes it invisible.
- **Color**: use a theme role, never an invented color. Use the theme accent
  for a focal icon (at most one per slide), and text color
  for a supporting icon. An icon has only one color: Lucide is
  entirely outlined, with no fill or second shade.

### The three overrides

On an icon **instantiated by a template** (therefore carrying a `template_key`),
only three props can be overridden (contract 5.3):

- `color` and `stroke_width`: always; these are the normal edits for a bound
  icon.
- `name`: ONLY if the template writes a literal name. When the name comes
  from a slot or item field, the slot value is authoritative (contract 7.4) and
  a `name` override MASKS it, taking control of that position away from both the agent
  and the user. In that case, write the slot, not an override.

Override skeleton and general rules: `references/format-cheatsheet.md`.

## Editorial guidance

- An icon conveys an idea rather than decorating: do not add one per bullet if it
  does not distinguish anything.
- Lucide is entirely outlined: keep a single stroke-to-size ratio per deck and
  the same visual vocabulary (do not mix abstract icons and
  figurative pictograms in the same series).
- The name is English and technical; it never appears on the slide: the
  adjacent text speaks to the user.
