"""Tests de la configuration du paquet (TP 4), lancés dans le dépôt, sans installer la roue.

Ils lisent pyproject.toml et les sources : ils attrapent tôt une erreur de configuration
(modèle oublié, commande mal déclarée, version absente). Le paquet installé, lui, est testé
par tests/test_paquet.py, que lance scripts/verifier_livrable.py.
"""
import re
import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
PAQUET = RACINE / "src" / "sentiment_app"


def lire_pyproject() -> dict:
    return tomllib.loads((RACINE / "pyproject.toml").read_text(encoding="utf-8"))


def test_metadonnees_du_paquet():
    """Un paquet nommé, avec une version écrite en clair et sa commande."""
    projet = lire_pyproject()["project"]
    assert projet["name"] == "sentiment-app"
    assert re.fullmatch(r"\d+\.\d+\.\d+", projet["version"])
    assert projet["scripts"]["sentiment"] == "sentiment_app.cli:main"


def test_scikit_learn_est_fige():
    """Le modèle sérialisé ne se relit qu'avec la version de scikit-learn qui l'a produit."""
    dependances = lire_pyproject()["project"]["dependencies"]
    assert any(d.replace(" ", "").startswith("scikit-learn==1.5") for d in dependances), dependances


def test_le_modele_est_declare_dans_la_roue():
    """Sans package-data, la roue se construit sans erreur, mais sans le modèle."""
    setuptools = lire_pyproject()["tool"]["setuptools"]
    assert setuptools["packages"]["find"]["where"] == ["src"]
    assert "modele/*.joblib" in setuptools["package-data"]["sentiment_app"]


def test_une_seule_source_pour_la_version():
    """__init__.py lit la version dans les métadonnées : aucun numéro écrit en dur dans le code."""
    init = (PAQUET / "__init__.py").read_text(encoding="utf-8")
    assert 'version("sentiment-app")' in init
    assert not re.search(r"__version__\s*=\s*[\"']\d", init)


def test_le_journal_decrit_la_version():
    version = lire_pyproject()["project"]["version"]
    assert f"[{version}]" in (RACINE / "CHANGELOG.md").read_text(encoding="utf-8")


def test_le_modele_n_est_pas_commite():
    """Le modèle est copié dans le paquet au moment de construire, jamais versionné."""
    assert "src/sentiment_app/modele/*.joblib" in (RACINE / ".gitignore").read_text(encoding="utf-8")
