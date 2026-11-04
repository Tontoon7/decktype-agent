# Choose a layout variant

Check for `layout.variants.review` in `deck capabilities --json`, then read
`deck layout variants --help` and `deck layout apply --help`. This workflow is
local, with no model call, image generation or library write.
It uses the slide's exact revision, its templates and the theme's
captures. The canonical offline fallback is identified by `shipped_fallback`.

1. Read `deck inspect source.deck --json` and choose a bound slide's ULID.
2. Prepare a new review directory:

```sh
deck layout variants source.deck --slide ULID --out variantes --json
```

3. Read `variantes/review.json`. `candidates` contains at most three choices,
   numbered from 1, with name, provenance, exact mapping, visual diagnostic,
   bundle and PNG. `exclusions` explains rejections with the engine's reasons;
   `omitted` counts entries beyond the limit of 32. Zero choices is valid:
   do not invent a mapping or remove an edit to obtain one.
4. Inspect every PNG and compare it with the source slide. The automatic check
   covers text block ink, not collisions, cells, chart labels,
   contrast or composition quality.
   A retained slot must also be used by the candidate; do not confuse
   presence in JSON with content actually preserved in the rendering.
5. If `layout.variants.protected_review` is advertised, also read `deck layout
   review --help` and prepare a comparison for the selected candidate:

```sh
deck layout review source.deck --review variantes/review.json --candidate 1 --out comparaison --json
```

The report contains `impacts`, `stage`, `before`, `after` and `skipped_commands`.
Decisions in `comparaison/choices.json` are initially null. For
each block, write `keep_original` or `apply_change` according to the
user's decision on this proposal. A layout change is an
indivisible operation: keeping one block keeps the entire source layout.
Do not invent a choice the user has not expressed.

```sh
deck layout review source.deck --review variantes/review.json --candidate 1 --choices comparaison/choices.json --out resolu --json
```

Inspect the resolved PNGs before continuing. `stage` must be `resolved`.
Choices are bound to the source bytes, catalogue, candidate number and
templates; choices from another review cannot be reused.

6. Apply the resolved result to a new file:

```sh
deck layout apply source.deck --review variantes/review.json --candidate 1 --resolved-review resolu/review.json --out choix.deck --json
```

Without protection impacts, the U2 workflow remains available:

```sh
deck layout apply source.deck --review variantes/review.json --candidate 1 --out choix.deck --json
deck validate choix.deck --json
deck render choix.deck --out rendu-choix
```

7. Inspect the final rendering. Keeping the source allows a return to the
   original document. Do not reuse this directory after editing the source.

The source, existing directories and existing output files are
never overwritten. Applying compares source and artifact bytes,
rebuilds the candidate with the shared engine and its frozen resources,
then requires the same saveable copy and compares PNG pixels. Only
a maximum difference of one level out of 255 per channel is tolerated for GPU antialiasing. If the source,
fonts, resources or preview have changed, prepare a new review.
Do not manually alter fingerprints to bypass a rejection.

The document, its binding and its elements are applied in one engine
transaction. In-memory undo history is not stored in the resulting `.deck`:
`history_saved` is `false`. Selected resources are embedded; the
usual format preserves all templates and active or referenced revisions.
A directory without `review.json` may come from an interrupted write: it
cannot be applied. Start again in a new directory, without merging
files from different reviews.

The protected comparison contains all slides and a visual diagnostic for
each document, including the candidate's resources. Acceptance rechecks
both bundles, their PNGs and decisions. A keep decision writes the
source file byte for byte, without installing candidate resources.
Apply writes the exact resolved bundle; the library may have been removed
after catalogue preparation, because its resources were frozen.
