"""Konfiguracja projektu: ścieżki, stałe i parametry globalne.

Wszystkie moduły korzystają z tych samych ścieżek i ziarna losowości,
dzięki czemu wyniki eksperymentów są w pełni powtarzalne.
"""

from __future__ import annotations

from pathlib import Path

# --- Ścieżki -----------------------------------------------------------------
# ROOT = katalog główny projektu (Projekt3/), niezależnie od miejsca uruchomienia.
ROOT_DIR: Path = Path(__file__).resolve().parents[1]
DATA_DIR: Path = ROOT_DIR / "data"
RAW_DATA_FILE: Path = DATA_DIR / "SMSSpamCollection"
RESULTS_DIR: Path = ROOT_DIR / "results"
MODEL_FILE: Path = RESULTS_DIR / "best_model.joblib"
METRICS_FILE: Path = RESULTS_DIR / "metrics.csv"

# --- Źródło danych -----------------------------------------------------------
# Zbiór "SMS Spam Collection" z repozytorium UCI Machine Learning.
DATASET_URL: str = (
    "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
)
DATASET_MEMBER: str = "SMSSpamCollection"  # nazwa pliku wewnątrz archiwum ZIP

# --- Parametry eksperymentu --------------------------------------------------
RANDOM_STATE: int = 42        # ziarno losowości – powtarzalność wyników
TEST_SIZE: float = 0.20       # 20% danych odkładamy na zbiór testowy

# --- Parametry wektoryzacji TF-IDF ------------------------------------------
# max_features ogranicza wymiarowość przestrzeni cech (redukcja wymiarowości),
# min_df odrzuca bardzo rzadkie tokeny (redukcja szumu i przeuczenia).
TFIDF_MAX_FEATURES: int = 3000
TFIDF_MIN_DF: int = 2
TFIDF_NGRAM_RANGE: tuple[int, int] = (1, 2)  # słowa pojedyncze + bigramy


def ensure_dirs() -> None:
    """Tworzy katalogi na dane i wyniki, jeśli jeszcze nie istnieją."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
