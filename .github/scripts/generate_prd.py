"""Generate a PRD from a GitHub issue using Claude API."""

import os
import re
from pathlib import Path

import anthropic

ISSUE_NUMBER = os.environ["ISSUE_NUMBER"]
ISSUE_TITLE = os.environ["ISSUE_TITLE"]
ISSUE_BODY = os.environ["ISSUE_BODY"]

TEMPLATE = Path(".github/templates/prd-template.md").read_text()

PROMPT = f"""Tu es un Product Manager technique qui travaille en Vibe Coding avec le framework GIST (Goals, Ideas, Steps, Tasks) et l'ICE scoring enrichi par le Confidence Meter d'Itamar Gilad.

A partir de l'insight suivant (issue GitHub) :

**Titre :** {ISSUE_TITLE}

**Contenu :**
{ISSUE_BODY}

Genere un PRD complet en remplissant TOUTES les sections du template ci-dessous.
Remplace chaque placeholder {{...}} par du contenu pertinent et concret.

Regles :
- Sois concis et structure. Pas de prose inutile.
- Si une information manque dans l'issue, propose une hypothese raisonnable et marque-la comme **[Assumption]**.
- Le score ICE doit etre calcule rigoureusement a partir des evidence disponibles.
- Les hypotheses doivent etre testables avec un prototype minimal.
- Les user flows doivent etre specifiques au contexte Dive Director (planification de plongee).
- Ecris en francais.

Template a remplir :

{TEMPLATE}

IMPORTANT : renvoie UNIQUEMENT le markdown du PRD rempli, sans bloc de code, sans explication autour.
Le fichier doit commencer par "# PRD" et etre pret a sauvegarder tel quel.
"""


def main():
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": PROMPT}],
    )

    prd_content = response.content[0].text

    # Clean title for filename
    clean_title = ISSUE_TITLE.replace("[Insight] ", "")
    slug = re.sub(r"[^a-z0-9]+", "-", clean_title.lower()).strip("-")[:50]
    filename = f"{ISSUE_NUMBER}-{slug}.md"

    output_path = Path("docs/prd") / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prd_content)

    print(f"PRD generated: {output_path}")


if __name__ == "__main__":
    main()
