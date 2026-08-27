---
name: decktype
description: Create, revise, validate, render, import, or export editable Decktype presentations. Use for a Decktype .deck file, an agent-built slide deck that must remain editable, or a PowerPoint workflow that should end in Decktype or export to .pptx. Do not use for ordinary Markdown documents or image-only slideshows.
---

# Decktype

Create presentations as structured `.deck` bundles, then leave the final editorial control to the user in the Decktype app.

Two invariants protect the human-agent round trip:

1. Prefer template-bound slides. Fill template slots and let `deck regenerate` materialize their elements.
2. Inspect the rendered result. A deck is not complete until every changed slide has been rendered and visually reviewed.

## Check the local setup

Start with:

```sh
command -v deck
deck --version
```

If `deck` is unavailable, stop and ask the user to install Decktype, open the app, and choose **Connect an agent**. Do not invent an install path or download and execute a binary on the user's behalf.

Judge document compatibility by the bundle's `format_version`, not only by the CLI version.

## Agree on the presentation before generating it

For a new deck, establish:

- the audience;
- the decision or action the deck should produce;
- the source material and facts that may be used;
- the delivery format (`.deck` only, or an additional `.pptx`).

Propose a short slide outline with one message per slide and wait for approval before creating the file. A detailed user-provided brief or explicit advance approval counts as approval.

Never invent metrics, quotations, customer names, testimonials, or sources. Use placeholders only when the user explicitly asks for them, and label them clearly.

## Create a deck

1. Discover templates from the installed CLI. Do not assume a locally installed pack exists:

   ```sh
   deck templates list --json
   deck templates show standard/titre --json
   ```

2. Read [references/templates.md](references/templates.md) for template selection and content budgets. Re-run `deck templates show <pack>/<id> --json` for every selected template; its slot schema is authoritative.

3. Scaffold the bundle:

   ```sh
   deck new presentation.deck --title "Presentation title"
   ```

4. Read [references/format.md](references/format.md), replace the empty slide with approved template bindings, and keep `elements` empty on newly bound slides.

5. Materialize and verify:

   ```sh
   deck regenerate presentation.deck
   deck validate presentation.deck --json
   deck lint presentation.deck
   deck render presentation.deck --out presentation-preview
   ```

6. Open and inspect every rendered PNG. Check text overflow, cramped spacing, empty blocks, weak hierarchy, and repeated layouts. Shorten slot content or select a better template, then repeat regeneration, validation, linting, rendering, and inspection.

7. Deliver the `.deck` path and a one-line summary per slide. Explain that the user can open the file in Decktype for final edits.

## Revise an existing deck

Inspect before editing:

```sh
deck inspect presentation.deck --json
unzip -p presentation.deck deck.json > deck.json
```

For a slide with a `template` binding:

- change text and lists in `template.slots`;
- preserve every existing slide and element ID;
- preserve all existing `template.overrides`, including overrides you do not understand;
- do not edit a materialized element's `kind.content` to change slot-driven text;
- do not delete a bound slide's elements manually.

For a free slide without a `template`, its `elements` are the source of truth and may be edited directly.

After any bundle change, replace `deck.json` in the archive and run:

```sh
deck regenerate presentation.deck
deck validate presentation.deck --json
deck lint presentation.deck
deck render presentation.deck --out presentation-preview
```

Inspect every changed slide and any neighboring slide whose narrative depends on it.

## Import an existing PowerPoint

Use the built-in importer instead of translating the package by hand:

```sh
deck import source.pptx --out imported.deck --json
deck inspect imported.deck --json
deck validate imported.deck --json
deck render imported.deck --out imported-preview
```

Imported slides are normally free slides rather than template-bound slides. Read every importer warning and inspect every preview. Rebuild only the slides that benefit from reusable template bindings.

## Export to PowerPoint

The `.deck` file remains the editable source. Export only after the final validation and visual review:

```sh
deck export presentation.deck --out presentation.pptx
```

Open the `.pptx` in the intended destination application and check fonts, charts, and complex positioning. Keep both files: the `.pptx` is a delivery artifact, not a replacement for the `.deck` source.

## Completion checklist

- The outline was approved or the brief was already explicit.
- Every factual claim comes from the user or a cited source.
- Template slot bounds are respected.
- Existing IDs and human overrides are preserved.
- `deck regenerate` ran after each JSON change.
- `deck validate` reports zero errors and every warning was understood.
- `deck lint` findings were reviewed.
- Every changed slide was rendered and visually inspected.
- The final `.deck` opens in Decktype; any requested `.pptx` was also checked.

