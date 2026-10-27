import json
import re
import shlex
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "decktype"
SKILL_DIR = PLUGIN / "skills" / "decktype"
DECK_CLI_FINGERPRINT = ROOT / "tests" / "fixtures" / "deck-cli-1.3.2.json"
# Pieces stay separate: a contiguous PEM header in this file is rejected before commit.
PRIVATE_KEY_HEADER = "-----" + "BEGIN " + "PRIVATE KEY" + "-----"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_version(text: str):
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    if match is None:
        raise ValueError(f"no version in {text!r}")
    return tuple(int(part) for part in match.groups())


def public_documents(root=ROOT):
    return [
        root / "README.md",
        *sorted((root / "docs").glob("*.md")),
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
    root = ROOT

    def paths(self):
        root = self.root
        plugin = root / "plugins" / "decktype"
        return root, plugin

    def skill_files(self):
        _, plugin = self.paths()
        return sorted(path for path in (plugin / "skills" / "decktype").rglob("*") if path.is_file())

    def test_dual_marketplaces_point_to_one_versioned_plugin(self):
        root, plugin = self.paths()
        claude_marketplace = load_json(root / ".claude-plugin" / "marketplace.json")
        codex_marketplace = load_json(root / ".agents" / "plugins" / "marketplace.json")
        claude_manifest = load_json(plugin / ".claude-plugin" / "plugin.json")
        codex_manifest = load_json(plugin / ".codex-plugin" / "plugin.json")

        self.assertEqual(claude_marketplace["name"], "decktype-agent")
        self.assertEqual(codex_marketplace["name"], "decktype-agent")
        self.assertEqual(claude_manifest["name"], "decktype")
        self.assertEqual(codex_manifest["name"], "decktype")
        claude_entry = claude_marketplace["plugins"][0]
        codex_entry = codex_marketplace["plugins"][0]
        self.assertIn("version", claude_marketplace)
        self.assertIn("version", claude_entry)
        self.assertIn("version", claude_manifest)
        self.assertIn("version", codex_manifest)
        versions = [claude_marketplace["version"], claude_entry["version"], claude_manifest["version"], codex_manifest["version"]]
        for version in versions:
            self.assertIsInstance(version, str)
            self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        self.assertEqual(len(set(versions)), 1, f"manifest versions differ: {versions}")
        self.assertEqual(claude_entry["name"], "decktype")
        self.assertEqual(claude_entry["source"], "./plugins/decktype")
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
        files = self.skill_files()
        self.assertTrue(files, "generated skill directory is empty")
        corpus = "\n".join(path.read_bytes().decode("utf-8", errors="replace") for path in files)
        skill_path = self.root / "plugins" / "decktype" / "skills" / "decktype" / "SKILL.md"
        skill = skill_path.read_bytes().decode("utf-8", errors="replace")
        self.assertIn("name: decktype", skill)
        for command in ["deck templates list --json", "deck templates show"]:
            self.assertIn(command, corpus)
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

        for path in files:
            content = path.read_bytes().decode("utf-8", errors="replace").lower()
            for marker in ["/users/", "/home/", "~/dev/", "@kairia.fr", "kairia", "begin private key", "gho_", "api_key=", "api-key:", "password="]:
                self.assertNotIn(marker, content, f"{path.relative_to(self.root)} contains forbidden marker {marker!r}")

    def test_cited_deck_commands_exist_in_published_cli(self):
        fingerprint = load_json(DECK_CLI_FINGERPRINT)
        commands = fingerprint["commands"]
        cited = []
        root, _ = self.paths()
        for path in public_documents(root):
            for invocation in cited_deck_invocations(path.read_text(encoding="utf-8")):
                cited.append((path.relative_to(ROOT), invocation))
        self.assertTrue(cited, "no deck command was extracted from the public documents")

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
        _, plugin = self.paths()
        deck_path = plugin / "examples" / "agent-workflow.deck"
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
            preview = plugin / "examples" / f"slide-{index:02d}.png"
            self.assertTrue(preview.is_file(), f"{preview.name} is missing")
            self.assertGreater(preview.stat().st_size, 1_000, f"{preview.name} looks empty")

    def test_readme_has_both_install_paths_and_tracking(self):
        root, _ = self.paths()
        readme = (root / "README.md").read_text(encoding="utf-8")
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
        root, _ = self.paths()
        submission = (root / "docs" / "directory-submission.md").read_text(encoding="utf-8")
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

    def test_sync_copy_accepts_new_skill_names_and_versions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            shutil.copytree(ROOT / ".claude-plugin", root / ".claude-plugin")
            shutil.copytree(ROOT / ".agents", root / ".agents")
            shutil.copytree(ROOT / "plugins", root / "plugins")
            shutil.copytree(ROOT / "tests", root / "tests")
            shutil.copytree(ROOT / "docs", root / "docs")
            shutil.copy2(ROOT / "README.md", root / "README.md")
            skill_dir = root / "plugins" / "decktype" / "skills" / "decktype"
            shutil.rmtree(skill_dir)
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("---\nname: decktype\n---\nGenerated skill.\n", encoding="utf-8")
            (skill_dir / "guide").write_text("deck templates list --json\ndeck regenerate\ndeck validate\ndeck lint\n", encoding="utf-8")
            nested = skill_dir / "nested"
            nested.mkdir()
            (nested / "new-reference.md").write_text("deck templates show\ndeck render\ndeck import\ndeck export\ndeck pdf\ndeck cloud sync --new-option\ndeck image create --new-option\ndecktype-cloud\n", encoding="utf-8")
            paths = [root / ".claude-plugin" / "marketplace.json", root / "plugins/decktype/.claude-plugin/plugin.json", root / "plugins/decktype/.codex-plugin/plugin.json"]
            marketplace = load_json(paths[0])
            marketplace["version"] = marketplace["plugins"][0]["version"] = "9.9.9"
            paths[0].write_text(json.dumps(marketplace), encoding="utf-8")
            for path in paths[1:]:
                manifest = load_json(path)
                manifest["version"] = "9.9.9"
                path.write_text(json.dumps(manifest), encoding="utf-8")

            suite = unittest.TestSuite()
            for name in ["test_dual_marketplaces_point_to_one_versioned_plugin", "test_public_skill_is_safe_and_actionable", "test_readme_has_both_install_paths_and_tracking", "test_directory_submission_texts_are_bilingual"]:
                case = ReleaseContractTests(name)
                case.root = root
                suite.addTest(case)
            result = unittest.TestResult()
            suite.run(result)
            self.assertEqual(result.errors, [])
            self.assertEqual(result.failures, [])

            mutations = [
                (nested / "new-reference.md", "kairia", "test_public_skill_is_safe_and_actionable"),
                (nested / "new-reference.md", "/Users/example", "test_public_skill_is_safe_and_actionable"),
                (nested / "new-reference.md", "/home/example", "test_public_skill_is_safe_and_actionable"),
                (nested / "new-reference.md", "~/dev/example", "test_public_skill_is_safe_and_actionable"),
                (nested / "new-reference.md", "person@kairia.fr", "test_public_skill_is_safe_and_actionable"),
                (nested / "new-reference.md", "password=secret", "test_public_skill_is_safe_and_actionable"),
                (nested / "new-reference.md", PRIVATE_KEY_HEADER, "test_public_skill_is_safe_and_actionable"),
                (nested / "new-reference.md", "gho_secret", "test_public_skill_is_safe_and_actionable"),
                (nested / "new-reference.md", "api_key=secret", "test_public_skill_is_safe_and_actionable"),
                (nested / "new-reference.md", "api-key: secret", "test_public_skill_is_safe_and_actionable"),
            ]
            for command in ["deck templates list --json", "deck templates show", "deck regenerate", "deck validate", "deck lint", "deck render", "deck import", "deck export"]:
                command_file = next(path for path in skill_dir.rglob("*") if path.is_file() and command in path.read_text(encoding="utf-8"))
                mutations.append((command_file, command, "test_public_skill_is_safe_and_actionable"))
            version_fields = [
                (paths[0], "version"),
                (paths[0], "plugins"),
                (paths[1], "version"),
                (paths[2], "version"),
            ]
            for path, field in version_fields:
                mutations.append((path, f"version:{field}", "test_dual_marketplaces_point_to_one_versioned_plugin"))
            mutations.extend([
                (paths[0], "version:malformed", "test_dual_marketplaces_point_to_one_versioned_plugin"),
                (paths[0], "version:missing", "test_dual_marketplaces_point_to_one_versioned_plugin"),
            ])
            for path, marker, test_name in mutations:
                original = path.read_text(encoding="utf-8")
                if marker.startswith("version:"):
                    data = load_json(path)
                    field = marker.split(":", 1)[1]
                    if field == "plugins":
                        data["plugins"][0]["version"] = "9.9.8"
                    elif field == "missing":
                        del data["version"]
                    elif field == "malformed":
                        data["version"] = "9.9"
                    elif field == "version":
                        data["version"] = "9.9.8"
                    else:
                        data["version"] = "9.9.8"
                    path.write_text(json.dumps(data), encoding="utf-8")
                elif marker.startswith("deck "):
                    path.write_text(original.replace(marker, ""), encoding="utf-8")
                else:
                    path.write_text(original + "\n" + marker, encoding="utf-8")
                case = ReleaseContractTests(test_name)
                case.root = root
                negative_result = unittest.TestResult()
                case.run(negative_result)
                self.assertEqual(len(negative_result.failures), 1, f"mutation {marker!r} did not fail its contract")
                self.assertEqual(negative_result.errors, [], f"mutation {marker!r} caused an execution error")
                path.write_text(original, encoding="utf-8")

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
