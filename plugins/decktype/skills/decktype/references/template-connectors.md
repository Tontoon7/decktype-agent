# Correct a template connector or its arrowheads

A template connector pointing to the wrong place is corrected with an override
in `template.overrides`, never by editing `elements`. On a LINKED element,
`from`/`to` have no effect: regeneration erases them. The slide stays linked,
its slots regenerate and other edits survive.

## 1. Diagnose

Read the bundle again, never a local copy:

```bash
unzip -p f.deck deck.json                        # slide, element, overrides
unzip -l f.deck                                  # templates/<pack>/<id>.json embedded
unzip -p f.deck templates/<pack>/<id>.json       # the template that applies
```

In the slide, find the element by its `template_key` and note:

- `kind.shape`: `line` (case 2) or `path` (case 3);
- `transform`: the effective box, including overrides;
- for a `path`, `kind.path.commands`, in `0..1` coordinates inside the box;
- in `template.overrides`, an existing `transform` or `path` override on this
  key (case 4).

The authoritative template is EMBEDDED in the bundle and takes priority over
the installed library: correct the deck against its own copy. Correcting the
library does not repair existing decks: a deck embedding an old `path`
connector needs case 3 even if the library now declares a `line`.

## 2. `line` case

A `line` box carries the segment along its horizontal center, then `rotation`
(degrees, clockwise, around the center) rotates it. Use one `transform`
override calculated from the two desired points:

    w = hypot(to.x - from.x, to.y - from.y)          h = 24 (hit area)
    rotation = degrees(atan2(to.y - from.y, to.x - from.x))
    x = (from.x + to.x)/2 - w/2                      y = (from.y + to.y)/2 - h/2

```json
{"key": "conn1", "prop": "transform",
 "value": {"x": 428.51057106077656, "y": 431.5,
           "w": 472.97885787844683, "h": 24.0, "rotation": 6.4338340759319355}}
```

Copy values at full precision: rounding moves endpoints accordingly and the
line misses its target. `from` is the first endpoint, `to` the second:
preserve the template's direction.

## 3. `path` case (old template)

`transform` supports neither mirroring nor negative scaling: use two overrides
on the same key. The box becomes the desired segment's bounding box (rotation
0, minimum dimensions 8), and `path` places both ends in `0..1` coordinates:

    x = min(from.x, to.x)                            y = min(from.y, to.y)
    w = max(abs(to.x - from.x), 8)                   h = max(abs(to.y - from.y), 8)
    move_to = ((from.x - x)/w, (from.y - y)/h)       line_to = ((to.x - x)/w, (to.y - y)/h)

Example, from (1500, 900) to (975, 845):

```json
[
  {"key": "conn2", "prop": "transform",
   "value": {"x": 975.0, "y": 845.0, "w": 525.0, "h": 55.0, "rotation": 0.0}},
  {"key": "conn2", "prop": "path",
   "value": {"commands": [{"op": "move_to", "x": 1.0, "y": 1.0},
                          {"op": "line_to", "x": 0.0, "y": 0.0}]}}
]
```

Flipping the diagonal without moving the box requires only the `path` override
(swapped corners, for example `(1, 0)` then `(0, 1)` becomes `(1, 1)` then
`(0, 0)`). `path` never accepts `null` and is interpreted against the element's
final box: without a `transform` override, it follows the template's box even
if the author changes it later.

## 4. Existing override

A `transform` or `path` override already exists on this key: replace it in
place (its `value`), never duplicate it. Overrides apply in array order and
the last wins: a duplicate hides the first and misleads the next reader.
Do this only because the request targets this connector: all other overrides
made by a human remain intact.

## 5. Verify

```bash
zip -q f.deck deck.json && rm deck.json          # the working copy dies here
deck regenerate f.deck                           # slide N: regenerated
deck validate f.deck --json                      # no "materialized elements diverge"
deck regenerate f.deck                           # slide N: up to date
unzip -p f.deck deck.json                        # read the element back
deck check f.deck --out check --json             # contact sheet, flagged slides
deck render f.deck --out slides-png              # look at the PNG
```

- A `line` saves its endpoints in the bundle as `kind.from` and `kind.to`:
  compare them with the desired points.
- A `path` (rotation 0 after this recipe) goes from `(x + move_to.x * w,
  y + move_to.y * h)` to `(x + line_to.x * w, y + line_to.y * h)`.
- Inspect the PNG: does the line touch the target point in the right direction?

## 6. Arrowheads (format 0.33.0)

To make a label designate a point, draw a `line` from the label (`from`) to
the point (`to`) and put the head on `to` with `marker_end`; `marker_start`
is the `from` end. `shape: arrow` is a filled pictogram, never a pointer.

| `kind` | Drawn at the end | Size (w = max(stroke width, 1), s = `scale`) |
| --- | --- | --- |
| `arrow` | filled triangle | length 4ws, base 2ws |
| `open` | stroked chevron | length 4ws, width 2ws |
| `dot` | filled disc | radius 1.5ws |

`scale` is optional (default 1, omitted on write), relative to the stroke
width and clamped to 0.25..4. Heads exist on `line` and open `path` ends only,
in the stroke color; the shaft is shortened so the tip lands on the point.

- **Free line**: write `marker_end` in its `kind` (cheatsheet `line` example);
  through `deck patch`, `set_element_kind` with the COMPLETE kind.
- **Bound line**: one override per end, `null` removing the template head.
  `set_override` replaces the override with the same `key` and `prop` in place
  and appends otherwise: the other overrides stay untouched. Never
  `set_overrides`, which replaces the whole list. Slide ULID from `deck.json`:

```json
{"version": 1, "commands": [
  {"op": "set_override", "slide": "<slide ULID>",
   "retouch": {"key": "conn1", "prop": "marker_end", "value": {"kind": "open", "scale": 1.5}}},
  {"op": "set_override", "slide": "<slide ULID>",
   "retouch": {"key": "conn1", "prop": "marker_start", "value": null}}
]}
```

```bash
deck patch f.deck arrows.json --dry-run --json   # every entry applies, file untouched
deck patch f.deck arrows.json                    # applies and regenerates the slide
```

Then the loop of section 5 from `deck regenerate` on. `deck validate` warns,
without error, on an unknown `kind` (kept, nothing drawn), a `scale` outside
0.25..4 (clamped) and a head on another shape (inert). PowerPoint export
writes native line ends rounded to `sm` 0.75, `med` 1 or `lg` 1.25 and warns
on each rounding: prefer these scales for a deck going to PowerPoint.

## For template authors

Declare a straight connector as `line`, never as a two-point `path`: its two
points define its box and one `transform` override corrects it. Converting an
old connector requires recalculating its box:
[authoring](authoring-themes-templates.md), `shape` bullet.
