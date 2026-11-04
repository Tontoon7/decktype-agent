# Images through Decktype Cloud

**This document covers GENERATED images only.** An existing file (logo,
screenshot, photo) is added with `deck image add mon-deck.deck fichier.png`: local,
offline, free, no account; see “Local images” in `SKILL.md`.
`deck image generate` and `deck image accept` use Cloud and consume
quota: never use them for a file the user already has.

## Contents

- [Non-negotiable contract](#non-negotiable-contract)
- [Login, workspace and credits](#login-workspace-and-credits)
- [Create an image](#create-an-image)
- [Edit an explicit image](#edit-an-explicit-image)
- [Inspect, then accept](#inspect-then-accept)
- [Stable JSON](#stable-json)
- [Quotas and lifecycle](#quotas-and-lifecycle)
- [Error recovery](#error-recovery)
- [Reference scenarios](#reference-scenarios)

## Non-negotiable contract

- Use only `deck cloud` and `deck image`. Never call OpenAI
  directly, supply a provider key or construct a provider URL.
- Build the prompt locally from the approved brief. The backend must receive
  only that prompt, ratio, quality and, for edits, the explicit image bytes.
- Never send an entire `.deck`. `deck image edit --deck ...` opens the bundle
  locally and uploads only the asset targeted by `--slide` and `--element`.
- An `--out` preview is temporary and does not modify the deck. Never add it
  manually to the zip.
- Run `accept` only after visually inspecting the preview. Regeneration is
  a new paid job: obtain the user's agreement unless an explicit request
  has already authorized this new attempt.

## Login, workspace and credits

First check the session and selected workspace:

```sh
deck cloud status --json
deck cloud workspace --json
```

If the CLI is logged out, run `deck cloud login`, let the user authorize
the device on the Decktype page, then run `status` again. To switch workspace:

```sh
deck cloud workspace WORKSPACE_ID --json
```

Check the balance before every job and announce its cost:

```sh
deck image balance --json
```

`standard` costs 1 credit; `high` costs 4. Do not start if `remaining` is
lower than the cost. The balance belongs to the workspace and is shared across CLI,
desktop and web.

## Create an image

Start from an approved visual brief: subject, composition, mood, brand constraints,
ratio and relevant exclusions. Do not automatically attach text, notes or
other slides to the prompt.

Use a unique preview name so an old file is never confused with the
current result:

```sh
deck image generate \
  --prompt "PROMPT VALIDE" \
  --ratio 16:9 \
  --quality standard \
  --out /tmp/decktype-image-JOB-UNIQUE.png \
  --json
```

Ratios: `auto`, `16:9`, `1:1`, `4:5`. For CLI creation, `auto` uses Decktype's
default ratio `16:9`. Prefer an explicit ratio when the slide requires it.

The command waits for a terminal state, downloads only the preview and returns its
`job_id`. The deck remains unchanged.

## Edit an explicit image

First identify the exact slide and image element. Render the slide to inspect it,
then read `deck.json` locally to match the visible image to its `id`:

```sh
deck render presentation.deck --out /tmp/decktype-avant --slide N
unzip -p presentation.deck deck.json > /tmp/decktype-deck.json
```

Never choose an ambiguous element. Edit the deck image while preserving its displayed
ratio with `auto`:

```sh
deck image edit \
  --prompt "MODIFICATION VALIDEE" \
  --deck presentation.deck \
  --slide N \
  --element ELEMENT_ID \
  --ratio auto \
  --quality standard \
  --out /tmp/decktype-edit-JOB-UNIQUE.png \
  --json
```

For an explicitly chosen external PNG/JPEG, replace the three source options
with `--source chemin/source.png`. The source limit is 20 MiB. No other deck
content or asset is uploaded.

## Inspect, then accept

After JSON `status: "succeeded"`, open exactly the file indicated by `output`
with the available image viewer. Check framing, subject, readability, absence
of artifacts, fidelity to the brief and compatibility with the slide's image area.

Only then ask for an explicit choice: accept, regenerate at a new
cost, or continue the deck without this image.

New insertion:

```sh
deck image accept JOB_ID --deck presentation.deck --slide N --json
```

Replacement that preserves geometry and, on a bound slide, sets the correct
`asset` override:

```sh
deck image accept JOB_ID \
  --deck presentation.deck \
  --slide N \
  --replace ELEMENT_ID \
  --json
```

Do not blindly rerun `accept` after an interruption: inspect the deck to
avoid duplicate insertion. Then finish without exception:

```sh
deck validate presentation.deck --json
deck lint presentation.deck
deck render presentation.deck --out /tmp/decktype-apres
```

Open every affected PNG. For delivery, also apply all validation
and inspection rules in the main `SKILL.md`.

## Stable JSON

`--json` outputs deliberately contain no secrets or signed URLs:

- `balance`: `allocation`, `plan`, `remaining`, `reserved`, `resets_at`, `used`;
- `generate`, `edit`, `status`, `cancel`: `credit_cost`, optional `error_code`,
  `job_id`, optional `output`, `status`;
- `accept`: `asset_id`, `asset_path`, `deck`, `element_id`, `job_id`, `slide`.

States: `queued`, `generating`, `succeeded`, `accepted`, `failed`, `canceled`,
`expired`. Only `succeeded` with an inspected preview can be accepted.

## Quotas and lifecycle

- Free: generation not included, allocation 0.
- Pro: 50 credits per Stripe period.
- Autonomous: 100 credits per Stripe period.
- Unused credits do not roll over; no top-ups in v1.
- A usable preview consumes credits even if discarded.
- An unaccepted input or result expires after 24 hours.
- An accepted result becomes a durable private workspace asset and its bytes are
  also embedded in the `.deck` for offline use.
- The prompt and asset lineage are private workspace content, never
  analytics data. Do not copy them into logs or an unnecessary response.

## Error recovery

Preserve the prompt and keep the deck intact. Never invent a replacement image.

| Situation | Action |
| --- | --- |
| No session | `deck cloud login`, then recheck workspace and balance. |
| Expired session (401) | `deck cloud login`, then recheck workspace and balance. |
| Free / `IMAGE_NOT_INCLUDED` | Explain that Pro or Autonomous is required; continue with existing assets. |
| Credits exhausted | Run `deck image balance --json` again. On Pro, suggest Autonomous; on Autonomous, announce `resets_at`. Do not call the generator. |
| `failed` or moderation refusal | Report `error_code` without provider details. Offer to adjust the prompt, without retrying. |
| `canceled` or `expired` | Do not accept. Ask before starting any new paid job. |
| Service/network/polling unavailable | If a `job_id` is known, use `deck image status JOB_ID --json`; otherwise report the uncertainty and do not silently recreate it. |
| User rejects preview | Do not accept; continue the deck or ask permission for paid regeneration. |
| Failure during `accept` | Inspect the deck before retrying; validate and render if it already contains the asset. |

To request explicit cancellation:

```sh
deck image cancel JOB_ID --json
```

Canceling a queued job normally releases its reservation. Generation already in
progress may be charged: never promise a refund.

## Reference scenarios

1. **Hero**: approved brief, sufficient balance, `generate`, preview inspection,
   agreement, `accept` to insert, then validate/render/inspect.
2. **Retouch**: rendered slide, unambiguously chosen image element, `edit --deck
   --slide --element`, inspection, agreement, `accept --replace`, then verify that
   geometry is preserved.
3. **Exhaustion**: read `plan` and `resets_at`, explain upgrade or renewal,
   preserve the prompt and continue the deck without fabricating or reusing an image.
