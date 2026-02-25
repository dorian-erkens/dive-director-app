# PRD – Port de départ configurable

> **Issue source :** #{{ISSUE_NUMBER}}
> **Date :** 2024-01-15
> **Statut :** Draft

---

## 1. Idea – Description de l'amélioration

- **Idea title**
  Port de départ configurable pour les directeurs de plongée

- **Context – Pourquoi maintenant ?**
  L'outil est actuellement limité au port de Ouistreham, ce qui constitue le principal frein à l'adoption par les autres clubs normands. 3 clubs ont déjà manifesté leur intérêt et l'issue #1 du repository porte sur ce sujet.

- **Problem statement**
  > Les directeurs de plongée des clubs normands (Courseulles, Port-en-Bessin, Grandcamp, Dives) ne peuvent pas utiliser l'outil car toutes les données sont codées en dur pour Ouistreham, limitant drastiquement l'adoption de la solution.

---

## 2. Goal – Objectif structuré

> **Goal**
> Permettre aux DP de sélectionner leur port de départ pour que l'ensemble du workflow de planification (marées, météo, transit, épaves) s'adapte automatiquement à leur localisation.

- **Métrique clé**
  - Nom : Nombre de clubs actifs utilisant l'outil
  - Valeur actuelle : **[Assumption]** 1 club (Ouistreham)
  - Cible visée : 5 clubs normands dans les 3 mois

- **Impact attendu** : Multiplication par 5 du nombre de clubs utilisateurs

---

## 3. ICE Score + Confidence Meter

- **Impact (I)** : 9 / 10
- **Ease (E)** : 7 / 10
- **Confidence (C)** : 2.0 / 10

### Evidence collectée

- [x] Self-conviction / intuition interne (+0.1)
- [ ] Avis d'autres membres de l'équipe / stakeholders (+0.1)
- [ ] Trends marché / benchmarks sectoriels (+0.1)
- [x] Feedback client anecdotique (support, conversations) (+0.4)
- [x] Estimations / plans de faisabilité (+0.4)
- [ ] Survey quantitatif / market research (+1.0)
- [ ] Analytics / logs / funnel data (+1.0)
- [ ] Interviews de validation utilisateur (+2.5)
- [ ] User study avec prototype (+2.5-3.0)
- [ ] MVP / feature live + behavioral metrics (+3.0)

**Score Confidence (C) = :** `2.0`

| Score | Niveau | Action |
|-------|--------|--------|
| 0.1-0.5 | Very Low | Valider avant prototypage |
| 0.5-1.5 | Low | Discovery légère |
| 1.5-3.0 | Medium | Prototype + test interne |
| 3.0-6.0 | High | Passer en delivery |
| 6.0-10 | Very High | Priorité forte |

**ICE = (I x C x E) / 10 = 12.6**

---

## 4. Hypothèses à tester (Discovery)

### H1
- **Hypothèse :**
  > Les DP des autres ports normands adoptront l'outil s'ils peuvent configurer leur port de départ et que les données s'adaptent automatiquement.
- **Test :** Prototype avec 2-3 ports configurables + test avec DP de Courseulles et Port-en-Bessin
- **Critère de validation :** 2/3 des DP testeurs utilisent le prototype pour planifier une sortie complète
- **Criticité :** Must validate

### H2
- **Hypothèse :**
  > **[Assumption]** Les APIs météo et marées fournissent des données fiables pour tous les ports normands majeurs.
- **Test :** Vérification technique des endpoints API pour 4-5 ports cibles
- **Critère de validation :** Données disponibles et cohérentes pour 80% des ports visés
- **Criticité :** Nice to have

---

## 5. Prototype Scope

### 5.1 User flows critiques

**Flow 1 : Sélection et configuration du port de départ**
- Trigger : Premier lancement de l'outil ou changement de configuration
- Étapes :
  1. L'utilisateur sélectionne son port dans une liste déroulante (Ouistreham, Courseulles, Port-en-Bessin, Grandcamp, Dives)
  2. Le système charge automatiquement les coordonnées, données de marée et stations météo associées
  3. L'interface s'adapte avec les bonnes références géographiques et temporelles
- Outcome : Toutes les fonctionnalités (météo, marées, calcul d'épaves proches) sont recalibrées sur le nouveau port

### 5.2 Logique fonctionnelle

- Si port != Ouistreham, alors recalcul des distances et trajets vers les sites de plongée
- Dans l'état "port configuré", l'utilisateur peut planifier des sorties avec données météo/marée locales
- Si changement de port en cours de session, alors réinitialisation des calculs en cours

### 5.3 Données mockées

- Types de données : Ports normands avec coordonnées GPS, stations météo associées, coefficients de marée
- Attributs : nom_port, lat, lng, station_meteo_id, station_maree_id, sites_plongee_proximite[]
- Exemples : Courseulles (49.3336, -0.4594), Port-en-Bessin (49.3486, -0.7553), Grandcamp (49.3889, -1.0394)

---

## 6. Success criteria

### Qualitatif
- [ ] Les testeurs comprennent la fonctionnalité sans explication détaillée
- [ ] Le flow principal est complété sans blocage majeur
- [ ] Retour majoritairement positif sur l'utilité et la précision des données adaptées

### Quantitatif
- [ ] >= 2 / 3 testeurs completent une planification de sortie sans aide
- [ ] Score satisfaction >= 4 / 5

### Decision post-test
- Si critères atteints → passe en delivery
- Si critères non atteints → adapter ou abandonner

---

## 7. Notes pour Claude Code

- **Fidélité** : Prototype fonctionnel minimal, testable en local
- **Priorité** : flows critiques + logique métier + données mockées
- **Assumptions** marquées explicitement dans le document