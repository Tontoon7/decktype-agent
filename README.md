# Decktype Agent

Build presentations with Claude Code or Codex, then keep editing them as native `.deck` files in Decktype.

[Download Decktype for macOS](https://decktype.com/en/download?utm_source=github&utm_medium=plugin&utm_campaign=claude_code_plugin_launch) · [Read the Claude Code PowerPoint tutorial](https://decktype.com/en/blog/claude-code-powerpoint?utm_source=github&utm_medium=plugin&utm_campaign=claude_code_plugin_launch)

![A Decktype presentation generated through the public agent skill](plugins/decktype/examples/slide-01.png)

The plugin gives both agents the same workflow:

- agree on the audience and decision before generating slides;
- build with structured Decktype templates instead of flattened screenshots;
- preserve manual edits when the agent revises the content;
- validate, lint, render, and inspect every changed slide;
- deliver an editable `.deck`, with optional PowerPoint export.

## Requirements

- A Mac with Apple silicon.
- The [Decktype app](https://decktype.com/en/download?utm_source=github&utm_medium=plugin&utm_campaign=claude_code_plugin_launch).
- Claude Code or Codex.

After installing Decktype, open the app and choose **Connect an agent** once. This makes the local `deck` CLI available to your agent.

## Install for Claude Code

```sh
claude plugin marketplace add Tontoon7/decktype-agent
claude plugin install decktype@decktype-agent
```

Start a new Claude Code session, or run `/reload-plugins` if the installer asks you to reload.

## Install for Codex

```sh
codex plugin marketplace add Tontoon7/decktype-agent
codex plugin add decktype@decktype-agent
```

Start a new Codex session after installation.

## Use it

Ask naturally. The `decktype` skill activates when the request needs an editable presentation or a `.deck` file.

```text
Create an editable 7-slide presentation for a product review.
Audience: the leadership team.
Decision: approve a two-week pilot.
Use only facts from brief.md, show me the outline before generating,
and export a PowerPoint after I approve the rendered deck.
```

For an existing presentation:

```text
Revise customer-review.deck with the new priorities in notes.md.
Keep my manual layout changes, render every modified slide,
and show me the result before exporting.
```

## Example

The repository includes a real four-slide presentation built with the standard template pack:

- [Open or download the editable `.deck`](plugins/decktype/examples/agent-workflow.deck)
- [Title](plugins/decktype/examples/slide-01.png)
- [Thesis](plugins/decktype/examples/slide-02.png)
- [Workflow](plugins/decktype/examples/slide-03.png)
- [Next step](plugins/decktype/examples/slide-04.png)

## What is public

This repository contains only the agent workflow, plugin manifests, references, tests, and example assets. The Decktype application source is not part of the plugin.

The plugin does not add hooks, background services, an MCP server, or bundled executables. It calls the local `deck` CLI installed through Decktype and works on files the user places in scope.

## Validate the repository

```sh
python3 -m unittest -v tests/test_release.py
claude plugin validate --strict plugins/decktype
claude plugin validate --strict .
```

The release tests also validate the example bundle when the `deck` CLI is available.

## Learn the complete workflow

Read [Claude Code PowerPoint: Build Editable Presentations with Decktype](https://decktype.com/en/blog/claude-code-powerpoint?utm_source=github&utm_medium=plugin&utm_campaign=claude_code_plugin_launch), or use the [agent connection guide](https://decktype.com/en/agents?utm_source=github&utm_medium=plugin&utm_campaign=claude_code_plugin_launch) if the CLI is not detected.

## License

MIT. See [LICENSE](LICENSE).

