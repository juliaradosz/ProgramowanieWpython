"""Wstępne przetwarzanie danych tekstowych (pre-processing).

Realizuje wymagany element projektu: przygotowanie danych przed uczeniem.
Obejmuje:
    * czyszczenie i normalizację tekstu,
    * kodowanie etykiet (ham -> 0, spam -> 1),
    * podział na zbiór uczący i testowy ze stratyfikacją,
    * wektoryzację TF-IDF z ograniczeniem wymiarowości (redukcja wymiarów).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

from . import config

# Mapowanie etykiet tekstowych na liczby. Spam = 1 jest "klasą pozytywną"
# (interesuje nas głównie skuteczność wykrywania spamu/phishingu).
LABEL_MAP: dict[str, int] = {"ham": 0, "spam": 1}
LABEL_NAMES: list[str] = ["ham (pożądana)", "spam / phishing"]

# Wzorce do "maskowania" elementów typowych dla phishingu. Zamiana na token
# zamiast usuwania zachowuje informację, że taki element w ogóle wystąpił.
_URL_RE = re.compile(r"http\S+|www\.\S+")
_EMAIL_RE = re.compile(r"\S+@\S+")
_PHONE_RE = re.compile(r"\b\d{6,}\b")          # długie ciągi cyfr = numery premium
_MONEY_RE = re.compile(r"[£$€]\s?\d+|\d+\s?(?:gbp|usd|eur)\b", re.IGNORECASE)
_NON_LETTER_RE = re.compile(r"[^a-z\s]")
_MULTISPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Czyści pojedynczą wiadomość i sprowadza ją do postaci znormalizowanej.

    Kroki:
        1. zamiana na małe litery,
        2. zastąpienie URL / e-mail / numerów / kwot tokenami specjalnymi
           (dla phishingu sam fakt ich obecności jest istotną cechą),
        3. usunięcie pozostałych znaków niebędących literami,
        4. redukcja wielokrotnych spacji.

    Args:
        text: surowa treść wiadomości.

    Returns:
        Oczyszczony, znormalizowany tekst.
    """
    text = text.lower()
    text = _URL_RE.sub(" tokenurl ", text)
    text = _EMAIL_RE.sub(" tokenemail ", text)
    text = _MONEY_RE.sub(" tokenmoney ", text)
    text = _PHONE_RE.sub(" tokennumber ", text)
    text = _NON_LETTER_RE.sub(" ", text)
    text = _MULTISPACE_RE.sub(" ", text).strip()
    return text


@dataclass
class Dataset:
    """Komplet danych po podziale i wektoryzacji.

    Atrybuty z sufiksem ``_vec`` to rzadkie macierze cech TF-IDF
    podawane na wejście modeli; ``_raw`` to wersje tekstowe (np. do chmur słów).
    """

    X_train_vec: csr_matrix
    X_test_vec: csr_matrix
    y_train: np.ndarray
    y_test: np.ndarray
    X_train_raw: pd.Series
    X_test_raw: pd.Series
    vectorizer: TfidfVectorizer
    feature_names: np.ndarray


def prepare_dataset(df: pd.DataFrame) -> Dataset:
    """Wykonuje pełny pre-processing: czyszczenie, podział i wektoryzację.

    Args:
        df: ramka z kolumnami ``label`` i ``message``.

    Returns:
        Obiekt :class:`Dataset` gotowy do trenowania modeli.
    """
    cleaned = df["message"].apply(clean_text)
    y = df["label"].map(LABEL_MAP).to_numpy()

    # Podział na zbiór uczący/testowy ZE STRATYFIKACJĄ – zachowuje ten sam
    # udział spamu w obu zbiorach (zbiór jest niezbalansowany ~13% spamu).
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        cleaned,
        y,
        test_size=config.TEST_SIZE,
        random_state=config.RANDOM_STATE,
        stratify=y,
    )

    # Wektoryzacja TF-IDF. Uczona WYŁĄCZNIE na zbiorze treningowym,
    # aby uniknąć "wycieku" informacji ze zbioru testowego.
    # max_features + min_df ograniczają wymiarowość przestrzeni cech.
    vectorizer = TfidfVectorizer(
        max_features=config.TFIDF_MAX_FEATURES,
        min_df=config.TFIDF_MIN_DF,
        ngram_range=config.TFIDF_NGRAM_RANGE,
        stop_words="english",
        sublinear_tf=True,
    )
    X_train_vec = vectorizer.fit_transform(X_train_raw)
    X_test_vec = vectorizer.transform(X_test_raw)

    print(
        f"[prep] Zbiór uczący: {X_train_vec.shape[0]} próbek, "
        f"testowy: {X_test_vec.shape[0]} próbek, "
        f"liczba cech TF-IDF: {X_train_vec.shape[1]}"
    )
    return Dataset(
        X_train_vec=X_train_vec,
        X_test_vec=X_test_vec,
        y_train=y_train,
        y_test=y_test,
        X_train_raw=X_train_raw.reset_index(drop=True),
        X_test_raw=X_test_raw.reset_index(drop=True),
        vectorizer=vectorizer,
        feature_names=vectorizer.get_feature_names_out(),
    )
