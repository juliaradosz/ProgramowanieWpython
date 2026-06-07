"""Pobieranie i wczytywanie zbioru danych "SMS Spam Collection".

Zbiór jest pobierany automatycznie z repozytorium UCI przy pierwszym
uruchomieniu i zapisywany lokalnie w katalogu ``data/``. Kolejne
uruchomienia korzystają już z kopii lokalnej (brak ponownego pobierania).
"""

from __future__ import annotations

import io
import urllib.request
import zipfile

import pandas as pd

from . import config


def download_dataset() -> None:
    """Pobiera archiwum ZIP z UCI i wypakowuje plik z danymi do ``data/``.

    Jeśli plik z danymi już istnieje lokalnie, funkcja nic nie robi.
    """
    config.ensure_dirs()
    if config.RAW_DATA_FILE.exists():
        print(f"[data] Zbiór już istnieje lokalnie: {config.RAW_DATA_FILE}")
        return

    print(f"[data] Pobieram zbiór z: {config.DATASET_URL}")
    with urllib.request.urlopen(config.DATASET_URL, timeout=60) as response:
        archive_bytes = response.read()

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        raw_bytes = archive.read(config.DATASET_MEMBER)

    config.RAW_DATA_FILE.write_bytes(raw_bytes)
    print(f"[data] Zapisano zbiór do: {config.RAW_DATA_FILE}")


def load_dataframe() -> pd.DataFrame:
    """Wczytuje zbiór do ``DataFrame`` i wykonuje minimalne porządkowanie.

    Returns:
        DataFrame z dwiema kolumnami:
            ``label``  – etykieta tekstowa (``ham`` / ``spam``),
            ``message`` – treść wiadomości SMS.

    Etapy porządkowania (element wymagany: obsługa brakujących danych):
        * usunięcie wierszy z brakującą treścią lub etykietą,
        * usunięcie białych znaków z brzegów wiadomości,
        * usunięcie duplikatów (te same wiadomości zaburzają ocenę modelu).
    """
    download_dataset()

    # Plik ma format: <etykieta>\t<treść wiadomości>, kodowanie latin-1.
    df = pd.read_csv(
        config.RAW_DATA_FILE,
        sep="\t",
        header=None,
        names=["label", "message"],
        encoding="latin-1",
    )

    n_start = len(df)

    df = df.dropna(subset=["label", "message"])

    df["message"] = df["message"].astype(str).str.strip()
    df = df[df["message"].str.len() > 0]

    df = df.drop_duplicates(subset=["message"]).reset_index(drop=True)

    n_removed = n_start - len(df)
    print(
        f"[data] Wczytano {len(df)} wiadomości "
        f"(usunięto {n_removed} brakujących/pustych/zduplikowanych)."
    )
    return df


if __name__ == "__main__":
    # Szybki test modułu: wypisuje podstawowe statystyki zbioru.
    data = load_dataframe()
    print(data["label"].value_counts())
    print(data.head())
