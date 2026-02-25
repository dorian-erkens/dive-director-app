# PRD – {{TITLE}}

> **Issue source :** #{{ISSUE_NUMBER}}
> **Date :** {{DATE}}
> **Statut :** Draft

---

## 1. Idea – Description de l'amelioration

- **Idea title**
  {{TITLE}}

- **Context – Pourquoi maintenant ?**
  {{CONTEXT}}

- **Problem statement**
  > {{PROBLEM_STATEMENT}}

---

## 2. Goal – Objectif structure

> **Goal**
> {{GOAL}}

- **Metrique cle**
  - Nom :
  - Valeur actuelle :
  - Cible visee :

- **Impact attendu** : {{IMPACT_DIRECTION}}

---

## 3. ICE Score + Confidence Meter

- **Impact (I)** : {{IMPACT_SCORE}} / 10
- **Ease (E)** : {{EASE_SCORE}} / 10
- **Confidence (C)** : {{CONFIDENCE_SCORE}} / 10

### Evidence collectee

- [ ] Self-conviction / intuition interne (+0.1)
- [ ] Avis d'autres membres de l'equipe / stakeholders (+0.1)
- [ ] Trends marche / benchmarks sectoriels (+0.1)
- [ ] Feedback client anecdotique (support, conversations) (+0.4)
- [ ] Estimations / plans de faisabilite (+0.4)
- [ ] Survey quantitatif / market research (+1.0)
- [ ] Analytics / logs / funnel data (+1.0)
- [ ] Interviews de validation utilisateur (+2.5)
- [ ] User study avec prototype (+2.5-3.0)
- [ ] MVP / feature live + behavioral metrics (+3.0)

**Score Confidence (C) = :** `{{CONFIDENCE_SCORE}}`

| Score | Niveau | Action |
|-------|--------|--------|
| 0.1-0.5 | Very Low | Valider avant prototypage |
| 0.5-1.5 | Low | Discovery legere |
| 1.5-3.0 | Medium | Prototype + test interne |
| 3.0-6.0 | High | Passer en delivery |
| 6.0-10 | Very High | Priorite forte |

**ICE = (I x C x E) / 10 = {{ICE_SCORE}}**

---

## 4. Hypotheses a tester (Discovery)

### H1
- **Hypothese :**
  > {{H1}}
- **Test :** {{H1_TEST}}
- **Critere de validation :** {{H1_CRITERIA}}
- **Criticite :** Must validate

### H2
- **Hypothese :**
  > {{H2}}
- **Test :** {{H2_TEST}}
- **Critere de validation :** {{H2_CRITERIA}}
- **Criticite :** Nice to have

---

## 5. Prototype Scope

### 5.1 User flows critiques

**Flow 1 : {{FLOW1_NAME}}**
- Trigger : {{FLOW1_TRIGGER}}
- Etapes :
  1. L'utilisateur {{STEP1}}
  2. Le systeme {{STEP2}}
  3. {{STEP3}}
- Outcome : {{FLOW1_OUTCOME}}

### 5.2 Logique fonctionnelle

- Si {{CONDITION1}}, alors {{BEHAVIOR1}}
- Dans l'etat {{STATE1}}, l'utilisateur peut / ne peut pas {{ACTION1}}

### 5.3 Donnees mockees

- Types de donnees : {{DATA_TYPES}}
- Attributs : {{DATA_ATTRIBUTES}}
- Exemples : {{DATA_EXAMPLES}}

---

## 6. Success criteria

### Qualitatif
- [ ] Les testeurs comprennent la fonctionnalite sans explication detaillee
- [ ] Le flow principal est complete sans blocage majeur
- [ ] Retour majoritairement positif sur {{KEY_DIMENSION}}

### Quantitatif
- [ ] >= {{N}} / {{TOTAL}} testeurs completent {{TASK}} sans aide
- [ ] Score satisfaction >= {{SCORE}} / 5

### Decision post-test
- Si criteres atteints → passe en delivery
- Si criteres non atteints → adapter ou abandonner

---

## 7. Notes pour Claude Code

- **Fidelite** : Prototype fonctionnel minimal, testable en local
- **Priorite** : flows critiques + logique metier + donnees mockees
- **Assumptions** marquees explicitement dans le document
