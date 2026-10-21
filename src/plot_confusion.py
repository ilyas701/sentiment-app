#!/usr/bin/env python
"""Affiche et enregistre la matrice de confusion du modèle de sentiment.

Usage :
  python src/plot_confusion.py              # jeu de démonstration
  python src/plot_confusion.py --allocine   # jeu public Allociné
  python src/plot_confusion.py --normaliser # pourcentages par ligne

Produit : docs/images/matrice-confusion.png (et la version texte à l'écran)
"""
import argparse
import sys
from pathlib import Path

import joblib
import numpy as np
from numpy.typing import NDArray
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
from train import GRAINE, MODELE, charger  # noqa: E402

SORTIE = RACINE / "docs" / "images" / "matrice-confusion.png"
ETIQUETTES = ["negative", "positive"]


def matrice_texte(
    mc: NDArray[np.int64], etiquettes: list[str] = ETIQUETTES
) -> str:
    """Version texte, lisible dans un terminal et collable dans un compte rendu."""
    largeur = max(len(etiquette) for etiquette in etiquettes) + 2
    lignes = [" " * largeur + "".join(f"{etiquette:>{largeur}}" for etiquette in etiquettes)]
    for nom, ligne in zip(etiquettes, mc, strict=True):
        lignes.append(f"{nom:>{largeur}}" + "".join(f"{valeur:>{largeur}}" for valeur in ligne))
    return "\n".join(lignes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allocine", action="store_true", help="évaluer sur le jeu public")
    parser.add_argument("--normaliser", action="store_true", help="afficher des pourcentages par ligne")
    args = parser.parse_args()

    if not MODELE.exists():
        raise SystemExit("Modèle absent : lancez d'abord python src/train.py")
    pipeline = joblib.load(MODELE)

    df, source = charger(args.allocine)
    # Même découpage que l'entraînement : même graine, mêmes proportions.
    _, X_test, _, y_test = train_test_split(
        df["review"], df["label"], test_size=0.2, random_state=GRAINE, stratify=df["label"]
    )
    y_pred = pipeline.predict(X_test)

    mc = confusion_matrix(y_test, y_pred, labels=ETIQUETTES)
    print(f"Évaluation sur {len(X_test)} avis ({source})\n")
    print(classification_report(y_test, y_pred, digits=3, zero_division=0))
    print("Matrice de confusion (lignes = vérité, colonnes = prédiction)")
    print(matrice_texte(mc))
    _, faux_positifs, faux_negatifs, _ = mc.ravel()
    print(f"\n{faux_positifs} négatifs classés positifs (clients mécontents traités en retard)")
    print(f"{faux_negatifs} positifs classés négatifs (sans gravité)")
    print(f"{faux_positifs + faux_negatifs} erreurs sur {len(X_test)} avis")

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib absent : figure non produite. pip install matplotlib")
        return 0

    affichage = ConfusionMatrixDisplay.from_predictions(
        y_test,
        y_pred,
        labels=ETIQUETTES,
        display_labels=["négatif", "positif"],
        cmap="Blues",
        normalize="true" if args.normaliser else None,
        values_format=".2f" if args.normaliser else "d",
        colorbar=False,
    )
    titre = f"Matrice de confusion, {source}, {len(X_test)} avis de test"
    affichage.ax_.set_title(titre + ("\n(proportions par ligne)" if args.normaliser else ""))
    affichage.ax_.set_xlabel("Prédiction")
    affichage.ax_.set_ylabel("Vérité")
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    affichage.figure_.tight_layout()
    affichage.figure_.savefig(SORTIE, dpi=150)
    plt.close(affichage.figure_)
    print(f"\nFigure enregistrée : {SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())