# Decktype connector

Commerce: none. The connector provides no commerce tools.
Authentication: OAuth with PKCE S256 and dynamic registration; scopes
`decks:read` and `decks:write`. Discovery:
https://api.decktype.com/.well-known/oauth-protected-resource/mcp

`mcp.json` declares dynamic registration through `extensions["com.openai"].auth`.
Brand assets: `assets/icon.png` and `assets/icon-dark.png` (512 × 512 PNG).
