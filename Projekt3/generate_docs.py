"""Generator dokumentacji projektu do pliku ``dokumentacja.pdf``.

Skrypt buduje zwięzłą, numerowaną dokumentację całego programu
(opis, uruchomienie, architektura, dane, modele, wyniki, strona WWW,
wkład AI, ograniczenia, źródła). Tabela wyników jest wczytywana na
żywo z ``results/metrics.csv``, więc dokument zawsze odpowiada
ostatniemu uruchomieniu eksperymentu.

Uruchomienie:
    python generate_docs.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

ROOT = Path(__file__).resolve().parent
METRICS = ROOT / "results" / "metrics.csv"
OUTPUT = ROOT / "dokumentacja.pdf"

AUTHOR = "Julia Radosz, Małgorzata Pytlak"
YEAR = "2025/26"

# Czcionki z polskimi znakami (Windows). Gdy brak – fpdf użyje Helvetiki
# (wówczas bez polskich diakrytyków, ale dokument i tak się wygeneruje).
FONT_REG = Path("C:/Windows/Fonts/arial.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/arialbd.ttf")
FONT_MONO = Path("C:/Windows/Fonts/consola.ttf")  # monospace + Unicode

# Po multi_cell przenosimy kursor do lewego marginesu i niżej – inaczej
# kolejne multi_cell(0, ...) nie miałyby już miejsca w poziomie.
NL = {"new_x": XPos.LMARGIN, "new_y": YPos.NEXT}


class DocPDF(FPDF):
    """PDF ze stałą stopką: wyśrodkowany numer strony + autor i rok."""

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font(self.base_font, "", 8)
        self.set_text_color(120, 120, 120)
        half = (self.w - self.l_margin - self.r_margin) / 2
        self.cell(half, 6, f"{AUTHOR}  ·  {YEAR}", align="L")
        self.cell(half, 6, f"—  {self.page_no()}  —", align="R")
        self.set_text_color(0, 0, 0)

    base_font = "Helvetica"
    mono_font = "Courier"


def _load_metrics() -> list[dict]:
    """Wczytuje wiersze z ``results/metrics.csv`` (lub [] gdy brak pliku)."""
    if not METRICS.exists():
        return []
    with METRICS.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _setup_fonts(pdf: DocPDF) -> None:
    """Rejestruje czcionkę z polskimi znakami, jeśli jest dostępna."""
    if FONT_REG.exists() and FONT_BOLD.exists():
        pdf.add_font("Main", "", str(FONT_REG))
        pdf.add_font("Main", "B", str(FONT_BOLD))
        pdf.base_font = "Main"
    else:
        pdf.base_font = "Helvetica"

    # Monospace z polskimi znakami do bloków kodu (rdzeniowy "Courier"
    # obsługuje tylko latin-1, więc nie pomieści np. "obsługa braków").
    if FONT_MONO.exists():
        pdf.add_font("Mono", "", str(FONT_MONO))
        pdf.mono_font = "Mono"
    else:
        pdf.mono_font = pdf.base_font


def _h1(pdf: DocPDF, text: str) -> None:
    pdf.ln(3)
    pdf.set_font(pdf.base_font, "B", 14)
    pdf.set_text_color(150, 20, 70)  # różowy akcent (spójny ze stroną)
    pdf.multi_cell(0, 8, text, **NL)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)


def _h2(pdf: DocPDF, text: str) -> None:
    pdf.ln(1)
    pdf.set_font(pdf.base_font, "B", 11.5)
    pdf.multi_cell(0, 6.5, text, **NL)


def _body(pdf: DocPDF, text: str) -> None:
    pdf.set_font(pdf.base_font, "", 10.5)
    pdf.multi_cell(0, 5.6, text, **NL)
    pdf.ln(1)


def _bullets(pdf: DocPDF, items: list[str]) -> None:
    pdf.set_font(pdf.base_font, "", 10.5)
    for item in items:
        pdf.cell(6)
        pdf.multi_cell(0, 5.6, f"•  {item}", **NL)
    pdf.ln(1)


def _code(pdf: DocPDF, text: str) -> None:
    pdf.set_font(pdf.mono_font, "", 9)
    pdf.set_fill_color(245, 238, 242)
    pdf.multi_cell(0, 5, text, fill=True, border=0, **NL)
    pdf.ln(1)


def _table(pdf: DocPDF, headers: list[str], rows: list[list[str]],
           widths: list[float]) -> None:
    pdf.set_font(pdf.base_font, "B", 9.5)
    pdf.set_fill_color(150, 20, 70)
    pdf.set_text_color(255, 255, 255)
    for h, w in zip(headers, widths):
        pdf.cell(w, 7, h, border=1, align="C", fill=True)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font(pdf.base_font, "", 9)
    fill = False
    for row in rows:
        pdf.set_fill_color(248, 240, 244)
        line_h = 6
        for value, w in zip(row, widths):
            pdf.cell(w, line_h, value, border=1, fill=fill)
        pdf.ln()
        fill = not fill
    pdf.ln(2)


def _title_page(pdf: DocPDF) -> None:
    pdf.add_page()
    pdf.ln(28)
    pdf.set_font(pdf.base_font, "B", 26)
    pdf.set_text_color(150, 20, 70)
    pdf.multi_cell(0, 13, "Detektor spamu / phishingu SMS",
                   align="C", **NL)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font(pdf.base_font, "", 15)
    pdf.multi_cell(0, 9, "Dokumentacja projektu", align="C", **NL)
    pdf.ln(18)

    meta = [
        ("Autor", AUTHOR),
        ("Przedmiot", "Programowanie w języku Python — Projekt 3"),
        ("Temat", "Uczenie maszynowe — klasyfikacja binarna tekstu"),
        ("Język / biblioteki", "Python 3.10+, scikit-learn, Flask"),
        ("Zbiór danych", "SMS Spam Collection (UCI, CC BY 4.0)"),
        ("Rok akademicki", YEAR),
    ]
    pdf.set_x((pdf.w - 150) / 2)
    pdf.set_font(pdf.base_font, "", 10.5)
    for label, value in meta:
        x = (pdf.w - 150) / 2
        pdf.set_x(x)
        pdf.set_font(pdf.base_font, "B", 10.5)
        pdf.cell(45, 8, label, border=1, fill=False)
        pdf.set_font(pdf.base_font, "", 10.5)
        pdf.cell(105, 8, f"  {value}", border=1)
        pdf.ln()


def build() -> None:
    """Buduje cały dokument i zapisuje go do ``dokumentacja.pdf``."""
    pdf = DocPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    _setup_fonts(pdf)

    _title_page(pdf)
    pdf.add_page()

    _h1(pdf, "1.  Opis projektu")
    _body(
        pdf,
        "Projekt rozwiązuje problem klasyfikacji binarnej: rozpoznawanie, "
        "czy wiadomość SMS jest treścią pożądaną (ham), czy spamem / próbą "
        "phishingu (spam). Zbiór jest niezbalansowany — spam stanowi ok. "
        "13% danych — dlatego modele oceniane są przede wszystkim metryką "
        "F1 dla klasy spam, a nie samą dokładnością (trywialny klasyfikator "
        "„zawsze ham” miałby ~87% trafności, będąc bezużytecznym).",
    )
    _h2(pdf, "1.1  Problem i motywacja")
    _body(
        pdf,
        "Spam i phishing SMS to realne zagrożenie: wyłudzanie danych, "
        "oszustwa „na kod BLIK”, fałszywe dopłaty i linki phishingowe. "
        "Zadanie polega na automatycznym oznaczaniu takich wiadomości. "
        "Kluczową trudnością jest niezbalansowanie danych — klasyfikator "
        "musi skutecznie wychwytywać rzadką klasę (spam), a nie tylko "
        "maksymalizować ogólną trafność.",
    )

    _h1(pdf, "2.  Uruchomienie")
    _h2(pdf, "2.1  Wymagania")
    _bullets(pdf, [
        "Python 3.10 lub nowszy (testowano na 3.14),",
        "pip,",
        "zależności z requirements.txt: numpy, pandas, scipy, "
        "scikit-learn, matplotlib, wordcloud, joblib, flask.",
    ])
    _h2(pdf, "2.2  Kroki")
    _body(pdf, "Zalecane wirtualne środowisko:")
    _code(
        pdf,
        "python -m venv .venv\n"
        ".venv\\Scripts\\activate        # Windows\n"
        "# source .venv/bin/activate   # Linux / macOS",
    )
    _body(pdf, "Instalacja zależności:")
    _code(pdf, "pip install -r requirements.txt")
    _body(pdf, "Pełny eksperyment (pobranie danych, trening, wyniki):")
    _code(pdf, "python main.py")
    _body(pdf, "Klasyfikacja pojedynczej wiadomości z wiersza poleceń:")
    _code(pdf, 'python main.py --classify "WINNER!! Call now to claim"')
    _body(pdf, "Strona internetowa (interaktywny klasyfikator):")
    _code(pdf, "python app.py\n# przeglądarka: http://127.0.0.1:5000")

    _h1(pdf, "3.  Struktura projektu")
    _code(
        pdf,
        "main.py            - punkt wejścia CLI (trening / klasyfikacja)\n"
        "app.py             - serwer WWW Flask (strona z klasyfikatorem)\n"
        "generate_docs.py   - generator tego dokumentu (PDF)\n"
        "templates/         - szablon strony (HTML, Jinja2)\n"
        "static/            - styl strony (CSS, motyw różowy)\n"
        "data/              - zbiór danych (pobierany automatycznie)\n"
        "results/           - wykresy, metryki, zapisany model\n"
        "src/\n"
        "  config.py        - ścieżki i parametry globalne\n"
        "  data_loader.py   - pobranie + wczytanie + obsługa braków\n"
        "  preprocessing.py - czyszczenie tekstu + TF-IDF + podział\n"
        "  models.py        - definicje 7 modeli + siatki hiperparametrów\n"
        "  evaluation.py    - metryki + wykresy diagnostyczne\n"
        "  visualization.py - chmury słów + wykresy zbiorcze\n"
        "  pipeline.py      - orkiestracja całego eksperymentu",
    )

    _h1(pdf, "4.  Zbiór danych i pochodzenie przykładów")
    _body(
        pdf,
        "Wykorzystano zbiór SMS Spam Collection z repozytorium UCI "
        "(5574 wiadomości, etykiety ham/spam, licencja CC BY 4.0). Jest "
        "pobierany automatycznie przy pierwszym uruchomieniu i zapisywany "
        "w data/SMSSpamCollection. Po usunięciu duplikatów i pustych "
        "wierszy do uczenia trafia ok. 5158 wiadomości.",
    )
    _h2(pdf, "4.1  Przykłady losowane na stronie")
    _body(
        pdf,
        "Przyciski spam / ham na stronie losują prawdziwą wiadomość danej "
        "klasy bezpośrednio z tego samego zbioru (funkcja _random_example "
        "w app.py) — każde kliknięcie zwraca inną wiadomość. Losowane "
        "przykłady przechodzą przez filtr treści wulgarnych / erotycznych "
        "(_EXPLICIT_PATTERN); filtr działa wyłącznie na podglądzie strony, "
        "natomiast zbiór treningowy i cytowany benchmark UCI pozostają "
        "nienaruszone (zachowanie reprodukowalności). Gdy zbioru nie da "
        "się wczytać, używany jest słownik awaryjny FALLBACK_EXAMPLES.",
    )

    _h1(pdf, "5.  Przetwarzanie danych (pre-processing)")
    _bullets(pdf, [
        "obsługa braków: usunięcie pustych / niekompletnych i "
        "zduplikowanych wierszy,",
        "czyszczenie tekstu: małe litery, usunięcie znaków "
        "niealfabetycznych,",
        "maskowanie tokenami elementów typowych dla phishingu "
        "(URL, e-mail, numery premium, kwoty),",
        "wektoryzacja TF-IDF (unigramy + bigramy, usuwanie stop-words),",
        "redukcja wymiarowości: maks. 3000 cech (max_features) oraz "
        "odrzucenie tokenów bardzo rzadkich (min_df),",
        "podział 80/20 ze stratyfikacją (zachowanie proporcji klas).",
    ])

    _h1(pdf, "6.  Modele uczenia maszynowego")
    _body(
        pdf,
        "Zdefiniowano 7 modeli z różnych rodzin algorytmów; każdy jest "
        "strojony walidacją krzyżową (GridSearchCV, 5 podziałów, kryterium "
        "F1).",
    )
    _table(
        pdf,
        ["Model", "Paradygmat", "Strojony hiperparametr"],
        [
            ["Naive Bayes", "probabilistyczny", "alpha"],
            ["Regresja logistyczna", "liniowy", "C"],
            ["k-NN", "instancyjny", "liczba sąsiadów k"],
            ["Drzewo decyzyjne", "regułowy", "max_depth"],
            ["Las losowy", "zespół (bagging)", "n_estimators, max_depth"],
            ["SVM (jądro liniowe)", "marginesowy", "C"],
            ["Sieć neuronowa (MLP)", "sieć neuronowa", "alpha, warstwy"],
        ],
        [55, 55, 70],
    )

    _h1(pdf, "7.  Metryki i ocena")
    _body(
        pdf,
        "Liczone są wymagane metryki: dokładność (accuracy), logarytmiczna "
        "funkcja straty (log loss), macierz błędów oraz krzywe uczenia się. "
        "Dodatkowo — ze względu na niezbalansowanie — precyzja, czułość, F1 "
        "i pole pod krzywą ROC (ROC AUC). Dla sieci neuronowej zapisywana "
        "jest też krzywa funkcji straty w kolejnych epokach. Wszystkie "
        "wykresy trafiają do katalogu results/.",
    )

    _h1(pdf, "8.  Wyniki")
    metrics = _load_metrics()
    if metrics:
        rows = [
            [
                m["model"],
                f'{float(m["accuracy"]):.4f}',
                f'{float(m["log_loss"]):.4f}',
                f'{float(m["precision"]):.4f}',
                f'{float(m["recall"]):.4f}',
                f'{float(m["f1"]):.4f}',
                f'{float(m["roc_auc"]):.4f}',
            ]
            for m in metrics
        ]
        _table(
            pdf,
            ["Model", "Acc.", "Log loss", "Precyzja", "Czułość",
             "F1 (spam)", "ROC AUC"],
            rows,
            [46, 22, 24, 26, 24, 26, 24],
        )
        best = max(metrics, key=lambda m: float(m["f1"]))
        _body(
            pdf,
            f"Najlepszy model: {best['model']} — najwyższe F1 = "
            f"{float(best['f1']):.4f} (precyzja "
            f"{float(best['precision']):.4f}, czułość "
            f"{float(best['recall']):.4f}) przy ROC AUC = "
            f"{float(best['roc_auc']):.4f} i dokładności = "
            f"{float(best['accuracy']):.4f}. Wybór oparto na F1 dla klasy "
            f"spam, ponieważ zbiór jest niezbalansowany (sama dokładność "
            f"byłaby myląca). Przy zbliżonej skuteczności do SVM i sieci "
            f"neuronowej regresja logistyczna jest modelem prostym, "
            f"szybkim i interpretowalnym (wagi cech), co czyni ją "
            f"wyborem najrozsądniejszym. Model wraz z wektoryzatorem "
            f"zapisywany jest w results/best_model.joblib i używany przez "
            f"stronę WWW oraz tryb --classify.",
        )
        _body(
            pdf,
            "Dokładne wartości mogą się nieznacznie różnić zależnie od "
            "wersji bibliotek; powtarzalność zapewnia ustalone ziarno "
            "RANDOM_STATE = 42. Wszystkie wykresy (chmury słów, macierze "
            "błędów, krzywe uczenia, ROC, porównanie modeli) zapisują się "
            "w katalogu results/.",
        )
    else:
        _body(
            pdf,
            "Brak pliku results/metrics.csv — uruchom najpierw "
            "`python main.py`, aby wygenerować wyniki, a następnie "
            "ponownie ten generator.",
        )

    _h1(pdf, "9.  Strona internetowa")
    _bullets(pdf, [
        "lekki serwer Flask (app.py) wczytujący zapisany najlepszy model,",
        "własny szablon HTML (templates/) i własny CSS (static/) — "
        "motyw różowy z dbałością o kontrast (WCAG AA),",
        "formularz z werdyktem (spam / bezpieczna) i paskiem "
        "prawdopodobieństwa, legenda pojęć ham/spam,",
        "przyciski losujące prawdziwe przykłady ze zbioru (patrz sekcja "
        "4.1) z filtrem treści niestosownych,",
        "obsługa sytuacji bez wytrenowanego modelu (komunikat dla "
        "użytkownika).",
    ])
    _h2(pdf, "9.1  Przykładowe wiadomości do testów")
    _body(
        pdf,
        "Gotowe wiadomości do ręcznego wklejenia w formularz na "
        "prezentacji (model trenowano na zbiorze anglojęzycznym, więc "
        "najlepiej testować po angielsku):",
    )
    _body(pdf, "Spam / phishing:")
    _code(
        pdf,
        "WINNER!! You have won a 1000 cash prize. Call 09061701461 now "
        "to claim your reward!\n"
        "URGENT! You have won a 1 week FREE membership in our 100,000 "
        "Prize Jackpot! Txt CLAIM to 81010",
    )
    _body(pdf, "Ham (treść pożądana):")
    _code(
        pdf,
        "Hey, are we still meeting for lunch tomorrow at noon?\n"
        "Thanks for dinner last night, see you on Sunday at grandma's "
        "place",
    )

    _h1(pdf, "10.  Wkład AI i podział pracy")
    _body(
        pdf,
        "AI (Claude, Anthropic) wykorzystano wyłącznie do zadań "
        "pomocniczych, niewpływających na logikę uczenia maszynowego ani "
        "na metryki i wyniki:",
    )
    _bullets(pdf, [
        "pula słów do filtrowania treści wulgarnych / erotycznych w "
        "przykładach losowanych na stronie (_EXPLICIT_PATTERN w app.py) "
        "— działa tylko na podglądzie, zbiór i modele bez zmian,",
        "stylizacja strony: static/style.css (motyw różowy, kontrast, "
        "responsywność) i drobne elementy prezentacyjne szablonu,",
        "skrypt generujący oraz wygenerowanie tego pliku PDF — układ, "
        "tabele, formatowanie (treść merytoryczna pochodzi od autorek),",
        "redakcja i formatowanie tekstu README oraz tej dokumentacji.",
    ])
    _body(
        pdf,
        "Cała logika eksperymentu ML oraz logika strony zostały "
        "opracowane przez autorki. Pracę podzielono na dwa równe filary:",
    )
    _h2(pdf, "10.1  Julia Radosz — dane, pre-processing i modele")
    _bullets(pdf, [
        "config.py, data_loader.py — parametry, pobranie danych, obsługa "
        "braków i duplikatów,",
        "preprocessing.py — czyszczenie tekstu, maskowanie tokenami, "
        "TF-IDF, podział ze stratyfikacją,",
        "models.py — dobór i strojenie 7 modeli (siatki hiperparametrów),",
        "pipeline.py (część) — trening, GridSearchCV, wybór najlepszego "
        "modelu; main.py — tryb CLI.",
    ])
    _h2(pdf, "10.2  Małgorzata Pytlak — ewaluacja, wizualizacje, strona")
    _bullets(pdf, [
        "evaluation.py — accuracy, log loss, macierz błędów, krzywe "
        "uczenia, F1, ROC AUC,",
        "visualization.py — chmury słów, rozkłady, porównanie modeli,",
        "pipeline.py (część) — analiza eksploracyjna, zapis wyników,",
        "app.py + templates/index.html — strona: klasyfikacja i losowanie "
        "przykładów; treść merytoryczna dokumentacji.",
    ])
    _body(
        pdf,
        "Każda z autorek zna i potrafi omówić swój obszar podczas dyskusji. "
        "Niniejszy dokument jest jedynym, kompletnym źródłem informacji o "
        "wkładzie własnym, użyciu AI oraz bibliografii (sekcja 12).",
    )
    _h2(pdf, "10.3  Elementy z samouczków / dokumentacji")
    _body(
        pdf,
        "API i dobór parametrów modeli opierają się na oficjalnej "
        "dokumentacji scikit-learn (zob. sekcja 12.3). Kod nie kopiuje "
        "gotowych samouczków 1:1 — wzorce użycia (GridSearchCV, "
        "TfidfVectorizer, learning_curve) pochodzą z dokumentacji "
        "biblioteki i zostały dostosowane do specyfiki zadania.",
    )

    _h1(pdf, "11.  Znane ograniczenia")
    _bullets(pdf, [
        "model trenowany na zbiorze anglojęzycznym — wiadomości po polsku "
        "klasyfikuje słabo (słownik cech jest angielski),",
        "filtr treści niestosownych jest oparty na liście słów — może "
        "pominąć nietypowe sformułowania,",
        "brak modeli głębokich (np. transformerów) — świadomy wybór na "
        "rzecz przejrzystości i czasu uczenia,",
        "wyniki mogą się minimalnie różnić zależnie od wersji bibliotek "
        "(powtarzalność zapewnia ustalone ziarno losowości).",
    ])

    _h1(pdf, "12.  Bibliografia i źródła")
    _body(
        pdf,
        "Sekcja stanowi pełną bibliografię projektu. Brak lub błędne "
        "cytowanie źródeł wpływa na ocenę — lista poniżej jest kompletna "
        "i obejmuje zbiór danych, biblioteki (z wersjami), źródła "
        "internetowe (z datą dostępu) oraz wykorzystane narzędzie AI.",
    )
    _h2(pdf, "12.1  Zbiór danych")
    _bullets(pdf, [
        "Almeida, T. & Hidalgo, J. (2011). SMS Spam Collection [Dataset]. "
        "UCI Machine Learning Repository. https://doi.org/10.24432/C5CC84 "
        "— https://archive.ics.uci.edu/dataset/228/sms+spam+collection "
        "(data dostępu: 2026-05-19). Licencja: CC BY 4.0.",
    ])
    _h2(pdf, "12.2  Biblioteki i frameworki (nazwa + wersja)")
    _bullets(pdf, [
        "NumPy 2.4.1 — https://numpy.org",
        "pandas 3.0.3 — https://pandas.pydata.org",
        "SciPy 1.17.1 — https://scipy.org",
        "scikit-learn 1.8.0 — https://scikit-learn.org",
        "Matplotlib 3.10.8 — https://matplotlib.org",
        "WordCloud 1.9.6 — https://github.com/amueller/word_cloud",
        "joblib 1.5.3 — https://joblib.readthedocs.io",
        "Flask 3.1.2 — https://flask.palletsprojects.com",
        "fpdf2 2.8.7 — https://py-pdf.github.io/fpdf2/ "
        "(generator tej dokumentacji).",
    ])
    _h2(pdf, "12.3  Dokumentacja / źródła internetowe")
    _bullets(pdf, [
        "scikit-learn — User Guide (klasyfikacja, dobór modelu, metryki). "
        "https://scikit-learn.org/stable/user_guide.html "
        "(data dostępu: 2026-05-19).",
    ])
    _h2(pdf, "12.4  Narzędzia AI")
    _bullets(pdf, [
        "Model: Claude Opus 4.7 (claude-opus-4-7).",
        "Producent: Anthropic.",
        "Zastosowanie: zadania pomocnicze, niemerytoryczne — filtr treści "
        "na stronie, stylizacja (CSS), skrypt i formatowanie tej "
        "dokumentacji PDF oraz redakcja tekstu (zob. sekcja 10).",
        "Data dostępu: 2026-05-19.",
        "Zakres weryfikacji: projekt uruchomiono i przetestowano (pełny "
        "pipeline, klasyfikacja, strona WWW); każda z autorek weryfikuje "
        "i rozumie swój obszar pracy przed prezentacją.",
    ])

    pdf.output(str(OUTPUT))
    print(f"Zapisano dokumentację: {OUTPUT}")


if __name__ == "__main__":
    build()
