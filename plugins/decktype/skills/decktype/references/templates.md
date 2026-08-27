# Standard template guide

Use this guide to choose a layout, then query the installed CLI for the current schema:

```sh
deck templates list --json
deck templates show standard/<template-id> --json
```

The CLI output wins if it differs from this reference. Optional slots should normally be omitted rather than filled with empty strings.

## Selection map

| Template | Use it for | Required slots | Content budget |
| --- | --- | --- | --- |
| `standard/titre` | Opening slide | `titre` | Title: about 8 words, 2 lines |
| `standard/statement` | One thesis or transition | `phrase` | One sentence, about 15 words |
| `standard/contenu` | Argument, observation, recommendation | `titre`, `points` | 1 to 5 short points |
| `standard/cartes` | Comparable pillars or options | `titre`, `cartes` | 2 to 4 cards |
| `standard/process` | Ordered workflow or timeline | `titre`, `etapes` | 2 to 6 steps |
| `standard/kpi` | Defensible metrics | `chiffres` | 2 to 4 values; never invent data |
| `standard/graphique` | One numeric series across categories | `titre`, `donnees` | 1 to 12 rows; never invent data |
| `standard/tableau` | Structured comparison, budget, plan | `titre`, `lignes` | 2 to 10 rows; never invent data |
| `standard/citation` | A verified quotation | `auteur`, `citation` | About 20 words |
| `standard/cloture` | Decision and next steps | `message`, `etapes` | 1 to 3 next actions |

Vary layouts when the content permits it. A useful six-slide rhythm is title, thesis, argument, options, process, and close.

## Binding shapes

### Title

```json
{
  "pack": "standard",
  "id": "titre",
  "slots": {
    "eyebrow": "Strategy review",
    "titre": "Turn the brief into a decision",
    "sous-titre": "A short, editable presentation"
  }
}
```

### Statement

```json
{
  "pack": "standard",
  "id": "statement",
  "slots": {
    "eyebrow": "Thesis",
    "phrase": "The agent builds structure. You keep editorial control."
  }
}
```

### Content

```json
{
  "pack": "standard",
  "id": "contenu",
  "slots": {
    "eyebrow": "Recommendation",
    "titre": "Keep one message per slide",
    "corps": "Structure comes before decoration.",
    "points": [
      {"texte": "Name the decision"},
      {"texte": "Select a fitting template"},
      {"texte": "Review the rendered slide"}
    ]
  }
}
```

### Cards

```json
{
  "pack": "standard",
  "id": "cartes",
  "slots": {
    "eyebrow": "Options",
    "titre": "Choose the right level of detail",
    "cartes": [
      {"label": "Concise", "detail": "One claim and its proof."},
      {"label": "Detailed", "detail": "Context plus the next decision."}
    ]
  }
}
```

### Process

```json
{
  "pack": "standard",
  "id": "process",
  "slots": {
    "eyebrow": "Workflow",
    "titre": "A deck both sides can change",
    "etapes": [
      {"numero": "01", "label": "Brief", "detail": "Agree on the decision."},
      {"numero": "02", "label": "Build", "detail": "Fill structured slots."},
      {"numero": "03", "label": "Review", "detail": "Inspect every render."}
    ]
  }
}
```

### KPI

```json
{
  "pack": "standard",
  "id": "kpi",
  "slots": {
    "eyebrow": "Observed results",
    "titre": "Use only sourced numbers",
    "chiffres": [
      {"valeur": "12", "label": "Interviews", "detail": "From the supplied research."},
      {"valeur": "3", "label": "Priorities", "detail": "Validated in the brief."}
    ]
  }
}
```

Do not reuse those example numbers unless they are true for the user's deck.

### Chart

```json
{
  "pack": "standard",
  "id": "graphique",
  "slots": {
    "eyebrow": "Trend",
    "titre": "Use values supplied by the user",
    "donnees": [
      {"categorie": "Q1", "valeur": "12"},
      {"categorie": "Q2", "valeur": "18"}
    ]
  }
}
```

### Table

```json
{
  "pack": "standard",
  "id": "tableau",
  "slots": {
    "eyebrow": "Plan",
    "titre": "A structured comparison",
    "lignes": [
      {"poste": "Discovery", "valeur": "Week 1", "detail": "Agree on scope."},
      {"poste": "Delivery", "valeur": "Week 2", "detail": "Review the result."}
    ]
  }
}
```

### Quote

```json
{
  "pack": "standard",
  "id": "citation",
  "slots": {
    "citation": "Use an exact, approved quotation.",
    "auteur": "Verified source",
    "role": "Optional context"
  }
}
```

### Close

```json
{
  "pack": "standard",
  "id": "cloture",
  "slots": {
    "eyebrow": "Next step",
    "message": "Open the deck and make it yours.",
    "etapes": [
      {"texte": "Edit any slide"},
      {"texte": "Export the approved version"}
    ],
    "contact": "decktype.com"
  }
}
```

