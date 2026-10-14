# Decktype bundle and editing reference

A `.deck` file is a ZIP bundle. `deck.json` is its source of truth; embedded templates and assets make the document portable.

```text
presentation.deck
├── deck.json
├── templates/
└── assets/
```

The renderer reads `slides[].elements`. For a template-bound slide, `template.slots` describes the editable semantic content and `deck regenerate` rebuilds the materialized elements.

## Safe editing loop

Work beside the bundle so `deck.json` returns to the archive root:

```sh
unzip -p presentation.deck deck.json > deck.json
# Edit deck.json with a structured file-editing tool.
zip -q presentation.deck deck.json
deck regenerate presentation.deck
deck validate presentation.deck --json
deck lint presentation.deck
deck render presentation.deck --out presentation-preview
```

Inspect the PNGs after rendering. Do not deliver a deck solely because validation passed; validation cannot judge hierarchy or crowded copy.

## Generate IDs

New slides and free elements need ULIDs. Generate them; never type plausible-looking IDs or change existing IDs.

```sh
python3 -c "import os,time; a='0123456789ABCDEFGHJKMNPQRSTVWXYZ'; t=int(time.time()*1000); print(''.join(a[(t>>(5*i))&31] for i in range(9,-1,-1))+''.join(a[b&31] for b in os.urandom(16)))"
```

## Template-bound slide

Copy the bundle's active `theme_id` and `theme_revision_id` into each new binding. Start with no materialized elements:

```json
{
  "id": "NEW_ULID",
  "size": {"w": 1920.0, "h": 1080.0},
  "background": {
    "color": {"r": 245, "g": 242, "b": 234, "a": 255}
  },
  "elements": [],
  "notes": null,
  "template": {
    "pack": "standard",
    "id": "cartes",
    "theme_id": "default",
    "theme_revision_id": "COPY_FROM_ACTIVE_REVISION",
    "slots": {
      "titre": "Two options",
      "cartes": [
        {"label": "Option A", "detail": "Short explanation."},
        {"label": "Option B", "detail": "Short explanation."}
      ]
    }
  }
}
```

Use `deck templates show <pack>/<id> --json` to confirm slot types and list bounds before writing the binding.

## Slot rules

- A text slot takes a string.
- A list slot takes an array of objects whose keys come from the template schema.
- A data slot also takes an array of row objects; numeric cells are represented as strings in the binding.
- Omit an unused optional slot. An empty string can still materialize an empty element.
- Keep each item inside the reported `min` and `max` bounds.
- Use supplied facts only. A valid chart with invented values is still wrong.

## Preserve human edits

Decktype records manual style and position changes in `template.overrides`. When revising a bound slide:

- edit `template.slots` for semantic content;
- preserve every existing override, even if it looks unnecessary;
- never change existing IDs;
- never replace the materialized `elements` array by hand;
- run `deck regenerate` after the slot change.

An override may target an item by a key such as `cartes[1].detail`. If the user shortened a list, an apparently orphaned override may be intentional and must remain.

## Free slides

A slide without `template` is a free slide. Its `elements` array is the editable content. This is normal for imported PowerPoint files and for layouts no template can express.

Prefer bound slides for new work because they survive agent revisions more predictably. Use free elements only when the available templates cannot represent the approved design.

## Validation diagnostics

`deck validate presentation.deck --json` returns a nonzero status for errors and reports warnings separately.

Fix every error. Read and explain every warning. A warning that materialized elements diverge from their template binding normally means `deck regenerate` has not run since the last slot change.

`deck lint presentation.deck` is editorial rather than structural. Review its findings for overflow risk, empty content, edge spacing, weak contrast, and punctuation issues.

## Import and export

Import PowerPoint into a new Decktype source:

```sh
deck import source.pptx --out imported.deck --json
```

Export the validated source to a PDF delivery artifact, available on every plan:

```sh
deck pdf presentation.deck --out presentation.pdf
```

Export the validated source to a PowerPoint delivery artifact. This requires a signed-in Decktype Pro or Autonomous plan; otherwise the command exits with status 3 and writes nothing:

```sh
deck export presentation.deck --out presentation.pptx
```

Import and export can surface warnings or destination-specific differences. Inspect the `.deck` render after import and open the actual `.pdf` or `.pptx` after export.

