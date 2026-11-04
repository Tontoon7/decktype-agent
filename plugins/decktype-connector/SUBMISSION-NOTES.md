# Submission preparation — official validation pending

Commerce: none. The connector provides no commerce tools.
Authentication: OAuth with PKCE S256 and dynamic registration; scopes
`decks:read` and `decks:write`. Discovery:
https://api.decktype.com/.well-known/oauth-protected-resource/mcp

`mcp.json` declares dynamic registration through `extensions["com.openai"].auth`,
as in the official plugin reference. Do not use ChatGPT's published client
(CIMD): its `private_key_jwt` document is refused by the server.
The machine-readable no-commerce declaration is unverified and omitted, not guessed.
This archive is a preparation artifact, not an officially validated submission.
Brand assets: `assets/icon.png` and `assets/icon-dark.png` (512 × 512 PNG).
The official schema must confirm their manifest references and required sizes.
