import json
import re
import shlex
import shutil
import subprocess
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "decktype"
SKILL_DIR = PLUGIN / "skills" / "decktype"
PLUGIN_VERSION = "1.1.0"
DECK_CLI_FINGERPRINT = ROOT / "tests" / "fixtures" / "deck-cli-1.3.2.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_version(text: str):
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    if match is None:
        raise ValueError(f"no version in {text!r}")
    return tuple(int(part) for part in match.groups())


def public_documents():
    return [
        ROOT / "README.md",
        SKILL_DIR / "SKILL.md",
        *sorted((SKILL_DIR / "references").glob("*.md")),
        *sorted((ROOT / "docs").glob("*.md")),
    ]


def cited_deck_invocations(text: str):
    """Return every `deck ...` invocation from inline code spans and code block lines."""
    invocations = re.findall(r"`(deck [^`\n]+)`", text)
    in_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_block = not in_block
            continue
        if in_block and stripped.startswith("deck "):
            invocations.append(stripped)
    return invocations


def parse_deck_invocation(invocation: str):
    """Split `deck <command> [args] [--options]` into a command key and its long options."""
    try:
        tokens = shlex.split(invocation)
    except ValueError:
        tokens = invocation.split()
    tokens = tokens[1:]
    if not tokens or tokens[0].startswith("-"):
        command = ""
    elif tokens[0] == "templates" and len(tokens) > 1:
        command = f"templates {tokens[1]}"
    else:
        command = tokens[0]
    options = {token.split("=", 1)[0] for token in tokens if token.startswith("--")}
    return command, options


class ReleaseContractTests(unittest.TestCase):
    def test_dual_marketplaces_point_to_one_versioned_plugin(self):
        claude_marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")
        codex_marketplace = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
        claude_manifest = load_json(PLUGIN / ".claude-plugin" / "plugin.json")
        codex_manifest = load_json(PLUGIN / ".codex-plugin" / "plugin.json")

        self.assertEqual(claude_marketplace["name"], "decktype-agent")
        self.assertEqual(codex_marketplace["name"], "decktype-agent")
        self.assertEqual(claude_manifest["name"], "decktype")
        self.assertEqual(codex_manifest["name"], "decktype")
        self.assertEqual(claude_marketplace["version"], PLUGIN_VERSION)
        self.assertEqual(claude_manifest["version"], PLUGIN_VERSION)
        self.assertEqual(codex_manifest["version"], PLUGIN_VERSION)

        claude_entry = claude_marketplace["plugins"][0]
        codex_entry = codex_marketplace["plugins"][0]
        self.assertEqual(claude_entry["name"], "decktype")
        self.assertEqual(claude_entry["source"], "./plugins/decktype")
        self.assertEqual(claude_entry["version"], PLUGIN_VERSION)
        self.assertEqual(codex_entry["name"], "decktype")
        self.assertEqual(codex_entry["source"]["path"], "./plugins/decktype")
        self.assertEqual(codex_entry["policy"]["installation"], "AVAILABLE")

        self.assertEqual(claude_entry["description"], claude_manifest["description"])
        self.assertEqual(claude_entry["tags"], claude_manifest["keywords"])
        self.assertEqual(codex_manifest["keywords"], claude_manifest["keywords"])
        for manifest in [claude_entry, claude_manifest, codex_manifest]:
            self.assertTrue(manifest["homepage"].startswith("https://decktype.com/"), manifest["homepage"])
            self.assertIn("Apple silicon", manifest["description"])
            self.assertIn("PDF", manifest["description"])
        self.assertIn("Apple silicon", codex_manifest["interface"]["longDescription"])
        self.assertLessEqual(len(codex_manifest["interface"]["defaultPrompt"]), 3)

    def test_public_skill_is_safe_and_actionable(self):
        skill_path = SKILL_DIR / "SKILL.md"
        templates_path = SKILL_DIR / "references" / "templates.md"
        format_path = SKILL_DIR / "references" / "format.md"
        skill = skill_path.read_text(encoding="utf-8")
        references = templates_path.read_text(encoding="utf-8") + format_path.read_text(encoding="utf-8")
        corpus = skill + references

        self.assertIn("name: decktype", skill)
        self.assertIn('export PATH="$HOME/Library/Application Support/Decktype/bin:$PATH"', skill)
        self.assertIn("deck templates list --json", corpus)
        self.assertIn("deck templates show", corpus)
        for command in [
            "deck regenerate",
            "deck validate",
            "deck lint",
            "deck render",
            "deck import",
            "deck export",
            "deck pdf",
        ]:
            self.assertIn(command, corpus)

        for private_marker in [
            "/Users/",
            "@kairia.fr",
            "decktype-cloud",
            "deck cloud",
            "deck image",
            "pack: kairia",
            "deck-v0",
            "docs/format",
        ]:
            self.assertNotIn(private_marker.lower(), corpus.lower())

    def test_cited_deck_commands_exist_in_published_cli(self):
        fingerprint = load_json(DECK_CLI_FINGERPRINT)
        commands = fingerprint["commands"]
        cited = []
        for path in public_documents():
            for invocation in cited_deck_invocations(path.read_text(encoding="utf-8")):
                cited.append((path.relative_to(ROOT), invocation))
        self.assertGreater(len(cited), 10, "no deck command was extracted from the public documents")

        for path, invocation in cited:
            command, options = parse_deck_invocation(invocation)
            allowed = set(fingerprint["global_options"])
            if command:
                self.assertIn(command, commands, f"{path}: `{invocation}` is not a public deck {fingerprint['version']} command")
                allowed |= set(commands[command]["options"])
            unknown = options - allowed
            self.assertFalse(unknown, f"{path}: `{invocation}` cites unknown options {sorted(unknown)}")

        self.assertIsNotNone(shutil.which("deck"), "deck CLI is required for release validation")
        version = subprocess.run(["deck", "--version"], check=True, capture_output=True, text=True).stdout
        installed = parse_version(version)
        live_checked = 0
        for command, contract in commands.items():
            # A command newer than the installed CLI is covered by the fingerprint above only.
            if parse_version(contract.get("requires", "0.0.0")) > installed:
                continue
            result = subprocess.run(
                ["deck", *command.split(), "--help"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, f"deck {command} --help: {result.stdout}{result.stderr}")
            for option in contract["options"]:
                self.assertIn(option, result.stdout, f"deck {command} --help does not list {option}")
            live_checked += 1
        self.assertGreater(live_checked, 0)

    def test_example_bundle_is_valid_and_public(self):
        deck_path = PLUGIN / "examples" / "agent-workflow.deck"
        self.assertTrue(deck_path.is_file(), "example .deck is missing")
        self.assertIsNotNone(shutil.which("deck"), "deck CLI is required for release validation")

        result = subprocess.run(
            ["deck", "validate", str(deck_path), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["valid"], report)
        self.assertEqual(report["errors"], 0, report)

        with zipfile.ZipFile(deck_path) as bundle:
            deck = json.loads(bundle.read("deck.json"))
        self.assertEqual(len(deck["slides"]), 4)
        self.assertTrue(all(slide.get("template", {}).get("pack") == "standard" for slide in deck["slides"]))
        self.assertTrue(all(slide.get("elements") for slide in deck["slides"]))
        self.assertNotIn("kairia", json.dumps(deck).lower())

        for index in range(1, 5):
            preview = PLUGIN / "examples" / f"slide-{index:02d}.png"
            self.assertTrue(preview.is_file(), f"{preview.name} is missing")
            self.assertGreater(preview.stat().st_size, 1_000, f"{preview.name} looks empty")

    def test_readme_has_both_install_paths_and_tracking(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for command in [
            "claude plugin marketplace add Tontoon7/decktype-agent",
            "claude plugin install decktype@decktype-agent",
            "codex plugin marketplace add Tontoon7/decktype-agent",
            "codex plugin add decktype@decktype-agent",
        ]:
            self.assertIn(command, readme)

        self.assertIn("https://decktype.com/en/blog/claude-code-powerpoint", readme)
        self.assertIn("utm_source=github", readme)
        self.assertIn("utm_medium=plugin", readme)
        self.assertIn("utm_campaign=claude_code_plugin_launch", readme)
        self.assertIn("plugins/decktype/examples/slide-01.png", readme)
        self.assertIn("https://decktype.com/en/pricing?utm_source=github", readme)
        for mention in ["Apple silicon", "macOS 11", "Pro", "Autonomous", "deck pdf"]:
            self.assertIn(mention, readme)

    def test_directory_submission_texts_are_bilingual(self):
        submission = (ROOT / "docs" / "directory-submission.md").read_text(encoding="utf-8")
        self.assertIn("## English", submission)
        self.assertIn("## Français", submission)
        for command in [
            "claude plugin marketplace add Tontoon7/decktype-agent",
            "claude plugin install decktype@decktype-agent",
            "codex plugin marketplace add Tontoon7/decktype-agent",
            "codex plugin add decktype@decktype-agent",
        ]:
            self.assertEqual(submission.count(command), 2, command)
        for url in [
            "https://decktype.com/en/privacy",
            "https://decktype.com/en/terms",
            "https://github.com/Tontoon7/decktype-agent",
        ]:
            self.assertIn(url, submission)
        for mention in ["Apple silicon", "macOS 11", "Pro", "12"]:
            self.assertIn(mention, submission)
        # The version tag is published only after release approval: do not link or create it here.
        self.assertNotIn("git tag", submission)
        self.assertNotIn("/releases/tag/", submission)

    def test_text_release_contains_no_private_paths_or_credentials(self):
        text_extensions = {".md", ".json", ".py", ".txt", ".yml", ".yaml"}
        corpus = "\n".join(
            path.read_text(encoding="utf-8")
            for path in ROOT.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and "tests" not in path.parts
            and path.suffix in text_extensions
        )
        for forbidden in [
            "/Users/axel",
            "BEGIN PRIVATE KEY",
            "gho_",
            "api_key=",
            "api-key:",
            "password=",
        ]:
            self.assertNotIn(forbidden, corpus)


if __name__ == "__main__":
    unittest.main()
