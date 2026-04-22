==============================================================
                       Enchanted Library
==============================================================

Mini-Goodreads dla miłośniczek książek, zbudowany na Flasku.
Tytuły pobierane są na żywo z Open Library API (darmowe, bez
klucza), a konta, półki i recenzje są trzymane lokalnie
w bazie SQLite.

Autorki:  Małgorzata Pytlak, Julia Radosz
Przedmiot: Programowanie w języku Python - Projekt II (2025/26)
Framework: Flask (Python 3.10+)


--------------------------------------------------------------
Instalacja i uruchomienie
--------------------------------------------------------------

Wymagany Python 3.10+ i pip.

Instalacja 

       pip install -r requirements.txt

 Start serwera

       python run.py

   Aplikacja działa pod adresem http://127.0.0.1:5000


--------------------------------------------------------------
Konta testowe
--------------------------------------------------------------

    Admin       login: admin        haslo: puchatek123
    Uzytkownik  login: kopciuszek   haslo: pantofelek


--------------------------------------------------------------
Funkcje aplikacji
--------------------------------------------------------------

  * Katalog - 12 bestsellerów na stronie głównej, zakładki
    gatunków (Fantasy, Thriller, Romance, Horror, History,
    Science), wyszukiwarka po tytule/autorze.

  * Szczegóły książki - opis, biogram autora, rok wydania,
    wydawca, liczba stron, recenzje innych czytelników.

  * Półka (My Shelf) - użytkownik przypisuje książce status
    Want to read / Currently reading / Finished.

  * Recenzje - ocena 1-5 gwiazdek + tekst; wymaga wcześniejszego
    dodania książki do półki.

  * Panel admina - usuwanie recenzji i użytkowników wraz
    z ich danymi.


--------------------------------------------------------------
Testy
--------------------------------------------------------------

       pytest tests/ -v

Testy używają bazy SQLite w pamięci, a wywołania do Open
Library są mockowane (testy nie chodzą do sieci).


--------------------------------------------------------------
