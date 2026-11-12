# Premium compositions

For a new presentation using brand roles without a prescribed gallery, prefer
`premium`. Discover the actual catalogue with `deck templates list --json`, then
`deck templates show <pack>/<id> --deck mon-deck.deck --json` before writing.
An explicitly requested theme gallery takes priority; `standard` remains
the fallback without visuals. None of these templates supplies your images.

Import images with `deck image add`, and use the returned paths in
`image` slots or list image fields. Every composition offers an optional
`logo` using image contain: omit this slot without a logo, never use a deleted
override or an empty path. For inverted backgrounds, use a logo with ink
legible on that background. Backgrounds and text alternate background/text; fonts
use display/body only.

In `content-text` (points), `card-grid` (cards) and `process` (steps), the optional
`icon` field expects a Lucide registry name, such as `star` or `check`,
never an image path. Verify the name with `deck icons list --json`; omit
the field without an icon. These vector icons use the theme accent color
and require no imported asset.

## Images

No composition veils its photo: colors stay as supplied, and a reading
panel sits only under the text. Images are cropped by a centered cover fit,
never stretched.

- `title-image` is a two-zone cover: the image fills a full-height column
  on the right third (640 x 1080). `method-image` and `cta-image` place it
  full-height to the right of the reading column (864 x 1080). Give these
  three a portrait (4:5 or taller) or a cut-out portrait on a transparent
  background: the full height stays visible, head included. A landscape photo
  shows only its central part.
- `image-full` keeps a full-bleed landscape photo (16:9) behind a reading panel
  at bottom left. Choose a calm photo where the footer sits (bottom right) or
  omit `footer`.
- `takeaway-list` keeps its optional image as a veiled backdrop under all text.

## Uses and slots

The ! suffix marks a required slot. Lists show their bounds followed by
their fields (! suffix if required). All also accept the optional logo.
Labels are written in the deck's language through optional slots,
with no imposed English text. For `approach-arch`, supply `example_label` with
`example` when a subheading is useful; without an example, omit both slots.
The composition then retains neither an empty card nor a label.

| Composition | Usage | Slots |
| --- | --- | --- |
| `title-image` | Two-zone cover: a monumental title on the left and a full-height photo or cut-out portrait on the right, with a discreet optional logo. | `eyemark`, `footer`, `image!`, `subtitle`, `title!` |
| `statement` | A single strong statement, centered on a tonal background with a restrained topographic motif. | `caption`, `mark`, `text!` |
| `takeaway-list` | A decisive takeaway with two or three supporting arguments and an optional photographic backdrop. | `eyemark`, `image`, `insight!`, `subtitle`, `supporting_points!` 2..3 (num!, point!) |
| `approach-arch` | An editorial explanation and example beside an arch-shaped image, on an inverted theme background. | `definition!`, `example`, `example_label`, `eyemark`, `image!`, `source`, `term!` |
| `three-pillars` | Three illustrated pillars with large image windows, numbered headings and concise descriptions. | `cols!` 3..3 (description!, image!, index!, title!), `eyemark`, `title!` |
| `image-full` | Full-bleed image with a protected reading zone for a short title and supporting caption. | `eyemark`, `footer`, `image!`, `subtitle`, `title!` |
| `loop` | Three connected steps with an explicit feedback loop and a caption explaining the return. | `eyemark`, `loop_caption`, `n1_desc`, `n1_label!`, `n2_desc`, `n2_label!`, `n3_desc`, `n3_label!`, `subtitle`, `title!` |
| `statement-light` | An editorial statement on an inverted theme background, framed by fine rules and orbital decoration. | `attribution`, `quote!` |
| `method-image` | Three numbered method steps in a compact reading column with a full-height image alongside. | `eyemark`, `image!`, `items!` 3..3 (detail, num!, title!), `title!` |
| `cta-image` | A closing invitation with a prominent action, contact information and an atmospheric image. | `contact_info`, `cta_text!`, `eyemark`, `image!`, `subtitle`, `title!` |
| `section-divider` | A chapter opening with an oversized index, title and optional introductory caption. | `eyemark`, `index!`, `subtitle`, `title!` |
| `content-text` | Editorial text on the left with a separate column of concise supporting points. | `eyemark`, `points!` 2..4 (icon, text!), `subtitle`, `title!` |
| `content-two-cols` | Two complementary editorial columns, separated by a fine rule rather than boxed cards. | `eyemark`, `left_content!`, `left_title!`, `right_content!`, `right_title!`, `title!` |
| `card-grid` | A grid of two to four spacious cards with optional illustrations and short descriptions. | `cards!` 2..4 (body!, icon, title!), `eyemark`, `title!` |
| `comparison` | Compare two named alternatives with parallel numbered criteria and a shared headline. | `eyemark`, `left_points!` 2..5 (num!, text!), `left_title!`, `right_points!` 2..5 (num!, text!), `right_title!`, `title!` |
| `before-after` | Show a transformation with two contrasting panels and an explicit direction of change. | `after_description`, `after_label`, `after_title!`, `before_description`, `before_label`, `before_title!`, `eyemark`, `title` |
| `big-number` | Make one decisive metric the focal point, with a clear label and optional context. | `context`, `eyemark`, `label!`, `number!` |
| `stats` | A row of two to four substantial indicators, with large values and concise labels. | `eyemark`, `stats!` 2..4 (label!, value!), `title!` |
| `quote` | An attributed quotation with an oversized typographic opening mark and ample breathing room. | `author!`, `quote!`, `role` |
| `case-study` | A client story separating context, challenge and a prominent quantified result. | `challenge!`, `challenge_label`, `client`, `context!`, `context_label`, `eyemark`, `image!`, `result_caption`, `result_label!`, `result_value!`, `title!` |
| `timeline` | A horizontal chronology of dated milestones with short explanatory captions. | `events!` 2..5 (date!, description, title!), `eyemark`, `title!` |
| `roadmap` | A phased delivery plan with stage, duration, activities and a tangible milestone per column. | `eyemark`, `phases!` 2..4 (duration, items!, milestone!, name!, stage!), `title!` |
| `checklist` | A vertical series of checkpoints with concise supporting detail and generous row spacing. | `eyemark`, `items!` 2..5 (detail, text!), `title!` |
| `matrix-2x2` | A positioning matrix with two named axes and four editable quadrant summaries. | `eyemark`, `q1_desc`, `q1_title!`, `q2_desc`, `q2_title!`, `q3_desc`, `q3_title!`, `q4_desc`, `q4_title!`, `title!`, `x_axis`, `y_axis` |
| `process` | A linear sequence of illustrated steps with accent markers and distinct explanatory columns. | `eyemark`, `steps!` 2..5 (description!, icon, title!), `title!` |

## Measured budgets

Guidelines measured with `deck templates show --deck` on a Sora/Inter brand style,
1920 x 1080, background #142D2A, text #F3EFE4, accent #D49A61. Method
`rendered-corpus-v1`, corpus `fr-short-medium-v1`, no font fallback.
These are indicative ceilings, not a guarantee of comfortable editorial density.
Keep a margin, shorten messages, then inspect the contact sheet and report.
Recalculate on the actual brand style: another font or size changes these budgets.
Image/logo fields consume no text and have no budget.

| Composition | Field: characters / lines |
| --- | --- |
| `title-image` | eyemark: 80 / 1 ; footer: 96 / 1 ; subtitle: 159 / 2 ; title: 64 / 4 |
| `statement` | caption: 127 / 1 ; mark: 45 / 1 ; text: 123 / 5 |
| `takeaway-list` | eyemark: 34 / 1 ; insight: 118 / 3 ; subtitle: 100 / 1 ; supporting_points.num: 5 / 1 ; supporting_points.point: 122 / 1 |
| `approach-arch` | definition: 297 / 4 ; example: 84 / 1 ; example_label: 28 / 1 ; eyemark: 34 / 1 ; source: 98 / 1 ; term: 33 / 2 |
| `three-pillars` | cols.description: 149 / 3 ; cols.index: 16 / 1 ; cols.title: 70 / 2 ; eyemark: 82 / 1 ; title: 51 / 1 |
| `image-full` | eyemark: 61 / 1 ; footer: 53 / 2 ; subtitle: 151 / 3 ; title: 70 / 3 |
| `loop` | eyemark: 82 / 1 ; loop_caption: 98 / 1 ; n1_desc: 158 / 4 ; n1_label: 26 / 1 ; n2_desc: 158 / 4 ; n2_label: 26 / 1 ; n3_desc: 158 / 4 ; n3_label: 26 / 1 ; subtitle: 99 / 2 ; title: 48 / 1 |
| `statement-light` | attribution: 102 / 1 ; quote: 99 / 4 |
| `method-image` | eyemark: 63 / 1 ; items.detail: 135 / 2 ; items.num: 5 / 1 ; items.title: 48 / 1 ; title: 47 / 2 |
| `cta-image` | contact_info: 72 / 1 ; cta_text: 71 / 2 ; eyemark: 34 / 1 ; subtitle: 60 / 1 ; title: 67 / 3 |
| `section-divider` | eyemark: 82 / 1 ; index: 4 / 1 ; subtitle: 107 / 1 ; title: 58 / 2 |
| `content-text` | eyemark: 54 / 1 ; points.text: 86 / 2 ; subtitle: 270 / 4 ; title: 114 / 4 |
| `content-two-cols` | eyemark: 82 / 1 ; left_content: unavailable / 8 ; left_title: 86 / 2 ; right_content: unavailable / 8 ; right_title: 86 / 2 ; title: 102 / 2 |
| `card-grid` | cards.body: 190 / 7 ; cards.title: 62 / 4 ; eyemark: 82 / 1 ; title: 45 / 1 |
| `comparison` | eyemark: 82 / 1 ; left_points.num: 4 / 1 ; left_points.text: 113 / 2 ; left_title: 44 / 1 ; right_points.num: 4 / 1 ; right_points.text: 113 / 2 ; right_title: 43 / 1 ; title: 47 / 1 |
| `before-after` | after_description: 345 / 6 ; after_label: 33 / 1 ; after_title: 71 / 2 ; before_description: 345 / 6 ; before_label: 33 / 1 ; before_title: 71 / 2 ; eyemark: 82 / 1 ; title: 54 / 1 |
| `big-number` | context: 246 / 3 ; eyemark: 68 / 1 ; label: 36 / 1 ; number: 5 / 1 |
| `stats` | eyemark: 82 / 1 ; stats.label: 47 / 2 ; stats.value: 4 / 1 ; title: 40 / 1 |
| `quote` | author: 99 / 1 ; quote: 137 / 4 ; role: 116 / 1 |
| `case-study` | challenge: 260 / 3 ; challenge_label: 72 / 1 ; client: 47 / 1 ; context: 260 / 3 ; context_label: 72 / 1 ; eyemark: 54 / 1 ; result_caption: 72 / 1 ; result_label: 74 / 2 ; result_value: 10 / 1 ; title: 106 / 2 |
| `timeline` | events.date: 26 / 1 ; events.description: 171 / 5 ; events.title: 24 / 1 ; eyemark: 82 / 1 ; title: 45 / 1 |
| `roadmap` | eyemark: 82 / 1 ; phases.duration: 45 / 1 ; phases.items: 182 / 5 ; phases.milestone: 71 / 2 ; phases.name: 47 / 2 ; phases.stage: 30 / 1 ; title: 45 / 1 |
| `checklist` | eyemark: 37 / 1 ; items.detail: 107 / 1 ; items.text: 75 / 1 ; title: 95 / 5 |
| `matrix-2x2` | eyemark: 82 / 1 ; q1_desc: 203 / 3 ; q1_title: 44 / 1 ; q2_desc: 203 / 3 ; q2_title: 45 / 1 ; q3_desc: 203 / 3 ; q3_title: 45 / 1 ; q4_desc: 203 / 3 ; q4_title: 45 / 1 ; title: 53 / 1 ; x_axis: 28 / 1 ; y_axis: 23 / 1 |
| `process` | eyemark: 82 / 1 ; steps.description: 176 / 6 ; steps.title: 18 / 1 ; title: 45 / 1 |

Full measurements, warnings and cardinalities are in the CLI output.
The recipe and QA contact sheets are documented in the repository under
`docs/qa/premium-templates/`. No account or private pack is needed.
No template crops or shrinks text.
