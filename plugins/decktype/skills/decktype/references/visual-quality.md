# Read visual diagnostics

Discover `diagnostics.visual` in `deck capabilities --json`.
`deck lint mon-deck.deck --visual --json` complements historical lint: it
measures ink from materialized text elements using renderer formatting.
Text can fit its own box while extending beyond the slide.

Editorial `small_text` is a warning for nonblank text when the minimum of the
block size and effective run sizes is below `12 * page_scale` pt; equality
passes. `page_scale = max(slide.width, slide.height) / 1920`: 1 for 1920x1080
and 1920x1440, about 0.4385 for A4 (minimum about 5.26 pt, so 4 fails and 9
passes). Lint contrast keeps its 3:1/2:1 floors, switching at
`24 * page_scale` pt. Breathing margins remain 3% of each axis.
A4 PDF pages are 595.28 x 841.89 pt; recognized A4 PowerPoint decks export
at about 21.0 x 29.7 cm with unchanged source point sizes. Other PowerPoint
formats keep the historical 12192000 EMU width.

The historical U1 calibration from 2026-09-05, with a fixed 1 pt threshold,
covers ten small synthetic decks, twenty slides and 53 text blocks, with PNGs
inspected before reading reports. It finds seven expected overflows without
false positives and one font uncertainty. Three defects remain out of scope:
a clipped cell, overlapping chart labels and off-canvas text. Historical lint
flags the last case. These counts measure neither client presentation quality
nor user time savings.

- `complete: true` means measurement of in-scope text blocks completed.
  It does not approve the entire slide.
- `complete: false` and `uncertainties` require checking: an unmeasurable glyph
  is not text that fits.
- Explicit masks and invisible monochrome text are intentional controls.
  Do not remove a mask to make a warning disappear.
- Axes are read in the block's coordinate system. Rotation alone is not an
  overflow; an identifier without spaces may extend horizontally.
- Every overflow carries `suggested_font_size`: the largest integer that fits
  with resolved fonts, or `null` if no reliable size is available. Both axes
  of an element share the suggestion. Search rejects more than 4096 sizes or
  262144 estimated work units (rendered characters times candidate sizes),
  without hiding the overflow. Only block size varies; explicit run sizes stay
  intact. Shorten first, then review a suggested size, then split across slides.
  A proposed small size still requires visual judgment before acceptance.
- The absolute floor remains 1 pt. Current policy grants typographic margins
  when usable lines and visible advances, excluding trailing spaces, fit inside
  the box: at horizontal edges, the relative component adds
  `max(0, 0,02 em - 1 pt) / 2`, where `em` is the visible glyph's size.
  At the top and bottom, this relative component and quantized halves of
  negative leading, capped at 0.20 em, also require a known capital height
  from the run's font (`OS/2 sCapHeight`) that fits available height and usable
  line height within 1 pt. A tall box does not justify a margin when the line
  compresses capital bodies; diacritic offsets do not change this guard.
  Otherwise vertical comparison stays at the absolute 1 pt floor.
  Arbitrarily compressed line spacing does not prove capital bodies fit;
  missing metrics do not justify a margin. A single visible line can also
  extend by 0.03 em horizontally. The text box does not clip its ink: these
  margins distinguish a fully painted accent from text that is too low or too
  wide. An outline clipped by more than 1 pt at the slide edge loses these
  margins. Retained alerts' `overflow` and `required` dimensions remain exact,
  without subtracting margins. The historical corpus contains clear excesses
  from 12.77 to 2558.91 points; it proves neither an optimal subpoint threshold
  nor the new policy's scores.
- Recalculate after every edit. With `diagnostics.check`, follow the contact
  sheet and report loop below (full size only for flagged or doubtful slides);
  otherwise render and inspect every PNG. Keep historical lint for off-canvas
  boxes.
- Contrast evaluates text against shapes beneath its center: a gradient counts
  by its worst stop, a semitransparent shape or text is composited over what is
  below; images, decorations, charts and tables do not count.

Editorial proposals are described in [text-rewrite.md](text-rewrite.md).
An exact identifier is not shortened to fit; a short reply is not necessarily
faithful. The person compares both versions before retaining a proposal.
Styles, notes and edits remain preserved.

For a multitheme deck, each binding uses its exact revision during regeneration
and validation. A missing or partial reference is reported without silently
substituting the global theme. Opening never regenerates the file.

## Read `deck check`

Discover `diagnostics.check` in `deck capabilities --json`, then run
`deck check mon-deck.deck --out check --json`. The report runs on CPU; the
contact sheet requires a GPU. `--no-sheet --json` recalculates findings without
rendering. By default, a 1536 px-wide sheet contains up to 12 numbered
thumbnails; `--per-sheet` and `--width` change these limits. `sheets` lists
exactly the files written: do not read old sheets left in the directory.
Red borders and numbers mark flagged slides.

- `kind: "deck_check"`, `schema_version: 1`, `source_revision` and `slides`
  identify the derived report. It copies no deck text.
- `flagged_slides` is sorted with 1-based numbers. `pointer` and `other_pointer`
  are JSON paths with zero-based indices; `slide_id`, `element_id` and
  `template_key` locate the stable target.
- `text_overflow` uses the visual classification and typographic margins
  described above: `axis` and `overflow` are in points. `suggested_font_size`
  reuses lint's suggestion without automatic application. `thresholds` exposes
  the absolute floor and relative/margin parameters. Intentional masks stay
  excluded; split and rewrite correctors use this same classification with
  slide size to reject a proposal whose accent would be clipped at the edge.
- `text_overlap` compares ink from two texts after translation and rotation on
  the slide. `other_element_id` and `overlap` identify the pair and rectangle.
  An excess of more than 1 pt on both axes is flagged.
- `hyphen_break` flags a break after a hyphen inside a word; `word_split` flags
  a midword break. `line` starts at 1, `offset` is a UTF-8 byte index in
  rendered text. Explicit line breaks and CJK scripts without spaces are not
  word breaks. Composed or decomposed accents before the hyphen are recognized;
  offsets remain those of the original text without Unicode normalization.
- `low_contrast` retains the element's worst style: `ratio`, `minimum`,
  `font_size`, `color` and `run` (zero-based index, or null for text without
  runs). Minimum is 4.5:1 below `44 * page_scale` pt, 3:1 from that boundary
  (44 pt at scale 1, about 19.29 pt in A4). Report threshold parameters remain
  the reference values at scale 1. These ratios are stricter than `deck lint`'s
  editorial floor. `small_text` remains a lint rule, not a check rule.
- `complete: false` and `uncertainties` require full-size inspection of uncertain
  targets. `--strict` exits with 1 for findings or uncertainties, 0 otherwise,
  2 for an operational error.

Overlap covers text against text only, not cells or chart labels. Contrast
uses backgrounds beneath the text's center, shapes, gradients and transparencies
from lint; it does not judge images, decorations, charts or tables. Inspecting
a contact sheet remains necessary for aesthetics, off-canvas objects and
out-of-scope defects. Parley leaves some long words unbroken: their overflow
then is `text_overflow`, not `word_split`.

Read the entire contact sheet once and the report, then render only flagged
or doubtful slides in one call: `flagged_slides`, `uncertainties` targets, and
slides where the sheet shows a named concern (clipped or crowded text,
off-frame element, empty card, unreadable hierarchy). Use
`deck render mon-deck.deck --out slides-png --slide 3,7` and inspect those PNGs
at full size in one message. Do not render an unflagged slide without a named
concern, even if just created; without findings or doubts, deliver without
rendering. After correction, `deck check mon-deck.deck --no-sheet --json`,
then render only affected slides. Rebuild the sheet at delivery if structure
changed. For small text, darken the accent rather than change an image's
background; #E07A3F on white is near 2.99:1 and #B85A22 near 4.64:1.
