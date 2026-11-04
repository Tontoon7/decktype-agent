# Prepare the story before generating slides

Check `deck capabilities --json`: this recipe requires `story.outline.edit` for
editing and `story.outline.generate` for generation. Everything runs locally,
without an account or assistant call. A supplied reference remains unverified;
never present it as established evidence.

## Read or prepare a draft

```sh
deck outline read source.deck --json
```

The output contains the source file SHA and its optional outline. `null` means
no outline is saved. For an existing outline, extract its `outline` field into
a working JSON file, then preserve identities of edited or moved rows. Only
new rows receive a new identity.

For a new draft based on messages already accepted:

```sh
deck outline init --objective "Décider du pilote" --audience "Comité" \
  --message "Mesurer la valeur du pilote" \
  --message "Décider de la prochaine étape" --out plan.json --json
```

Then edit `plan.json`: objective, audience, messages, roles, references, notes
and order. References have status `missing` without a source or `provided` with
a supplied source, never `verified`. Durations are optional and indicative.
Notes are private preparation notes, distinct from speaker notes. Follow the
user's brief and preferences for a client presentation.

## Compare, then accept a copy

```sh
deck outline review source.deck --input plan.json --out review.json --json
```

Read the review's `original` and `proposed` fields and verify messages, order,
identities and references. The source stays intact. Review JSON can contain
private notes: do not publish it or attach it to a theme capture.
After this comparison is accepted:

```sh
deck outline apply source.deck --review review.json --out plan-accepte.deck --json
deck outline read plan-accepte.deck --json
deck validate plan-accepte.deck --json
```

An existing file is never overwritten. A source changed since comparison is
rejected: start from its current version and create a new review. The editing
copy preserves slides, identities, slots, edits and resources; only the private
outline changes. Operation history is not saved in the copy. The selected review
is a local document, neither a signature nor evidence that anyone read it.

## Choose layouts and create slides

Start from the file containing the accepted story. For each row, use its ID
from `outline read` to prepare options:

```sh
deck outline layouts plan-accepte.deck --slide <message-id> --out options-1 --json
```

Read `options-1/review.json` and inspect the PNGs before choosing. Options
preserve the full message and active theme revision. Exclusions are explicit;
no option is selected automatically. Each `choice_file` identifies an option's
JSON with its bundle, PNG and fingerprints. Repeat for every row, then supply
exactly one choice per message:

```sh
deck outline preview plan-accepte.deck \
  --choice options-1/01.json --choice options-2/02.json --out creation-review --json
```

The numbers illustrate choices after inspection, not a selection rule. Final
order follows the accepted story even if arguments appear in another order.
Inspect all PNGs in the final directory and check messages and flagged
references. `preview.deck` is the complete proposed copy. Rejecting means not
running creation; the source stays intact. After acceptance:

```sh
deck outline create plan-accepte.deck --review creation-review/review.json \
  --out presentation.deck --json
deck validate presentation.deck --json
deck outline read presentation.deck --json
```

Saving rechecks source, content, resources and pixels, then copies reviewed
bytes into a new file. A change to the source or a font visible in previews
requires a new review. A changed installed library does not replace frozen
templates. The new document identity is that of the reviewed bundle; slides
use the identities of story messages. Preparation notes and references stay
private in the outline; they do not automatically become speaker notes or
rendered text. Also verify relevant exports using the main skill's loop.
A U3-compatible app provides the same workflow through “Create slides”.

## Contract, compatibility and privacy

The optional outline lives at `assets/.decktype/outline.json`, introduced in
format 0.20.0 with `schema_version: 1`. No generation occurs on opening.

Preserve every `assets/` entry during a round-trip, including unknown entries.
Never copy `assets/.decktype/` into a template capture, theme or demonstration
deck: these are private document data. An old 0.19 writer transports these
bytes but may reset the container's label to 0.19; it cannot edit the outline.

The outline contains `schema_version`, `objective`, `audience` and the `slides`
list. Each row has a stable ULID `id`, `message`, `role`, `evidence`,
`speaker_notes` and optional `estimated_seconds`. Identities belong to the
outline; no link to a rendered slide is implicit.
Each evidence entry has `status`, `description` and optional `source`:

- `missing`: no reference supplied, `source` absent or null.
- `provided`: a nonempty reference supplied, still unverified.

Never invent evidence or use `verified` status. The outline can be empty.
Unknown fields in schema 1 must survive; an unknown version or invalid outline
must remain opaque without replacement.

UTF-8 byte limits: 2 MiB JSON, 200 rows, 20 evidence entries per row,
16 KiB message, 64 KiB notes, 8 KiB objective/audience, 80-byte role,
8 KiB description/reference. The declared estimate is absent or an integer
between 1 and 86400 seconds; it does not guarantee a presentation's duration.
General bundle security limits still apply.

Full repository contract: `docs/format/deck-v0.md`, section 13.
