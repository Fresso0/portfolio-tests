# Tests automatisés — Portfolio fresnel.host

[![Tests automatisés du portfolio](https://github.com/Fresso0/portfolio-tests/actions/workflows/tests.yml/badge.svg)](https://github.com/Fresso0/portfolio-tests/actions/workflows/tests.yml)

Suite de tests automatisés de mon portfolio [fresnel.host](https://fresnel.host),
écrite avec **Selenium (Python/pytest)** et **Robot Framework**, exécutée
automatiquement par **GitHub Actions** à chaque push et chaque nuit.

## Stratégie de test

| Périmètre | Scénarios | Outil |
|---|---|---|
| Disponibilité | Chargement de la page, titre, hero | Selenium + Robot |
| Navigation | Menu (Projets, Expérience, Outils), lien CV (PDF, HTTP 200) | Selenium |
| Intégrité | Aucun lien externe cassé (4xx/5xx) | Selenium + requests |
| Formulaire de contact | Rejet email invalide, rejet message < 7 mots | Selenium + Robot |
| Responsive | Affichage en largeur mobile (375 px) | Selenium |

Le site testé n'est volontairement **pas** dans ce dépôt : les tests s'exécutent
contre l'environnement de production, comme une supervision de non-régression.

## Lancer en local

```bash
pip install -r requirements.txt

# Selenium
pytest tests_selenium/ -v

# Robot Framework (rapports HTML dans ./resultats)
robot --outputdir resultats tests_robot/
```

## CI/CD

Le workflow [.github/workflows/tests.yml](.github/workflows/tests.yml) :
- se déclenche à chaque push, chaque pull request, et **tous les jours à 6h** (cron) ;
- exécute les deux suites en parallèle sur Chrome headless ;
- publie les rapports (JUnit XML + rapports HTML Robot Framework) en artefacts.

## Auteur

Fresnel Dossou — [fresnel.host](https://fresnel.host) · dossoufres@gmail.com
