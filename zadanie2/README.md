# Przepisy Kulinarne - Aplikacja Django

Strona internetowa do przeglądania, dodawania i komentowania przepisów kulinarnych.  
Aplikacja pozwala użytkownikom tworzyć własne przepisy, oceniać dania innych użytkowników oraz zapisywać ulubione przepisy.

## Funkcjonalności

- **Przeglądanie przepisów** – lista przepisów z podziałem na kategorie
- **Szczegóły przepisu** – wyświetlanie opisu, składników oraz instrukcji przygotowania
- **CRUD przepisów** – dodawanie, edycja i usuwanie przepisów (wymaga logowania)
- **System komentarzy** – ocenianie i komentowanie przepisów (1-5 gwiazdek)
- **Ulubione przepisy** – możliwość zapisywania przepisów w ulubionych
- **Konta użytkowników** – rejestracja, logowanie, profile z avatarami
- **Profile użytkowników** – lista przepisów oraz ulubionych dań użytkownika
- **Wyszukiwanie** – wyszukiwanie przepisów po tytule, opisie, składnikach i poziomie trudności
- **Kategorie przepisów** – podział przepisów na kategorie (np. Zupy, Desery)
- **Panel administracyjny** – zarządzanie wszystkimi danymi aplikacji
- **Responsywny design** – interfejs oparty o Bootstrap 5

## Wymagania

- Python 3.10+
- Django 5.0+
- Pillow (obsługa obrazów)

## Instalacja i uruchomienie

```bash
# instalacja zależności
pip install -r requirements.txt

# wykonanie migracji bazy danych
python manage.py migrate

# utworzenie konta administratora
python manage.py createsuperuser

# wypełnienie bazy przykładowymi danymi
python manage.py seed_data

# uruchomienie serwera
python manage.py runserver

Po uruchomieniu aplikacja będzie dostępna pod adresem:

`http://127.0.0.1:8000`

Panel administracyjny:

`http://127.0.0.1:8000/admin`

## Komendy manage.py

Aplikacja zawiera dodatkowe komendy Django:

`python manage.py seed_data` – wypełnia bazę przykładowymi przepisami

`python manage.py import_recipes plik.csv` – importuje przepisy z pliku CSV

`python manage.py delete_old_recipes --days 30` – usuwa stare nieopublikowane przepisy

`python manage.py download_images` – automatycznie pobiera zdjęcia dla przepisów

`python manage.py import_ingredients plik.csv` – importuje składniki dla przepisówo


## Import przepisów z CSV

Przepisy można zaimportować z pliku CSV przy użyciu komendy:


python manage.py import_recipes recipes.csv


Przykładowy format pliku CSV:


title,category,description,instructions,prep_time,cook_time,servings,difficulty
```

## Uruchamianie testów

Projekt zawiera zestaw testów jednostkowych obejmujących modele, widoki, formularze oraz komendy Django.

Uruchomienie wszystkich testów:

python manage.py test

Łącznie projekt zawiera około **60 testów jednostkowych**.

## Modele danych

Projekt wykorzystuje następujące modele:

* **Category** – kategorie przepisów (np. Zupy, Desery, Sałatki)
* **Tag** – tagi przepisów (np. wegetariańskie, szybkie) – relacja ManyToMany z Recipe
* **Recipe** – przepisy (relacja ForeignKey do User i Category)
* **Ingredient** – składniki przepisu (relacja ForeignKey do Recipe)
* **Comment** – komentarze z oceną (relacja ForeignKey do Recipe i User)
* **UserProfile** – rozszerzony profil użytkownika (OneToOne z User)

## Struktura projektu

```
przepisy_project/      – konfiguracja Django (settings, urls)

recipes/               – główna aplikacja
  models.py            – modele danych
  views.py             – widoki aplikacji
  forms.py             – formularze
  urls.py              – routing
  admin.py             – konfiguracja panelu admina

  management/commands/ – komendy manage.py
      seed_data.py
      import_recipes.py
      delete_old_recipes.py
      download_images.py

  tests/               – testy aplikacji
      test_models.py
      test_views.py
      test_forms.py
      test_commands.py

templates/             – szablony HTML (Bootstrap 5)
static/css/            – pliki CSS
media/                 – przesyłane zdjęcia przepisów
```

## Technologie

Projekt został zrealizowany przy użyciu:

* Python
* Django
* SQLite
* Bootstrap 5
* HTML
* CSS
* Pillow

## Autor
Julia Radosz
Zakres pracy:

* implementacja modeli danych (Category, Recipe, Ingredient, Comment, UserProfile)

* implementacja widoków aplikacji (views.py)

* obsługa CRUD przepisów

* implementacja systemu komentarzy i ocen

* przygotowanie formularzy Django

* integracja z bazą danych

Małgorzata Pytlak

Zakres pracy:

* przygotowanie szablonów HTML i stylizacji (Bootstrap)

* implementacja profili użytkowników oraz systemu ulubionych przepisów

* wyszukiwarka przepisów

* przygotowanie komend manage.py

* import danych z plików CSV

* implementacja testów jednostkowych

* przygotowanie dokumentacji projektu (README)

* Programowanie w języku Python 2025/2026
