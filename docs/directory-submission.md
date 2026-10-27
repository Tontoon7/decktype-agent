# Plugin directory submission texts

Ready-to-paste texts for the Claude Code and Codex plugin directories, in English and French. Prices and platforms match [decktype.com/en/pricing](https://decktype.com/en/pricing) and [decktype.com/en/download](https://decktype.com/en/download); the website remains the reference if they change.

## Before submitting

- Proposed plugin version: `1.1.0`, identical in the four manifest version fields. The matching `v1.1.0` version tag is created by the maintainer once the release is approved, never by these texts.
- Check each directory's current submission requirements (field names, length limits, screenshots, review policy) before pasting. The lengths below fit the usual limits: tagline under 80 characters, short description under 200 characters.
- Screenshot: [plugins/decktype/examples/slide-01.png](../plugins/decktype/examples/slide-01.png) and the three other example slides.
- Install from GitHub once more after the release is merged, with the commands below.

## English

**Name:** Decktype

**Tagline:** Build editable presentations with your agent, then finish them in Decktype.

**Short description:** Claude Code or Codex creates and revises native .deck presentations, renders every slide for review, and exports a PDF or a PowerPoint file. For Apple silicon Macs.

**Long description:**

Decktype Agent connects Claude Code and Codex to Decktype, the native presentation editor for Mac. The agent agrees on the audience and the decision with you, proposes an outline, then fills structured Decktype templates instead of drawing flattened slides. It validates, lints, and renders every changed slide, and reviews the images before delivering.

The result is an editable `.deck` file that you keep refining by hand in Decktype. When the agent revises the deck later, your manual layout changes are preserved. The plugin can also import an existing PowerPoint file, export a PDF on every plan, and export a Keynote-compatible PowerPoint file on the Pro and Autonomous plans.

**Category:** Productivity

**Keywords:** presentations, slides, powerpoint, pptx, pdf, keynote, decktype, macos

**Requirements:**

- An Apple silicon Mac (M1 or newer) running macOS 11 Big Sur or newer.
- The Decktype app, free to download, with **Connect an agent** run once.
- Claude Code or Codex.

**Plans and pricing:**

- Free, €0: editable `.deck` files, PowerPoint import, PDF and PNG export.
- Pro, €12 / month incl. VAT: adds PowerPoint export, cloud, sharing, and version history.
- Autonomous, €29 / month incl. VAT: adds the assistant built into the Decktype app.

The plugin itself is free and open source (MIT).

**Data and privacy:** the plugin adds no hooks, no background service, no MCP server, and no bundled executable. It runs the local `deck` CLI installed by Decktype on the files you place in the agent's scope; your `.deck` files stay on your disk. Your agent follows its own provider's terms.

**Example prompts:**

- Create an editable 7-slide presentation for a product review from brief.md, and show me the outline first.
- Revise customer-review.deck with the priorities in notes.md and keep my manual layout changes.
- Render quarterly-review.deck, check every slide, then export it to PDF.

**Install in Claude Code:**

```sh
claude plugin marketplace add Tontoon7/decktype-agent
claude plugin install decktype@decktype-agent
```

**Install in Codex:**

```sh
codex plugin marketplace add Tontoon7/decktype-agent
codex plugin add decktype@decktype-agent
```

**Links:**

- Repository: https://github.com/Tontoon7/decktype-agent
- Homepage: https://decktype.com/en/agents
- Download: https://decktype.com/en/download
- Pricing: https://decktype.com/en/pricing
- Privacy policy: https://decktype.com/en/privacy
- Terms of service: https://decktype.com/en/terms

## Français

**Nom :** Decktype

**Accroche :** Votre agent construit la présentation, vous la finissez dans Decktype.

**Description courte :** Claude Code ou Codex crée et révise des présentations .deck natives, rend chaque slide pour relecture et exporte un PDF ou un fichier PowerPoint. Pour Mac Apple silicon.

**Description longue :**

Decktype Agent relie Claude Code et Codex à Decktype, l'éditeur de présentations natif pour Mac. L'agent convient avec vous du public et de la décision attendue, propose un plan, puis remplit des templates Decktype structurés au lieu de dessiner des slides figées. Il valide, contrôle et rend chaque slide modifiée, et relit les images avant de livrer.

Le résultat est un fichier `.deck` modifiable, que vous continuez de retoucher à la main dans Decktype. Quand l'agent révise ensuite la présentation, vos retouches de mise en page sont conservées. Le plugin sait aussi importer un fichier PowerPoint existant, exporter un PDF avec toutes les offres et exporter un fichier PowerPoint compatible Keynote avec les offres Pro et Autonomous.

**Catégorie :** Productivité (Productivity)

**Mots-clés :** présentations, slides, powerpoint, pptx, pdf, keynote, decktype, macos

**Prérequis :**

- Un Mac Apple silicon (M1 ou plus récent) sous macOS 11 Big Sur ou plus récent.
- L'application Decktype, gratuite, avec **Connect an agent** lancé une fois.
- Claude Code ou Codex.

**Offres et prix :**

- Gratuit, 0 € : fichiers `.deck` modifiables, import PowerPoint, export PDF et PNG.
- Pro, 12 € par mois TTC : ajoute l'export PowerPoint, le cloud, le partage et l'historique de versions.
- Autonomous, 29 € par mois TTC : ajoute l'assistant intégré à l'application Decktype.

Le plugin lui-même est gratuit et open source (MIT).

**Données et confidentialité :** le plugin n'ajoute ni hook, ni service en arrière-plan, ni serveur MCP, ni exécutable embarqué. Il lance la CLI `deck` locale installée par Decktype sur les fichiers que vous placez dans le périmètre de l'agent ; vos fichiers `.deck` restent sur votre disque. Votre agent suit les conditions de son propre fournisseur.

**Exemples d'invites :**

- Crée une présentation modifiable de 7 slides pour une revue produit à partir de brief.md, et montre-moi d'abord le plan.
- Révise revue-client.deck avec les priorités de notes.md en gardant mes retouches de mise en page.
- Rends revue-trimestrielle.deck, vérifie chaque slide, puis exporte-le en PDF.

**Installation dans Claude Code :**

```sh
claude plugin marketplace add Tontoon7/decktype-agent
claude plugin install decktype@decktype-agent
```

**Installation dans Codex :**

```sh
codex plugin marketplace add Tontoon7/decktype-agent
codex plugin add decktype@decktype-agent
```

**Liens :**

- Dépôt : https://github.com/Tontoon7/decktype-agent
- Page d'accueil : https://decktype.com/fr/agents
- Téléchargement : https://decktype.com/fr/telecharger
- Tarifs : https://decktype.com/fr/tarifs
- Politique de confidentialité : https://decktype.com/fr/confidentialite (EN : https://decktype.com/en/privacy)
- Conditions d'utilisation : https://decktype.com/fr/conditions (EN : https://decktype.com/en/terms)
