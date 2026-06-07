"""Wypełnienie bazy przykładowymi danymi.

Odpowiednik komendy ``manage.py seed_data`` z wersji Django. Tworzy konto
demonstracyjne, kategorie, tagi oraz zestaw przykładowych przepisów.

Uruchomienie:  ``flask --app app seed``
"""

from __future__ import annotations

from extensions import db
from models import Category, Ingredient, Recipe, Tag, User
from utils import slugify

CATEGORIES = [
    ("Zupy", "Ciepłe i sycące zupy na każdą porę roku"),
    ("Dania główne", "Obiadowe dania główne"),
    ("Desery", "Słodkie wypieki i desery"),
    ("Sałatki", "Świeże i zdrowe sałatki"),
    ("Przekąski", "Szybkie przekąski na imprezę"),
]

TAGS = ["wegetariańskie", "szybkie", "fit", "tradycyjne", "bez glutenu"]

RECIPES = [
    {
        "title": "Rosół babci",
        "category": "Zupy",
        "description": "Klasyczny polski rosół z domowym makaronem.",
        "instructions": "1. Umyj mięso i warzywa.\n2. Włóż mięso do garnka z zimną wodą.\n3. Gotuj na wolnym ogniu przez 2 godziny.\n4. Dodaj warzywa i gotuj kolejną godzinę.\n5. Przecedź, dopraw do smaku.\n6. Podawaj z makaronem.",
        "prep_time": 20, "cook_time": 180, "servings": 8, "difficulty": "medium",
        "tags": ["tradycyjne"],
        "ingredients": [
            ("Kurczak", "1", "szt."), ("Marchew", "3", "szt."), ("Pietruszka", "2", "szt."),
            ("Seler", "1/2", "szt."), ("Cebula", "1", "szt."), ("Makaron", "200", "g"),
        ],
    },
    {
        "title": "Placki ziemniaczane",
        "category": "Dania główne",
        "description": "Chrupiące placki ziemniaczane z kwaśną śmietaną.",
        "instructions": "1. Obierz i zetrzyj ziemniaki na tarce.\n2. Odciśnij nadmiar wody.\n3. Dodaj jajko, mąkę i przyprawy.\n4. Smaż na rozgrzanym oleju z obu stron na złoty kolor.\n5. Podawaj z kwaśną śmietaną.",
        "prep_time": 20, "cook_time": 20, "servings": 4, "difficulty": "easy",
        "tags": ["tradycyjne", "wegetariańskie"],
        "ingredients": [
            ("Ziemniaki", "1", "kg"), ("Jajko", "1", "szt."), ("Mąka", "2", "łyżki"),
            ("Sól", "1", "szczypta"), ("Olej", "100", "ml"),
        ],
    },
    {
        "title": "Sernik na zimno",
        "category": "Desery",
        "description": "Kremowy sernik bez pieczenia, idealny na lato.",
        "instructions": "1. Pokrusz herbatniki i wymieszaj z masłem.\n2. Wyłóż masą dno formy i wstaw do lodówki.\n3. Wymieszaj ser z cukrem i śmietaną.\n4. Rozpuść żelatynę i dodaj do masy serowej.\n5. Wylej na spód z herbatników.\n6. Wstaw do lodówki na minimum 4 godziny.",
        "prep_time": 30, "cook_time": 0, "servings": 10, "difficulty": "easy",
        "tags": ["wegetariańskie"],
        "ingredients": [
            ("Ser mascarpone", "500", "g"), ("Herbatniki", "200", "g"), ("Masło", "100", "g"),
            ("Cukier", "100", "g"), ("Śmietana 30%", "200", "ml"), ("Żelatyna", "20", "g"),
        ],
    },
    {
        "title": "Sałatka grecka",
        "category": "Sałatki",
        "description": "Lekka sałatka z serem feta i oliwkami.",
        "instructions": "1. Pokrój pomidory, ogórek i paprykę w kostkę.\n2. Dodaj oliwki i pokrojoną fetę.\n3. Skrop oliwą i sokiem z cytryny.\n4. Dopraw oregano, solą i pieprzem.\n5. Delikatnie wymieszaj.",
        "prep_time": 15, "cook_time": 0, "servings": 4, "difficulty": "easy",
        "tags": ["wegetariańskie", "szybkie", "fit"],
        "ingredients": [
            ("Pomidory", "4", "szt."), ("Ogórek", "1", "szt."), ("Papryka", "1", "szt."),
            ("Ser feta", "200", "g"), ("Oliwki", "100", "g"), ("Oliwa z oliwek", "3", "łyżki"),
        ],
    },
    {
        "title": "Bruschetta z pomidorami",
        "category": "Przekąski",
        "description": "Włoska grzanka z pomidorami i bazylią.",
        "instructions": "1. Pokrój bagietkę w plastry i podpiecz na grillu.\n2. Pokrój pomidory w kosteczkę.\n3. Wymieszaj z oliwą, bazylią, solą i pieprzem.\n4. Natrzyj grzanki czosnkiem.\n5. Nałóż masę pomidorową na grzanki.",
        "prep_time": 10, "cook_time": 5, "servings": 6, "difficulty": "easy",
        "tags": ["wegetariańskie", "szybkie"],
        "ingredients": [
            ("Bagietka", "1", "szt."), ("Pomidory", "4", "szt."), ("Czosnek", "2", "ząbki"),
            ("Bazylia", "1", "pęczek"), ("Oliwa", "2", "łyżki"),
        ],
    },
    {
        "title": "Żurek na zakwasie",
        "category": "Zupy",
        "description": "Tradycyjny żurek z białą kiełbasą i jajkiem.",
        "instructions": "1. Przygotuj zakwas żytni (lub użyj gotowego).\n2. Ugotuj bulion z warzyw i białej kiełbasy.\n3. Dodaj zakwas do bulionu i zagotuj.\n4. Dopraw czosnkiem, majerankiem, solą i pieprzem.\n5. Pokrój kiełbasę na plastry.\n6. Ugotuj jajka na twardo i przekrój na pół.\n7. Podawaj z kiełbasą, jajkiem i chlebem.",
        "prep_time": 15, "cook_time": 45, "servings": 6, "difficulty": "medium",
        "tags": ["tradycyjne"],
        "ingredients": [
            ("Zakwas żytni", "500", "ml"), ("Biała kiełbasa", "400", "g"),
            ("Jajka", "4", "szt."), ("Czosnek", "4", "ząbki"),
            ("Majeranek", "1", "łyżeczka"), ("Marchew", "2", "szt."),
            ("Cebula", "1", "szt."), ("Liść laurowy", "2", "szt."),
        ],
    },
    {
        "title": "Spaghetti carbonara",
        "category": "Dania główne",
        "description": "Klasyczne włoskie spaghetti carbonara z guanciale.",
        "instructions": "1. Ugotuj makaron al dente w osolonej wodzie.\n2. Pokrój boczek na małe kawałki i podsmaż na patelni.\n3. Wymieszaj żółtka z tartym parmezanem i pecorino.\n4. Odcedź makaron, zachowując szklankę wody.\n5. Wrzuć makaron na patelnię z boczkiem (ogień wyłączony).\n6. Wlej masę jajeczno-serową i szybko mieszaj.\n7. Dodaj odrobinę wody z makaronu dla kremowej konsystencji.\n8. Dopraw świeżo mielonym pieprzem.",
        "prep_time": 10, "cook_time": 20, "servings": 4, "difficulty": "medium",
        "tags": ["szybkie"],
        "ingredients": [
            ("Spaghetti", "400", "g"), ("Boczek lub guanciale", "200", "g"),
            ("Żółtka", "4", "szt."), ("Parmezan", "100", "g"),
            ("Pecorino Romano", "50", "g"), ("Pieprz czarny", "1", "łyżeczka"),
        ],
    },
    {
        "title": "Pierogi ruskie",
        "category": "Dania główne",
        "description": "Domowe pierogi z nadzieniem z ziemniaków i twarogu.",
        "instructions": "1. Zagnieć ciasto z mąki, jajka, wody i szczypty soli.\n2. Ugotuj ziemniaki i rozgnieć je na purée.\n3. Wymieszaj ziemniaki z twarogiem i smażoną cebulą.\n4. Rozwałkuj ciasto i wycinaj kółka.\n5. Nakładaj farsz i zlepiaj pierogi.\n6. Gotuj w osolonej wodzie aż wypłyną.\n7. Podsmaż na maśle ze smażoną cebulą.",
        "prep_time": 60, "cook_time": 15, "servings": 6, "difficulty": "hard",
        "tags": ["tradycyjne", "wegetariańskie"],
        "ingredients": [
            ("Mąka pszenna", "500", "g"), ("Jajko", "1", "szt."),
            ("Ziemniaki", "500", "g"), ("Twaróg", "250", "g"),
            ("Cebula", "3", "szt."), ("Masło", "50", "g"),
        ],
    },
    {
        "title": "Tiramisu",
        "category": "Desery",
        "description": "Klasyczny włoski deser z mascarpone i kawą.",
        "instructions": "1. Zaparz mocną kawę espresso i ostudź.\n2. Oddziel żółtka od białek.\n3. Żółtka ubij z cukrem na puszysty krem.\n4. Dodaj mascarpone i delikatnie wymieszaj.\n5. Białka ubij na sztywną pianę i dodaj do masy.\n6. Maczaj biszkopty w kawie i układaj w naczyniu.\n7. Na warstwę biszkoptów nałóż krem mascarpone.\n8. Powtórz warstwy.\n9. Wstaw do lodówki na minimum 4 godziny.\n10. Posyp kakao przed podaniem.",
        "prep_time": 30, "cook_time": 0, "servings": 8, "difficulty": "medium",
        "tags": ["wegetariańskie"],
        "ingredients": [
            ("Mascarpone", "500", "g"), ("Jajka", "4", "szt."),
            ("Cukier", "100", "g"), ("Biszkopty", "300", "g"),
            ("Kawa espresso", "300", "ml"), ("Kakao", "2", "łyżki"),
        ],
    },
    {
        "title": "Sałatka Cezar z kurczakiem",
        "category": "Sałatki",
        "description": "Klasyczna sałatka Cezar z grillowanym kurczakiem i grzankami.",
        "instructions": "1. Grilluj pierś z kurczaka, dopraw solą i pieprzem.\n2. Porwij sałatę rzymską na kawałki.\n3. Przygotuj grzanki: pokrój bagietkę w kostkę i podsmaż na oliwie z czosnkiem.\n4. Sos: wymieszaj majonez, parmezan, sok z cytryny, czosnek i anchovis.\n5. Pokrój kurczaka w paski.\n6. Wymieszaj sałatę z sosem, dodaj grzanki i kurczaka.\n7. Posyp parmezanem.",
        "prep_time": 20, "cook_time": 15, "servings": 4, "difficulty": "easy",
        "tags": ["fit"],
        "ingredients": [
            ("Pierś z kurczaka", "400", "g"), ("Sałata rzymska", "2", "szt."),
            ("Bagietka", "1/2", "szt."), ("Parmezan", "80", "g"),
            ("Majonez", "3", "łyżki"), ("Cytryna", "1", "szt."),
        ],
    },
    {
        "title": "Hummus",
        "category": "Przekąski",
        "description": "Kremowy hummus z ciecierzycy z tahini.",
        "instructions": "1. Odcedź ciecierzycę z puszki (zachowaj płyn).\n2. Wrzuć ciecierzycę do blendera.\n3. Dodaj tahini, sok z cytryny, czosnek i oliwę.\n4. Blenduj, dodając płyn z ciecierzycy aż uzyskasz kremową konsystencję.\n5. Dopraw solą i kminkiem.\n6. Wyłóż na talerz, zrób wgłębienie i wlej oliwę.\n7. Posyp papryką wędzoną i podawaj z pitą.",
        "prep_time": 10, "cook_time": 0, "servings": 6, "difficulty": "easy",
        "tags": ["wegetariańskie", "szybkie", "fit", "bez glutenu"],
        "ingredients": [
            ("Ciecierzyca (puszka)", "400", "g"), ("Tahini", "3", "łyżki"),
            ("Cytryna", "1", "szt."), ("Czosnek", "2", "ząbki"),
            ("Oliwa z oliwek", "3", "łyżki"), ("Kminek", "1", "łyżeczka"),
        ],
    },
    {
        "title": "Zupa krem z dyni",
        "category": "Zupy",
        "description": "Rozgrzewająca zupa krem z dyni z imbirem i chili.",
        "instructions": "1. Obierz dynię i pokrój w kostkę.\n2. Podsmaż cebulę i czosnek na oliwie.\n3. Dodaj dynię, imbir i gotuj 2 minuty.\n4. Zalej bulionem i gotuj 20 minut aż dynia będzie miękka.\n5. Zblenduj na gładki krem.\n6. Dodaj mleczko kokosowe i dopraw.\n7. Podawaj z pestkami dyni i odrobiną chili.",
        "prep_time": 15, "cook_time": 30, "servings": 6, "difficulty": "easy",
        "tags": ["wegetariańskie", "fit", "bez glutenu"],
        "ingredients": [
            ("Dynia hokkaido", "1", "kg"), ("Cebula", "1", "szt."),
            ("Czosnek", "3", "ząbki"), ("Imbir", "3", "cm"),
            ("Bulion warzywny", "700", "ml"), ("Mleczko kokosowe", "200", "ml"),
        ],
    },
]


def seed_data() -> None:
    """Tworzy dane przykładowe (idempotentnie – pomija istniejące rekordy)."""
    # Konto demonstracyjne.
    user = db.session.scalar(db.select(User).filter_by(username="kucharz"))
    if user is None:
        user = User(
            username="kucharz",
            email="kucharz@example.com",
            bio="Pasjonat gotowania",
            favorite_cuisine="Polska",
        )
        user.set_password("kucharz123")
        db.session.add(user)
        db.session.flush()

    # Kategorie.
    categories: dict[str, Category] = {}
    for name, desc in CATEGORIES:
        cat = db.session.scalar(db.select(Category).filter_by(name=name))
        if cat is None:
            cat = Category(name=name, slug=slugify(name), description=desc)
            db.session.add(cat)
        categories[name] = cat

    # Tagi.
    tags: dict[str, Tag] = {}
    for name in TAGS:
        tag = db.session.scalar(db.select(Tag).filter_by(name=name))
        if tag is None:
            tag = Tag(name=name, slug=slugify(name))
            db.session.add(tag)
        tags[name] = tag

    db.session.flush()

    # Przepisy.
    for data in RECIPES:
        slug = slugify(data["title"])
        if db.session.scalar(db.select(Recipe).filter_by(slug=slug)):
            continue
        recipe = Recipe(
            title=data["title"],
            slug=slug,
            author_id=user.id,
            category_id=categories[data["category"]].id,
            description=data["description"],
            instructions=data["instructions"],
            prep_time=data["prep_time"],
            cook_time=data["cook_time"],
            servings=data["servings"],
            difficulty=data["difficulty"],
        )
        recipe.tags = [tags[t] for t in data["tags"]]
        for name, qty, unit in data["ingredients"]:
            recipe.ingredients.append(Ingredient(name=name, quantity=qty, unit=unit))
        db.session.add(recipe)

    db.session.commit()
