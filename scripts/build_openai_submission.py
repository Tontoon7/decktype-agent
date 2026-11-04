"""Build the connector preparation archive; this is not an OpenAI schema validator."""

import argparse
import io
import json
import re
import stat
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MCP_URL = "https://api.decktype.com/mcp"
MCP_CONFIGS = {
    "mcp.json": {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
        "mcpServers": {"decktype": {
            "type": "streamable-http",
            "url": MCP_URL,
            "extensions": {"com.openai": {"auth": {
                "type": "oauth",
                "client": {"mode": "dcr"},
                "baseScopes": ["decks:read", "decks:write"],
            }}},
        }},
    },
    ".mcp.json": {"mcpServers": {"decktype": {"url": MCP_URL}}},
}
FILES = (".codex-plugin/plugin.json", ".mcp.json", "SUBMISSION-NOTES.md",
         "assets/icon-dark.png", "assets/icon.png", "mcp.json", "plugin.json")
COMMERCIAL = re.compile(
    r"[$€£¥₹]|\b\d+(?:[.,]\d+)?\s*(?:USD|EUR|GBP|CAD|AUD|CHF|JPY|CNY|INR|dollars?|euros?)\b|"
    r"\b(?:subscriptions?|subscribe|paid\s+(?:plans?|tiers?|offers?)|"
    r"(?:pro|autonomous|premium)\s+(?:plans?|tiers?|subscriptions?)|"
    r"upgrade\s+to\s+(?:pro|autonomous|premium)|decktype\s+(?:pro|autonomous|premium)|trials?|promotions?|promotional|"
    r"discounts?|coupons?|pricing|limited[ -]time\s+offers?|special\s+offers?|buy\s+now|on\s+sale)\b|"
    r"\b(?:USD|EUR|GBP|CAD|AUD|CHF|JPY|CNY|INR)\s*\d|\b\d+\s*%\s*off\b|\bsave\s+\d+\s*%", re.I)
SECRETS = re.compile(
    r"gh[pousr]_|github_pat_|sk-[a-zA-Z0-9]{16,}|BEGIN\s+(?:RSA\s+|EC\s+)?PRIVATE\s+KEY|"
    r"(?:api[_-]?key|password|client_secret|access_token)\s*[\"']?\s*[:=]|"
    r"authorization\s*:\s*bearer|/Users/|/home/", re.I)


def strings(value, path="manifest"):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from strings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from strings(child, f"{path}[{index}]")


def check_commerce(text, path):
    if COMMERCIAL.search(text):
        raise ValueError(f"commercial wording in {path}")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def object_without_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def validate_manifest(data, name):
    keys = {"name", "version", "description", "author", "repository", "license", "keywords"}
    keys |= {"$schema"} if name == "plugin.json" else {"homepage", "mcpServers", "interface", "extensions"}
    require(isinstance(data, dict) and set(data) == keys, f"unexpected manifest fields in {name}")
    for field, value in strings(data):
        require(not SECRETS.search(value), f"secret or private path in {name}:{field}")
        check_commerce(value, f"{name}:{field}")
    for field in ("name", "version", "description", "repository", "license"):
        require(isinstance(data[field], str) and bool(data[field].strip()), f"invalid {field} in {name}")
    require(data["name"] == "decktype-connector" and re.fullmatch(r"\d+\.\d+\.\d+", data["version"]),
            f"invalid identity or version in {name}")
    require(data["repository"] == "https://github.com/Tontoon7/decktype-agent" and data["license"] == "MIT",
            "unexpected repository or license")
    require(isinstance(data["author"], dict) and bool(str(data["author"].get("name", "")).strip()), "author name required")
    require(isinstance(data["keywords"], list) and all(isinstance(v, str) for v in data["keywords"]), "invalid keywords")
    if name == "plugin.json":
        require(data["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", "unexpected schema reference")
        return
    require(data["homepage"] == "https://decktype.com/en/connectors", "unexpected documentation URL")
    require(data["mcpServers"] == "./.mcp.json", "unexpected MCP configuration path")
    interface = data["interface"]
    text_keys = {"displayName", "shortDescription", "longDescription", "developerName", "category",
                 "websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL", "brandColor",
                 "composerIcon", "composerIconDark", "logo", "logoDark"}
    require(isinstance(interface, dict) and set(interface) == text_keys | {"capabilities", "defaultPrompt"},
            "unexpected interface fields")
    require(all(isinstance(interface[k], str) and interface[k].strip() for k in text_keys), "invalid interface text")
    require(interface["brandColor"] == "#191713", "unexpected brand color")
    require(len(interface["displayName"]) <= 30 and len(interface["shortDescription"]) <= 30, "name or subtitle over 30 characters")
    require(isinstance(interface["capabilities"], list) and all(isinstance(v, str) and 0 < len(v) <= 120 for v in interface["capabilities"]),
            "invalid capabilities")
    require(all(interface[k] in {"./assets/icon.png", "./assets/icon-dark.png"} for k in ("composerIcon", "composerIconDark", "logo", "logoDark")),
            "unexpected icon path")
    require(isinstance(interface["defaultPrompt"], list) and 1 <= len(interface["defaultPrompt"]) <= 3
            and all(isinstance(v, str) and 0 < len(v.strip()) <= 128 for v in interface["defaultPrompt"]), "invalid prompts")
    for field, suffix in (("websiteURL", ""), ("supportURL", "/en/contact"), ("privacyPolicyURL", "/en/privacy"),
                          ("termsOfServiceURL", "/en/terms")):
        require(interface[field] == "https://decktype.com" + suffix, f"unexpected {field}")
    review = data["extensions"]["com.openai"]["review"]
    cases = review["test_cases"]
    require(len(cases["positive"]) == 5 and len(cases["negative"]) == 3, "five positive and three negative cases required")
    require(all(case.get("tools_triggered") and case.get("expected_behavior") for case in cases["positive"]), "incomplete positive case")
    require(review["demo_recording_url"].startswith("https://") and review["commerce"] is False, "unexpected review details")


def validate(source, document):
    require(not source.is_symlink(), "plugin root must not be a symlink")
    paths = list(source.rglob("*"))
    allowed_dirs = {"assets", ".codex-plugin"}
    for path in paths:
        relative = path.relative_to(source).as_posix()
        require(not path.is_symlink(), f"symlink forbidden: {relative}")
        require(path.is_file() or (path.is_dir() and relative in allowed_dirs), f"unexpected path: {relative}")
        require(not path.is_file() or not path.stat().st_mode & 0o111, f"executable forbidden: {relative}")
    require(sorted(p.relative_to(source).as_posix() for p in paths if p.is_file()) == list(FILES),
            "unexpected or missing plugin files")
    contents = {name: (source / name).read_bytes() for name in FILES}
    for name, content in contents.items():
        require(not SECRETS.search(content.decode("utf-8", errors="replace")), f"secret or private path in {name}")
    for name, expected in MCP_CONFIGS.items():
        config = json.loads(contents[name], object_pairs_hook=object_without_duplicates)
        require(config == expected, f"{name}: expected one remote server without headers or credentials")
    for name in ("plugin.json", ".codex-plugin/plugin.json"):
        data = json.loads(contents[name], object_pairs_hook=object_without_duplicates)
        validate_manifest(data, name)
    root_manifest = json.loads(contents["plugin.json"])
    codex_manifest = json.loads(contents[".codex-plugin/plugin.json"])
    for field in ("name", "version", "description", "repository", "license", "keywords"):
        require(root_manifest[field] == codex_manifest[field], f"manifest mismatch: {field}")
    for name in ("assets/icon.png", "assets/icon-dark.png"):
        require(contents[name][:8] == b"\x89PNG\r\n\x1a\n" and contents[name][16:24] == b"\x00\x00\x02\x00" * 2,
                f"expected 512px PNG: {name}")
    require("Commerce: none" in contents["SUBMISSION-NOTES.md"].decode(), "missing commerce declaration")
    listing = document.read_text(encoding="utf-8").split("## Directory listing\n", 1)
    require(len(listing) == 2, "missing Directory listing section")
    check_commerce(listing[1].split("\n## ", 1)[0], "Directory listing")
    return contents


def build(source, document, output):
    require(not output.is_symlink() and not output.exists(), "output already exists")
    require(not output.resolve().is_relative_to(source.resolve()), "output must be outside plugin source")
    contents = validate(source, document)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, content in contents.items():
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(entry, content)
    with output.open("xb") as destination:
        destination.write(buffer.getvalue())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        build(ROOT / "plugins/decktype-connector", ROOT / "docs/openai-submission.md", args.output)
    except (ValueError, OSError, TypeError) as error:
        parser.exit(1, f"Submission build refused: {error}\n")
    print(f"Built {args.output}")


if __name__ == "__main__":
    main()
