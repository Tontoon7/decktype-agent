# Decks hosted in Decktype Cloud

Read this entire reference before publishing, updating, retrieving, restoring
or sharing a hosted `.deck`.

## Hard rules

- Use only `deck cloud` commands. Never call a remote
  service directly or construct or reuse an object storage address, even
  if the caller provides one.
- Never display a session, installation token or keychain contents.
- Never write a share link to a file, note, log,
  commit or intermediate message. Copy it only into the final response to
  the user who explicitly requested it.
- Update a deck only with the `deck_id` and revision returned by a
  previous trusted Decktype command. Supply `--deck-id` and
  `--base-revision` together; never guess either value.
- Never force a write after a conflict. Retrieve and examine the
  current revision, or publish a separate copy.
- Validate every retrieved bundle before editing, publishing or delivering it.
- Restore an older version only at the user's explicit request, and
  only after showing them the history. Restoration is a write:
  it creates a new current revision.

## Authentication and discovery

Check status and the selected workspace:

```sh
deck cloud status --json
deck cloud workspace --json
```

If needed, run `deck cloud login`, complete the requested activation, then
check status again. Next, list decks and retain only the ID and
revision needed for the current operation:

```sh
deck cloud list --json
```

Never copy authentication secrets into a command or file.

## Mandatory loop before publication

Follow this sequence without shortcuts:

```text
inspect -> validate -> lint -> regenerate -> validate -> render -> inspect
-> cloud push -> optionally cloud share
```

In practice:

```sh
deck inspect mon-deck.deck --json
deck validate mon-deck.deck --json
deck lint mon-deck.deck
deck regenerate mon-deck.deck
deck validate mon-deck.deck --json
deck render mon-deck.deck --out slides-png
```

Open and inspect every generated PNG. Fix overflow, empty cards,
hierarchy problems or overly dense slides, then repeat the loop before any
upload.

## Publish a new deck

Publish only after completing the mandatory loop:

```sh
deck cloud push mon-deck.deck --json
```

Keep the report's `deck_id` and `revision` as the trusted identity for
a future update. Report success only after the cloud commit
returns.

## Update a deck

Start with a `deck_id` and revision obtained from `deck cloud list --json` or a
previous `deck cloud push --json`. After editing and completing the entire local loop,
use both values together:

```sh
deck cloud push mon-deck.deck --deck-id DECK_ID --base-revision REVISION --json
```

Replace `DECK_ID` and `REVISION` only with values from the trusted report.

On a conflict:

1. Never force an overwrite or reuse the old revision.
2. Retrieve the current deck to a new file, then validate and inspect it.
3. Either transfer the edits to this version and repeat the entire loop, or
   publish the local work as a copy without update options.

## Retrieve a deck

Write to an explicit local path, then validate immediately:

```sh
deck cloud pull DECK_ID --out deck-courant.deck --json
deck validate deck-courant.deck --json
deck inspect deck-courant.deck --json
```

Never edit or deliver `deck-courant.deck` if validation fails. To
publish it again after editing, repeat the mandatory loop and obtain the current
revision through a trusted command.

## View version history

Every publication creates an immutable revision. List them from newest to
oldest:

```sh
deck cloud revisions DECK_ID --json
```

Each entry contains `revision`, `created_at`, `client_source`, `byte_length`,
`sha256`, the author and `is_current` (the current version). For a deck with a long
history, continue with `--cursor` using `next_cursor`, and bound results with
`--limit` (1 to 100).

Retrieve a specific version without changing the hosted deck:

```sh
deck cloud pull DECK_ID --out version-42.deck --revision 42 --json
deck validate version-42.deck --json
```

This is the safe way to compare two versions or recover lost content:
nothing changes in the cloud.

## Restore a version

Restoration never deletes anything: the chosen revision is copied to the head,
so the full history remains and restoration itself is reversible.

```sh
deck cloud restore DECK_ID 42 --json
```

The report returns `restored_from` (the restored version) and `revision` (the new
current version). Before running this command:

1. Show the history to the user and have them confirm the version number.
2. If needed, check its content with `pull --revision` followed by `validate`.
3. Warn people currently editing this deck in a collaborative session
   to leave it: restoring during an open session may be undone by
   the session still in progress.

Restoring the already-current version is rejected with an explicit message:
this is never an error to bypass; it means there is nothing to restore.

## Share and revoke

Create a link only at the user's explicit request and after a successful
publication:

```sh
deck cloud share DECK_ID --json
```

The output contains the requested result. Do not redirect it to a file or
paste it anywhere except the final response. Retain the `share_id` only as
long as needed for a possible revocation:

```sh
deck cloud unshare DECK_ID SHARE_ID --json
```

Revocation is idempotent: repeating it is safe if the previous result is
uncertain. Do not create a link if the user asks only to host or
update the deck.
