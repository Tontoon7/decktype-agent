# Review a patch affecting protected blocks

Read `deck capabilities --json` and check the
`document.patch.protected_review` capability, then `deck patch --help`. This
capability describes this CLI's workflow. It does not prove that an older app
or the browser provides an equivalent workflow.

A protected block has a label and a stable key. It can target several elements
or template keys. Its policy travels with the `.deck`; the geometric `locked`
flag is independent. Never delete the policy or bypass a refusal by rewriting
the ZIP. If the CLI does not understand a future policy, use a compatible version.

## Compare and choose

The direct command `deck patch source.deck patch.json --dry-run --json`
reports `review_required: true`, `protection_impacts` and exit code 1 when a
choice is needed. It changes no files. Without `--dry-run`, a proposal affecting
a protected block is also rejected without writing. Temporary changes between
commands count, even if a later command restores the original value.

Prepare a comparison in a new directory:

```sh
deck patch source.deck patch.json --review-out proposition --json
```

The directory contains `before.deck`, `after.deck`, PNGs of every slide,
`review.json` and `choices.json`. Read the impacts and the
`before.visual` / `after.visual` diagnostics, then inspect every before/after PNG.
`stage: pending` means protected choices are still needed; this review cannot
be applied.

In `choices.json`, preserve `kind`, `schema_version` and `binding` unchanged.
Each `decisions` entry initially contains `null`. Replace each value with an
explicit choice for this proposal:

- `keep_original`: preserve the block by excluding the command that changes it;
- `apply_change`: allow the proposed change for this block.

Reuse decisions the user has already provided. If a decision is missing,
present the block's label and concrete consequences before asking for it.
Never fill every value with `apply_change` by default. These JSON files are
review data, not evidence of human authorization.

## Inspect the result of the choices

```sh
deck patch source.deck patch.json --review-out resultat-revu --choices proposition/choices.json --json
```

Read the new review and inspect every PNG. It now describes the actual result
of the choices (`stage: resolved`). `skipped_commands` contains zero-based
indices of excluded commands. A grouped command (`batch`) remains indivisible:
preserving a block can exclude other effects of that same command. Other
commands are recalculated; a broken dependency or a new unauthorized conflict
rejects the entire resolution.

A proposal with no protected impact directly produces a resolved review,
which must also be inspected before applying it.

## Save a new copy

```sh
deck patch source.deck patch.json --review resultat-revu/review.json --out copie.deck --json
deck validate copie.deck --json
deck lint copie.deck --visual --json
```

Applying reconstructs the result, compares document, templates, resources,
diagnostics and pixels, then saves exactly the verified `after.deck` bundle.
The source and existing outputs are never overwritten in this workflow.
`history_saved: false` means this CLI copy does not save undo history. The
policy remains available for future proposals, including after `apply_change`.

If the source, patch, installed templates in use or previews have changed,
create a new review. Do not alter fingerprints to reuse old choices. An
interruption may leave an incomplete directory: choose a new directory; only
`review.json`, written last, completes preparation.

Workflow limits: 8 MiB patch, 256 KiB choices, 2 MiB review, 200 slides per
compared document and 256 MiB of generated artifacts. The directory stays local;
this command neither publishes nor shares the deck.
