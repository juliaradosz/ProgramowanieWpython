"""Funkcje pomocnicze niezależne od warstwy webowej."""

from __future__ import annotations

import re
import unicodedata

# Mapowanie polskich znaków na ich odpowiedniki ASCII (na potrzeby slugów URL).
_POLISH_MAP = str.maketrans(
    "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ",
    "acelnoszzACELNOSZZ",
)


def slugify(value: str) -> str:
    """Tworzy "slug" przyjazny dla adresów URL z dowolnego tekstu.

    Przykład: ``"Zupa krem z dyni"`` -> ``"zupa-krem-z-dyni"``.

    Polskie znaki diakrytyczne są transliterowane (``ł`` -> ``l`` itd.),
    pozostałe znaki spoza zakresu liter i cyfr zamieniane na myślniki.
    """
    value = value.translate(_POLISH_MAP)
    # Usuń ewentualne pozostałe znaki diakrytyczne (np. z innych języków).
    value = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "przepis"


def allowed_image(filename: str, allowed_extensions: set[str]) -> bool:
    """Sprawdza, czy plik ma rozszerzenie dozwolone dla obrazów."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions
