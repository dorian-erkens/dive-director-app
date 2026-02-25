# Dive Director App

> **[English below](#english)**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2019-61DAFB)](https://react.dev/)
[![Claude API](https://img.shields.io/badge/AI-Claude%20API-blueviolet)](https://docs.anthropic.com/)
[![SHOM](https://img.shields.io/badge/Data-SHOM%204796%2B%20%C3%A9paves-0077b6)](https://data.shom.fr/)
[![PRD Workflow](https://img.shields.io/badge/Product-GIST%20%2F%20ICE%20PRDs-orange)](docs/prd/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Web app de planification de plongee pour **Directeur de Plongee (DP)**, propulsee par l'IA. Carte des epaves en temps reel, chatbot avec tool use, et panel Inspector qui montre ce que l'IA fait sous le capot.

Concue pour [Caen Ouistreham Plongee (COP)](https://caen-ouistreham-plongee.org/), adaptable a tout club de plongee francais.

---

## Demo

**Layout 3 colonnes : Chat | Carte | Inspector**

- **Chat** (gauche) — Posez des questions en langage naturel. Claude cherche dans la base SHOM, calcule des distances, et repond avec les donnees reelles.
- **Carte** (centre) — 4 796+ epaves SHOM affichees sur Leaflet. Chargement automatique quand vous bougez la carte.
- **Inspector** (droite) — Chaque appel IA, requete SHOM et decision s'affiche en temps reel. Effet "glass box" sur l'IA.

## Architecture

```
┌──────────────┐     WebSocket      ┌──────────────────┐
│   React UI   │◄──────────────────►│   FastAPI (Py)   │
│  Vite + TS   │     REST API       │                  │
│  Tailwind    │◄──────────────────►│  Claude API      │
│  Leaflet     │                    │  SHOM WFS        │
│              │     Inspector WS   │  Inspector Bus   │
│  Chat │ Map  │◄──────────────────►│                  │
│   Inspector  │                    │                  │
└──────────────┘                    └──────────────────┘
```

| Couche | Stack |
|--------|-------|
| **Frontend** | React 19, Vite, TypeScript, Tailwind CSS, Leaflet, Lucide |
| **Backend** | FastAPI, Uvicorn, Pydantic, httpx |
| **IA** | Claude API (Anthropic SDK) avec streaming + tool use |
| **Donnees** | SHOM WFS API (4 796+ epaves, live) |
| **Product** | GIST / ICE framework, PRDs auto-generes via GitHub Actions |

## Fonctionnalites

### Carte des epaves
- 4 796+ epaves de la base SHOM sur toutes les eaux francaises
- Chargement dynamique en fonction de la zone visible
- Popup avec brassiage, circonstances du naufrage, type de navire
- Recherche par nom, par zone, par proximite

### Chat IA
- Chatbot avec streaming (reponse token par token)
- Tool use : Claude appelle automatiquement l'API SHOM quand necessaire
- Historique de conversation persiste dans la session
- Contexte plongee : profondeurs, distances en NM, positions GPS

### Inspector Panel
- Chaque action de l'IA est tracee en temps reel via WebSocket
- Types d'events : appel agent, appel outil, resultat, erreur
- Timestamped, colore par type, avec metadata
- Dimension pedagogique : montrer comment fonctionne une app IA agentique

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Cle API Anthropic ([console.anthropic.com](https://console.anthropic.com/))

### Installation

```bash
git clone https://github.com/dorian-erkens/dive-director-app.git
cd dive-director-app

# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Ajouter votre ANTHROPIC_API_KEY
cd ..

# Frontend
cd frontend
npm install
cd ..
```

### Lancement

```bash
# Terminal 1 — Backend
cd backend && source .venv/bin/activate
uvicorn app.main:app --port 8000 --reload

# Terminal 2 — Frontend
cd frontend
npx vite --port 5173
```

Ouvrir **http://localhost:5173**

## Product Workflow

Ce projet utilise un workflow Product automatise :

1. **Creer un insight** → issue GitHub avec le template "Insight"
2. **PRD auto-genere** → GitHub Action appelle Claude API pour generer un PRD complet
3. **PR creee** → le draft PRD arrive dans `docs/prd/` via Pull Request
4. **Review & iterate** → challenger les hypotheses, ajuster les scores ICE
5. **Merge** → le PRD valide passe en backlog de prototypage

Framework : **GIST** (Goals, Ideas, Steps, Tasks) + **ICE Scoring** (Impact x Confidence x Ease) avec le **Confidence Meter** d'Itamar Gilad.

[Voir les PRDs](docs/prd/)

## Structure du projet

```
dive-director-app/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI + CORS + dotenv
│   │   ├── services/
│   │   │   ├── shom.py             # Client SHOM WFS (Python)
│   │   │   ├── claude.py           # Orchestrateur Claude API + tools
│   │   │   └── inspector.py        # Event bus pub/sub
│   │   ├── models/                 # Pydantic models
│   │   └── routers/                # REST + WebSocket endpoints
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Map/WreckMap.tsx    # Leaflet + markers SHOM
│   │   │   ├── Chat/ChatPanel.tsx  # Chat UX avec streaming
│   │   │   └── Inspector/         # Panel events IA temps reel
│   │   ├── hooks/                  # useChat, useWrecks
│   │   └── App.tsx                 # Layout 3 colonnes
│   └── vite.config.ts              # Proxy API + WS
├── docs/prd/                       # PRDs auto-generes
├── .github/
│   ├── ISSUE_TEMPLATE/insight.yml  # Template issue "Insight"
│   ├── workflows/generate-prd.yml  # GitHub Action PRD
│   ├── scripts/generate_prd.py     # Script generation Claude
│   └── templates/prd-template.md   # Template PRD (GIST/ICE)
└── README.md
```

## Roadmap

Voir les [issues ouvertes](https://github.com/dorian-erkens/dive-director-app/issues) pour la liste complete.

| Priorite | Feature |
|:---:|---|
| 1 | [Port de depart configurable](https://github.com/dorian-erkens/dive-director-app/issues/1) |
| 2 | [Agent port-access avec abris](https://github.com/dorian-erkens/dive-director-app/issues/2) |
| 3 | [Carte interactive avancee](https://github.com/dorian-erkens/dive-director-app/issues/3) |
| 4 | [Meteo temps reel via API](https://github.com/dorian-erkens/dive-director-app/issues/8) |
| 5 | [Inspector pedagogique](https://github.com/dorian-erkens/dive-director-app/issues/6) |

## Projets lies

- [dive-director](https://github.com/dorian-erkens/dive-director) — Version CLI (Claude Code agents)
- [mcp-shom-wrecks](https://github.com/dorian-erkens/mcp-shom-wrecks) — MCP server pour la base SHOM

## Licence

MIT

## Auteur

Dorian Erkens — [Caen Ouistreham Plongee](https://caen-ouistreham-plongee.org/)

---

<a id="english"></a>

## English

**Dive Director App** is an AI-powered web application for scuba **Dive Directors**, built with FastAPI (Python) and React.

### Key features
- **Wreck Map** — 4,796+ SHOM wrecks on an interactive Leaflet map
- **AI Chat** — Claude API with streaming and tool use (searches the SHOM database in real-time)
- **Inspector Panel** — real-time visibility into every AI action, tool call, and decision (pedagogical "glass box" on AI)

### Product Workflow
Every feature idea goes through an automated PRD pipeline: GitHub Issue (insight) → Claude generates a GIST/ICE PRD → PR for review → merge to backlog.

### Tech stack
FastAPI, React 19, TypeScript, Tailwind, Leaflet, Claude API (Anthropic), SHOM WFS, WebSocket streaming.

### Related projects
- [dive-director](https://github.com/dorian-erkens/dive-director) — CLI version with 7 Claude Code agents
- [mcp-shom-wrecks](https://github.com/dorian-erkens/mcp-shom-wrecks) — MCP server for SHOM wreck database (4,796+ wrecks)
