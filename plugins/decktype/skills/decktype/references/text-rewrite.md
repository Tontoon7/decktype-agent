# Propose shorter text

Correction order: shorten faithfully, then propose a reviewed font size,
then split the content if readability or meaning cannot be preserved.

## Review sizes as a batch

If `text.fit.review` is advertised, take the `slide_id` and `element_id` pairs
from visual lint and save them in `targets.json`, an explicit list:

```json
[{"slide_id":"<slide-id>","element_id":"<element-id>"}]
```

```sh
deck text fit review source.deck --targets targets.json --out comparaison --json
deck render comparaison/proposition.deck --out proposition-png --slide 3,7
deck text fit review source.deck --targets targets.json --choices comparaison/choices.json --out resultat --json
deck text fit apply source.deck --review resultat/review.json --out accepte.deck --json
deck lint accepte.deck --visual --json
```

Read the review's texts, sizes, resolved fonts and protections. Inspect PNGs
before acceptance and check readability at small sizes. Without a protection
to resolve, the first review can be accepted directly. A human override stays
protected; fill its choices explicitly to replace it. Existing sources and
outputs are never overwritten. A changed source, review, proposal, dependency
or font resolution requires a new review. A `null` suggestion requires
shortening or splitting. This workflow only changes the block's `font_size`,
never explicit run sizes, contents or other edits. Linked sizes survive
`deck regenerate`. Also render the accepted file and inspect affected slides.

## Propose a rewrite

Prerequisite: `deck capabilities --json` advertises `text.rewrite.preview` and
the commands below. This workflow is local, without an account or implicit
service call. It produces a copy for review, not an automatic correction.

1. `deck lint source.deck --visual --json`: choose the overflowing text's IDs.
2. Read `deck text rewrite request --help`, then prepare the request:

   ```sh
   deck text rewrite request source.deck --slide <slide-id> --element <element-id> --out request.json --json
   ```

   The report contains `request` and `prompt`. The file preserves the exact
   request, bound to the document and its dependencies. The prompt only
   contains the target text and its styles. Send it to the user's chosen
   agent, or process it in the current session if that session is this agent.
3. Save the reply in `reply.json`: unchanged schema_version, request_id and
   source_revision, then `spans`, one string per run in existing order or one
   string for plain text. No style fields or patch commands. Preserve meaning,
   numbers, names, caveats and negations. An impossible faithful shortening
   can be declined.
4. Read `deck text rewrite review --help`, then:

   ```sh
   deck text rewrite review source.deck --request request.json --reply reply.json --out proposition.deck --json
   deck validate proposition.deck --json
   deck lint proposition.deck --visual --json
   deck render proposition.deck --out proposition-png
   ```

   The report shows `original` and `proposed` with their styles. Open the
   relevant PNG and compare the meaning of both texts with the user before
   retaining the copy. Measurement only guarantees that this proposal fits
   in the current font context; it does not judge fidelity to the message.

Existing paths, including the source, are never overwritten. Slots, other
contents, notes, edits and free elements are preserved. The copy already
contains materialized text: this workflow requires no regeneration.
An empty, invisible, nonshorter or still overflowing reply is rejected.
A changed source, embedded font, image or template invalidates the request:
prepare it again without editing fingerprints by hand. An ambiguous slot
mapping or one hidden by an edit is rejected, never bypassed.

## Comparison and acceptance with protections

If `text.rewrite.protected_review` is advertised, use a full comparison instead
of the proposal export in step 4:

```sh
deck text rewrite review source.deck --request request.json --reply reply.json --review-out comparaison --json
```

Read `original`, `proposed`, impacts and every before/after PNG. Texts retain
their styles. Each decision in `comparaison/choices.json` initially is null;
fill it with `keep_original` or `apply_change` according to the user's choice.
Shortening forms a single indivisible operation.

```sh
deck text rewrite review source.deck --request request.json --reply reply.json --choices comparaison/choices.json --review-out resultat --json
```

Compare `result` and resolved PNGs: keeping preserves the original text;
applying retains the proposal. Then read `deck text rewrite apply --help`:

```sh
deck text rewrite apply source.deck --request request.json --reply reply.json --resolved-review resultat/review.json --out accepte.deck --json
deck validate accepte.deck --json
deck render accepte.deck --out accepte-png
```

Inspect the accepted file's PNGs. Without protected impacts, the first
comparison is already resolved, but accepting it still requires an explicit
command. Keeping writes the exact source, including its metadata; applying
writes the verified resolved bundle. Every output file and directory must be
new. `--out` and `--review-out` are mutually exclusive; `--choices` requires
`--review-out`. The old `--out proposition.deck` remains a proposal export.

Source, request, reply and templates are rechecked on acceptance, as are texts,
impacts, choices, bundles, diagnostics and PNGs. A change requires a new review;
do not recalculate fingerprints by hand to reuse decisions. Request, reply and
review are limited to 2 MiB each, choices to 256 KiB, comparison to 200 slides
and its artifacts to 256 MiB.
