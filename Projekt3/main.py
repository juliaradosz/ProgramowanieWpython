"""Punkt wejścia projektu: wykrywanie spamu / phishingu w SMS-ach.

Tryby uruchomienia:

    python main.py
        Uruchamia pełny eksperyment: pobranie danych, pre-processing,
        trening i strojenie 7 modeli, ocena, wykresy, wybór najlepszego.

    python main.py --classify "Tekst wiadomości do sprawdzenia"
        Wczytuje zapisany najlepszy model i klasyfikuje pojedynczą
        wiadomość (wymaga wcześniejszego uruchomienia treningu).
"""

from __future__ import annotations

import argparse
import sys

# Wymuszamy UTF-8 na wyjściu – w przeciwnym razie polskie znaki są błędnie
# wyświetlane w domyślnej konsoli Windows (strona kodowa cp1250).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import joblib

from src import config
from src.pipeline import run
from src.preprocessing import LABEL_NAMES, clean_text


def classify_message(text: str) -> None:
    """Klasyfikuje pojedynczą wiadomość zapisanym najlepszym modelem."""
    if not config.MODEL_FILE.exists():
        sys.exit(
            "Brak zapisanego modelu. Uruchom najpierw trening: "
            "`python main.py`"
        )

    bundle = joblib.load(config.MODEL_FILE)
    model, vectorizer = bundle["model"], bundle["vectorizer"]

    features = vectorizer.transform([clean_text(text)])
    pred = int(model.predict(features)[0])
    proba = float(model.predict_proba(features)[0, 1])

    print(f"\nWiadomość: {text!r}")
    print(f"Klasyfikacja: {LABEL_NAMES[pred]}")
    print(f"Prawdopodobieństwo, że to spam/phishing: {proba:.2%}")


def main() -> None:
    """Parsuje argumenty wiersza poleceń i wybiera tryb działania."""
    parser = argparse.ArgumentParser(
        description="Wykrywanie spamu/phishingu w wiadomościach SMS."
    )
    parser.add_argument(
        "--classify",
        metavar="TEKST",
        help="zaklasyfikuj pojedynczą wiadomość zapisanym modelem",
    )
    args = parser.parse_args()

    if args.classify:
        classify_message(args.classify)
    else:
        run()


if __name__ == "__main__":
    main()
