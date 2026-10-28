import os
import sys
from functools import lru_cache
from pathlib import Path

import joblib

RACINE = Path(__file__).resolve().parents[1]


def chemin_modele() -> Path:
    """SENTIMENT_MODELE si elle est définie, sinon le modèle entraîné dans le dépôt."""
    return Path(os.environ.get("SENTIMENT_MODELE") or RACINE / "models" / "sentiment.joblib")


# Déclaration indispensable pour que l'API ou les tests qui importent MODELE fonctionnent
MODELE = chemin_modele()


@lru_cache(maxsize=1)
def charger_modele():
    """Chargé une seule fois par processus, pas à chaque appel."""
    modele_path = chemin_modele()
    if not modele_path.exists():
        raise FileNotFoundError(f"Modèle absent : {modele_path} : lancez python src/train.py")
    return joblib.load(modele_path)


def predict(texte: str) -> dict:
    """Renvoie {'label': 'POSITIVE'|'NEGATIVE'|'INDETERMINE', 'score': float}."""
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")
    pipeline = charger_modele()

    probs = pipeline.predict_proba([texte])[0]
    score = float(probs.max())

    if score < 0.60:
        etiquette = "INDETERMINE"
    else:
        etiquette = pipeline.classes_[probs.argmax()]

    return {"label": etiquette, "score": round(score, 4)}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    resultat = predict(" ".join(sys.argv[1:]))
    print(f"{resultat['label']} (confiance {resultat['score']:.0%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
