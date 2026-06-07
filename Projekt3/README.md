# Projekt 3 (PPy) — Wykrywanie spamu / phishingu w wiadomościach SMS

Projekt zaliczeniowy z przedmiotu *Programowanie w języku Python*
(2025/26). Celem jest rozwiązanie problemu **klasyfikacji binarnej**
metodami uczenia maszynowego: rozpoznawanie, czy dana wiadomość SMS jest
treścią pożądaną (`ham`), czy spamem / próbą phishingu (`spam`).

> **Pełny przewodnik po programie znajduje się w pliku
> [`dokumentacja.pdf`](dokumentacja.pdf)** — opis i motywacja, instrukcja
> uruchomienia, struktura, zbiór danych, pre-processing, modele, metryki,
> wyniki, strona WWW, wkład AI i podział pracy oraz pełna bibliografia.
> Ten plik README jest jedynie zwięzłym wprowadzeniem.

## W skrócie

- **Problem:** spam/phishing SMS to realne zagrożenie (wyłudzenia,
  oszustwa „na kod BLIK", fałszywe dopłaty). Zbiór jest niezbalansowany
  (~13% spamu), więc modele oceniamy metryką **F1** dla klasy spam,
  a nie samą dokładnością.
- **Dane:** *SMS Spam Collection* (UCI, CC BY 4.0) — pobierany
  automatycznie przy pierwszym uruchomieniu. Pełne dane i cytowanie:
  sekcje 4 i 12.1 dokumentacji.
- **Metoda:** pre-processing tekstu + TF-IDF, **7 modeli** z różnych
  rodzin algorytmów, każdy strojony walidacją krzyżową (`GridSearchCV`).
  Metryki: accuracy, log loss, macierz błędów, krzywe uczenia, F1,
  ROC AUC.
- **Wynik:** najlepszy model — **regresja logistyczna** (F1 ≈ 0.94).
  Pełna tabela wyników: sekcja 8 dokumentacji.

## Szybki start

Wymagany Python 3.10+ (testowano na 3.14).

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt

python main.py                    # pełny eksperyment (dane, trening, wyniki)
python main.py --classify "WINNER!! Call now to claim your free prize"
python app.py                     # strona WWW: http://127.0.0.1:5000
```

Szczegółowa instrukcja uruchomienia: sekcja 2 dokumentacji.

## Autorzy

- **Julia Radosz** — dane, pre-processing i modele: pobranie i
  porządkowanie danych, czyszczenie tekstu i wektoryzacja TF-IDF, dobór
  i strojenie 7 modeli, trening i wybór najlepszego, tryb CLI.
- **Małgorzata Pytlak** — ewaluacja, wizualizacje i strona WWW: metryki
  i wykresy diagnostyczne, analiza eksploracyjna, serwer Flask z
  klasyfikatorem, treść merytoryczna dokumentacji.

> Szczegółowy podział pracy oraz zakres wsparcia AI: sekcja 10
> dokumentacji ([`dokumentacja.pdf`](dokumentacja.pdf)).

## Licencja i źródła

Kod udostępniony na licencji **MIT** ([`LICENSE`](LICENSE)). Informacja
o wkładzie własnym, użyciu narzędzi AI oraz pełna bibliografia: sekcje 10
i 12 dokumentacji ([`dokumentacja.pdf`](dokumentacja.pdf)).
