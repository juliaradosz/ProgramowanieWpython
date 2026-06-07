"""Strona internetowa do wykrywania spamu / phishingu (serwer Flask).

Lekka aplikacja WWW, która wczytuje wytrenowany wcześniej najlepszy model
(``results/best_model.joblib``) i pozwala interaktywnie sprawdzić, czy
wpisana wiadomość to spam/phishing.

Uruchomienie:
    python app.py
a następnie otwórz w przeglądarce:  http://127.0.0.1:5000

Uwaga: najpierw należy wytrenować model poleceniem ``python main.py`` —
bez zapisanego modelu strona poprosi o jego wcześniejsze wygenerowanie.
"""

from __future__ import annotations

import joblib
import pandas as pd
from flask import Flask, render_template, request

from src import config
from src.data_loader import load_dataframe
from src.preprocessing import LABEL_NAMES, clean_text

app = Flask(__name__)

FALLBACK_EXAMPLES: dict[str, str] = {
    "spam": (
        "WINNER!! You have won a 1000 cash prize. "
        "Call 09061701461 now to claim your reward!"
    ),
    "ham": "Hey, are we still meeting for lunch tomorrow at noon?",
}

# Filtr treści wulgarnych/erotycznych po to, by nie wyświetlić niestosownej wiadomości
_EXPLICIT_PATTERN = (
    r"\b(?:horny|naked|nude|sex|sexy|sexual|porn|porno|xxx|slut|slutty|"
    r"boobs|tits|fuck|fucking|shit|bitch|cock|dick|pussy|cum|orgasm|"
    r"erotic|escort|whore|wank)\b"
)

# Zasoby wczytywane raz i trzymane w pamięci procesu (tani cache).
_BUNDLE: dict | None = None
_DATA: pd.DataFrame | None = None


def _examples_df() -> pd.DataFrame:
    """Wczytuje (raz) zbiór wiadomości, z którego losujemy przykłady."""
    global _DATA
    if _DATA is None:
        _DATA = load_dataframe()
    return _DATA


def _random_example(label: str) -> str:
    """Losuje treść wiadomości danej klasy ('spam'/'ham') ze zbioru."""
    if label not in ("spam", "ham"):
        return ""
    try:
        pool = _examples_df()
        pool = pool.loc[pool["label"] == label, "message"]
        clean = pool[~pool.str.contains(
            _EXPLICIT_PATTERN, case=False, regex=True, na=False
        )]
        pool = clean if len(clean) else pool
        if len(pool):
            return str(pool.sample(1).iloc[0])
    except Exception:
        pass
    return FALLBACK_EXAMPLES.get(label, "")


def _load_bundle() -> dict | None:
    """Wczytuje (raz) słownik z modelem i wektoryzatorem; None, gdy brak."""
    global _BUNDLE
    if _BUNDLE is None and config.MODEL_FILE.exists():
        _BUNDLE = joblib.load(config.MODEL_FILE)
    return _BUNDLE


def _classify(message: str) -> dict:
    """Klasyfikuje wiadomość i zwraca dane gotowe do wyświetlenia."""
    bundle = _load_bundle()
    features = bundle["vectorizer"].transform([clean_text(message)])
    pred = int(bundle["model"].predict(features)[0])
    spam_proba = float(bundle["model"].predict_proba(features)[0, 1])
    return {
        "message": message,
        "is_spam": pred == 1,
        "label": LABEL_NAMES[pred],
        # Pewność dotyczy przewidzianej klasy (nie zawsze klasy "spam").
        "confidence": spam_proba if pred == 1 else 1.0 - spam_proba,
        "spam_proba": spam_proba,
    }


@app.route("/", methods=["GET", "POST"])
def index():
    """Strona główna: formularz + wynik klasyfikacji."""
    model_ready = config.MODEL_FILE.exists()

    # Po kliknięciu "spam"/"ham" losujemy wiadomość tej klasy ze zbioru.
    prefill = _random_example(request.args.get("example", ""))
    result = None
    error = None

    if request.method == "POST":
        message = (request.form.get("message") or "").strip()
        prefill = message
        if not model_ready:
            error = (
                "Brak wytrenowanego modelu. Uruchom najpierw "
                "`python main.py`, aby go wygenerować."
            )
        elif not message:
            error = "Wpisz treść wiadomości do sprawdzenia."
        else:
            result = _classify(message)

    return render_template(
        "index.html",
        model_ready=model_ready,
        prefill=prefill,
        result=result,
        error=error,
    )


if __name__ == "__main__":
    # debug=True ułatwia pracę; do "produkcji" należałoby go wyłączyć.
    app.run(host="127.0.0.1", port=5000, debug=True)
