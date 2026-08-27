import json
import shutil
import subprocess
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "decktype"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


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
        self.assertEqual(claude_manifest["version"], "1.0.0")
        self.assertEqual(codex_manifest["version"], "1.0.0")

        claude_entry = claude_marketplace["plugins"][0]
        codex_entry = codex_marketplace["plugins"][0]
        self.assertEqual(claude_entry["name"], "decktype")
        self.assertEqual(claude_entry["source"], "./plugins/decktype")
        self.assertEqual(claude_entry["version"], "1.0.0")
        self.assertEqual(codex_entry["name"], "decktype")
        self.assertEqual(codex_entry["source"]["path"], "./plugins/decktype")
        self.assertEqual(codex_entry["policy"]["installation"], "AVAILABLE")

    def test_public_skill_is_safe_and_actionable(self):
        skill_path = PLUGIN / "skills" / "decktype" / "SKILL.md"
        templates_path = PLUGIN / "skills" / "decktype" / "references" / "templates.md"
        format_path = PLUGIN / "skills" / "decktype" / "references" / "format.md"
        skill = skill_path.read_text(encoding="utf-8")
        references = templates_path.read_text(encoding="utf-8") + format_path.read_text(encoding="utf-8")
        corpus = skill + references

        self.assertIn("name: decktype", skill)
        self.assertIn("deck templates list --json", corpus)
        self.assertIn("deck templates show", corpus)
        for command in [
            "deck regenerate",
            "deck validate",
            "deck lint",
            "deck render",
            "deck import",
            "deck export",
        ]:
            self.assertIn(command, corpus)

        for private_marker in [
            "/Users/",
            "@kairia.fr",
            "decktype-cloud",
            "deck cloud",
            "deck image",
            "pack: kairia",
        ]:
            self.assertNotIn(private_marker.lower(), corpus.lower())

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
