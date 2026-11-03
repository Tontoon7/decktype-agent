import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/decktype-connector"
DOCUMENT = ROOT / "docs/openai-submission.md"
MEMBERS = [".codex-plugin/plugin.json", ".mcp.json", "SUBMISSION-NOTES.md",
           "assets/icon-dark.png", "assets/icon.png", "mcp.json", "plugin.json"]
TOOLS = {"list_themes", "list_templates", "create_deck", "get_deck_structure",
         "get_slide_preview", "update_deck", "list_decks", "get_edit_link"}


class SubmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("submission", ROOT / "scripts/build_openai_submission.py")
        cls.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.builder)

    def test_real_build_is_exact_reproducible_and_independent_of_app(self):
        with tempfile.TemporaryDirectory() as temp:
            archives = [Path(temp) / name for name in ("first.zip", "second.zip")]
            for output in archives:
                result = subprocess.run([sys.executable, str(ROOT / "scripts/build_openai_submission.py"),
                                         "--output", str(output)], capture_output=True, text=True,
                                        env={"PATH": "", "PYTHONDONTWRITEBYTECODE": "1"})
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(archives[0].read_bytes(), archives[1].read_bytes())
            with zipfile.ZipFile(archives[0]) as archive:
                self.assertEqual(archive.namelist(), MEMBERS)
                for entry in archive.infolist():
                    self.assertEqual(archive.read(entry), (PLUGIN / entry.filename).read_bytes())
                    self.assertEqual(entry.date_time, (1980, 1, 1, 0, 0, 0))
                    self.assertEqual(entry.external_attr >> 16, 0o100644)
                    self.assertEqual(entry.create_system, 3)
                    self.assertEqual(entry.compress_type, zipfile.ZIP_STORED)
                    self.assertEqual((entry.extra, entry.comment, entry.flag_bits), (b"", b"", 0))
                self.assertEqual(archive.comment, b"")

    def test_remote_contract_and_brand(self):
        for name in ("mcp.json", ".mcp.json"):
            self.assertEqual(json.loads((PLUGIN / name).read_text()), {
                "mcpServers": {"decktype": {"type": "http", "url": "https://api.decktype.com/mcp"}}})
        manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
        self.assertEqual((manifest["name"], manifest["version"]), ("decktype-connector", "0.1.0"))
        self.assertEqual(manifest["interface"]["brandColor"], "#191713")
        for name in ("assets/icon.png", "assets/icon-dark.png"):
            data = (PLUGIN / name).read_bytes()
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(data[16:24], (512).to_bytes(4, "big") * 2)
        notes = (PLUGIN / "SUBMISSION-NOTES.md").read_text()
        for text in ("Commerce: none", "OAuth", "PKCE", "pending"):
            self.assertIn(text, notes)

    def test_rejects_unsafe_inputs_before_creating_archive(self):
        mutations = [
            ("mcp.json", lambda p: p.write_text('{"mcpServers":{"a":{},"b":{}}}')),
            (".mcp.json", lambda p: p.write_text(p.read_text().replace('"type":', '"headers": {}, "type":'))),
            (".mcp.json", lambda p: p.write_text(p.read_text().replace('"http"', '"stdio"'))),
            ("mcp.json", lambda p: p.write_text(p.read_text().replace('https://api.', 'http://api.'))),
            ("mcp.json", lambda p: p.write_text(p.read_text().replace('"type":', '"url":"https://other.invalid", "type":'))),
            ("plugin.json", lambda p: p.write_text(p.read_text().replace('"name":', '"hooks": {}, "name":'))),
            ("plugin.json", lambda p: p.write_text(p.read_text().replace('"0.1.0"', '"0.1.1"'))),
            ("plugin.json", lambda p: p.write_text("[]")),
            (".codex-plugin/plugin.json", lambda p: p.write_text(p.read_text().replace(
                "Create presentations", r"Authorization\u003a Bearer example. Create presentations"))),
            ("hooks/hook.json", lambda p: p.write_text("{}")),
            ("unexpected.txt", lambda p: p.write_text("unexpected")),
            ("assets/icon.png", lambda p: p.chmod(0o755)),
            ("SUBMISSION-NOTES.md", lambda p: p.write_text("gh" + "p_" + "x" * 36)),
            ("SUBMISSION-NOTES.md", lambda p: p.write_text("-----" + "BEGIN " + "PRIVATE KEY-----")),
            ("SUBMISSION-NOTES.md", lambda p: p.write_text("Authorization: Bearer example")),
            ("SUBMISSION-NOTES.md", lambda p: (p.unlink(), p.symlink_to(DOCUMENT))),
        ]
        for name, mutate in mutations:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                source = Path(temp) / "plugin"
                shutil.copytree(PLUGIN, source)
                target = source / name
                target.parent.mkdir(parents=True, exist_ok=True)
                mutate(target)
                output = Path(temp) / "submission.zip"
                with self.assertRaisesRegex(ValueError, r".+"):
                    self.builder.build(source, DOCUMENT, output)
                self.assertFalse(output.exists())

    def test_output_cannot_overwrite_sources_or_existing_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "plugin"
            shutil.copytree(PLUGIN, source)
            for output in (source / "archive.zip", DOCUMENT, Path(temp) / "existing.zip"):
                if output.name == "existing.zip":
                    output.write_bytes(b"previous")
                with self.assertRaises(ValueError):
                    self.builder.build(source, DOCUMENT, output)
            self.assertEqual((Path(temp) / "existing.zip").read_bytes(), b"previous")

    def test_cli_refusal_has_nonzero_exit_and_no_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "plugins/decktype-connector"
            shutil.copytree(PLUGIN, source)
            (root / "scripts").mkdir()
            (root / "docs").mkdir()
            script = root / "scripts/build_openai_submission.py"
            shutil.copyfile(ROOT / "scripts/build_openai_submission.py", script)
            shutil.copyfile(DOCUMENT, root / "docs/openai-submission.md")
            (source / "hooks.json").write_text("{}")
            output = root / "refused.zip"
            result = subprocess.run([sys.executable, str(script), "--output", str(output)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("unexpected or missing plugin files", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(output.exists())

    def test_commercial_mutations_in_every_editorial_field_and_listing(self):
        prohibited = ["Only $12", "12 EUR", "€ 12", "SUBSCRIPTION", "paid plan", "Pro plan",
                      "Autonomous plan", "free trial", "14-day trial", "upgrade to Pro",
                      "limited-time offer", "20% off", "PROMOTION", "subscribe now", "EUR 12",
                      "save 20%", "special offer", "buy now", "on sale", "see pricing",
                      "Decktype Pro", "Decktype Autonomous", "12 CAD", "CAD 12"]
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "plugin"
            shutil.copytree(PLUGIN, source)
            output = Path(temp) / "archive.zip"
            for name in ("plugin.json", ".codex-plugin/plugin.json"):
                original = (source / name).read_text()
                data = json.loads(original)
                fields = [(k,) for k, v in data.items() if isinstance(v, str)] + [("keywords", 0)]
                if "interface" in data:
                    fields += [("interface", k) for k, v in data["interface"].items() if isinstance(v, str)]
                    fields += [("interface", "defaultPrompt", i) for i in range(len(data["interface"]["defaultPrompt"]))]
                for field in fields:
                    for text in prohibited:
                        mutated = json.loads(original)
                        parent = mutated
                        for part in field[:-1]:
                            parent = parent[part]
                        parent[field[-1]] = text
                        (source / name).write_text(json.dumps(mutated))
                        with self.assertRaisesRegex(ValueError, "commercial"):
                            self.builder.build(source, DOCUMENT, output)
                        self.assertFalse(output.exists())
                (source / name).write_text(original)
        listing = DOCUMENT.read_text().split("## Directory listing\n", 1)[1].split("\n## ", 1)[0]
        for text in prohibited:
            with self.subTest(listing=text), tempfile.TemporaryDirectory() as temp:
                document = Path(temp) / "submission.md"
                document.write_text(DOCUMENT.read_text().replace(listing, listing + text + "\n"))
                with self.assertRaisesRegex(ValueError, "commercial"):
                    self.builder.build(PLUGIN, document, Path(temp) / "submission.zip")
        for text in ("Professional presentations", "Plan the presentation", "A product review",
                     "Use premium/stats slots", "Improve the proposal"):
            self.builder.check_commerce(text, "legitimate text")

    def test_review_matrix_and_listing(self):
        text = DOCUMENT.read_text()
        rows = [line.split("|")[1:-1] for line in text.splitlines() if re.match(r"\| [PN]\d+\s*\|", line)]
        self.assertEqual([row[0].strip() for row in rows], ["P1", "P2", "P3", "P4", "P5", "N1", "N2", "N3"])
        for row in rows:
            self.assertEqual(len(row), 4)
            self.assertTrue(all(cell.strip() for cell in row))
        self.assertEqual(set(re.findall(r"`([a-z_]+)`", " ".join(row[2] for row in rows[:5]))), TOOLS)
        self.assertIn("exact same matrix on web and mobile", text)
        for suffix in ("", "/en/contact", "/en/privacy", "/en/terms", "/en/connectors"):
            self.assertIn("https://decktype.com" + suffix, text)
        for path in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"):
            self.assertNotIn("decktype-connector", (ROOT / path).read_text())


if __name__ == "__main__":
    unittest.main()
