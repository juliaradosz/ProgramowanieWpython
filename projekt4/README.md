# Projekt IV – Przepisy Kulinarne (Flask + AI)

**Programowanie w języku Python 2025/26**  

## Autorki

| Osoba | Zakres pracy |
|-------|-------------|
| **Julia Radosz** | Przepisanie strony kulinarnej z Django na Flask: struktura blueprintów (`main`, `auth`), modele danych (SQLAlchemy), formularze (Flask-WTF), szablony Jinja2, komendy CLI (`init-db`, `seed`), obsługa błędów 404/500 |

| **Małgorzata Pytlak** | Integracja asystenta kulinarnego AI: moduł `ai_assistant.py`, blueprint `chat`, endpoint JSON `/asystent/wiadomosc`, szablon `chat.html`, skrypt `chat.js`, konfiguracja klucza API, tryb offline |

---

## Opis projektu

Projekt IV łączy dwa wcześniejsze projekty:

- **Projekt I** – strona kulinarna napisana w Django (folder `Projekt02`)
- **Projekt IV** – ta sama strona przepisana we Flasku, rozszerzona o asystenta kulinarnego AI (folder `przepisy_flask`)

Powiązanie polega na przepisaniu aplikacji Django na Flask (zmiana frameworka) oraz dodaniu komponentu wykraczającego poza pierwotny zakres – czatu z modelem językowym, który odpowiada na pytania kulinarne.

---

## Funkcjonalności

### Strona (Flask)
- Przeglądanie przepisów z podziałem na kategorie
- Wyszukiwanie przepisów
- Konta użytkowników (rejestracja, logowanie, profil, avatar)
- Konto administratora z rozszerzonymi uprawnieniami
- Dodawanie, edytowanie i usuwanie własnych przepisów (CRUD)
- Dodawanie komentarzy z oceną (1–5 gwiazdek)
- Lista ulubionych przepisów
- Przesyłanie zdjęć przepisów
- Własne strony błędów 404 i 500

### Asystent kulinarny AI
- Czat z modelem językowym dostępny pod `/asystent/`
- Asystent odpowiada wyłącznie po polsku i wyłącznie na pytania kulinarne
- Możliwość otwarcia czatu w kontekście konkretnego przepisu – asystent zna jego składniki i może doradzić np. zamienniki
- Historia rozmowy przechowywana po stronie przeglądarki
- Tryb offline – strona działa normalnie bez klucza API

---

## Struktura projektu

```
projekt4/
├── Projekt02/               # Oryginalna strona w Django (Projekt I)
│   ├── przepisy_project/    # Ustawienia Django
│   ├── recipes/             # Aplikacja Django (modele, widoki, formularze, testy)
│   └── templates/
└── przepisy_flask/          # Przepisana strona w Flask (Projekt IV)
    ├── blueprints/
    │   ├── auth.py          # Rejestracja, logowanie, wylogowanie
    │   ├── chat.py          # Endpoint asystenta AI
    │   └── main.py          # Przepisy, kategorie, wyszukiwanie, ulubione
    ├── templates/           # Szablony Jinja2
    ├── static/              # CSS, JS
    ├── ai_assistant.py      # Integracja z API modelu językowego
    ├── models.py            # Modele SQLAlchemy
    ├── forms.py             # Formularze Flask-WTF
    ├── config.py            # Konfiguracja aplikacji
    ├── app.py               # Fabryka aplikacji, CLI
    ├── seed.py              # Dane przykładowe
    └── requirements.txt
```

---

## Uruchomienie

### Wymagania
- Python 3.10+
- pip

### Instalacja

```bash
cd przepisy_flask
pip install -r requirements.txt
```
### Uruchomienie serwera

# Uruchom serwer deweloperski
python3 app.py
```

Strona dostępna pod adresem: http://127.0.0.1:5000

### Domyślne konto administratora (po `seed`)

| Login | Hasło |
|-------|-------|
| `admin` | `admin123` |

---

## Wykorzystanie AI w projekcie

Do pomocy przy realizacji projektu korzystałyśmy z asystenta Claude (Anthropic). AI pomogło przy:
- dopasowaniu nazw modeli API Groq do darmowego tieru
- debugowaniu błędów konfiguracji klucza API
- uzupełnieniu docstringów w kodzie

Cały kod logiki aplikacji (modele, blueprinty, formularze, szablony, integracja AI) został napisany samodzielnie przez autorki. Kod był każdorazowo weryfikowany i rozumiany przed użyciem.

**Model AI użyty w asystencie:**  
`llama-3.3-70b-versatile`, Meta / Groq, Inc., dostęp: czerwiec 2026.

**Model AI użyty przy tworzeniu projektu:**  
Claude Sonnet 4.6, Anthropic, PBC, dostęp: czerwiec 2026.

---

## Bibliografia

### Dokumentacja frameworków i bibliotek

- Flask 3.1.2 – Pallets Projects, https://flask.palletsprojects.com, dostęp: czerwiec 2026
- Flask-SQLAlchemy 3.1.1 – Pallets Projects, https://flask-sqlalchemy.palletsprojects.com, dostęp: czerwiec 2026
- Flask-Login 0.6.3 – Matthew Frazier, https://flask-login.readthedocs.io, dostęp: czerwiec 2026
- Flask-WTF 1.3.0 – Pallets Projects, https://flask-wtf.readthedocs.io, dostęp: czerwiec 2026
- SQLAlchemy – Mike Bayer, https://docs.sqlalchemy.org, dostęp: czerwiec 2026
- Groq Python SDK 0.13.0 – Groq, Inc., https://console.groq.com/docs, dostęp: czerwiec 2026
- Django 4.x – Django Software Foundation, https://docs.djangoproject.com, dostęp: marzec 2025
- Jinja2 – Pallets Projects, https://jinja.palletsprojects.com, dostęp: czerwiec 2026
- Bootstrap 5 – The Bootstrap Team, https://getbootstrap.com/docs/5.0, dostęp: czerwiec 2026

### Książki

- Robert C. Martin, *Czysty kod. Podręcznik dobrego programisty*, Helion, 2010
- Guido van Rossum i in., *PEP 8 – Style Guide for Python Code*, https://peps.python.org/pep-0008, dostęp: czerwiec 2026

### Pozostałe źródła

- *Flask Blueprints*, Real Python, https://realpython.com/flask-blueprint, dostęp: czerwiec 2026
- *Flask Mega-Tutorial*, Miguel Grinberg, https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world, dostęp: czerwiec 2026
- *Groq API Quickstart*, Groq, Inc., https://console.groq.com/docs/quickstart, dostęp: czerwiec 2026
