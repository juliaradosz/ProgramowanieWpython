"""
Komenda do wypełnienia bazy danych przykładowymi danymi.

Użycie: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from recipes.models import Category, Tag, Recipe, Ingredient, UserProfile


class Command(BaseCommand):
    help = 'Wypełnia bazę danych przykładowymi przepisami'

    def handle(self, *args, **options):
        # Tworzenie użytkownika
        user, created = User.objects.get_or_create(
            username='kucharz',
            defaults={'email': 'kucharz@example.com'},
        )
        if created:
            user.set_password('kucharz123')
            user.save()
            UserProfile.objects.create(user=user, bio='Pasjonat gotowania', favorite_cuisine='Polska')
            self.stdout.write('  Utworzono użytkownika: kucharz')

        # Kategorie
        categories_data = [
            ('Zupy', 'Ciepłe i sycące zupy na każdą porę roku'),
            ('Dania główne', 'Obiadowe dania główne'),
            ('Desery', 'Słodkie wypieki i desery'),
            ('Sałatki', 'Świeże i zdrowe sałatki'),
            ('Przekąski', 'Szybkie przekąski na imprezę'),
        ]
        categories = {}
        for name, desc in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={'slug': slugify(name), 'description': desc},
            )
            categories[name] = cat

        # Tagi
        tags_data = ['wegetariańskie', 'szybkie', 'fit', 'tradycyjne', 'bez glutenu']
        tags = {}
        for name in tags_data:
            tag, _ = Tag.objects.get_or_create(
                name=name,
                defaults={'slug': slugify(name)},
            )
            tags[name] = tag

        # Przepisy
        recipes_data = [
            {
                'title': 'Rosół babci',
                'category': 'Zupy',
                'description': 'Klasyczny polski rosół z domowym makaronem.',
                'instructions': '1. Umyj mięso i warzywa.\n2. Włóż mięso do garnka z zimną wodą.\n3. Gotuj na wolnym ogniu przez 2 godziny.\n4. Dodaj warzywa i gotuj kolejną godzinę.\n5. Przecedź, dopraw do smaku.\n6. Podawaj z makaronem.',
                'prep_time': 20, 'cook_time': 180, 'servings': 8, 'difficulty': 'medium',
                'tags': ['tradycyjne'],
                'ingredients': [
                    ('Kurczak', '1', 'szt.'), ('Marchew', '3', 'szt.'), ('Pietruszka', '2', 'szt.'),
                    ('Seler', '1/2', 'szt.'), ('Cebula', '1', 'szt.'), ('Makaron', '200', 'g'),
                ],
            },
            {
                'title': 'Placki ziemniaczane',
                'category': 'Dania główne',
                'description': 'Chrupiące placki ziemniaczane z kwaśną śmietaną.',
                'instructions': '1. Obierz i zetrzyj ziemniaki na tarce.\n2. Odciśnij nadmiar wody.\n3. Dodaj jajko, mąkę i przyprawy.\n4. Smaż na rozgrzanym oleju z obu stron na złoty kolor.\n5. Podawaj z kwaśną śmietaną.',
                'prep_time': 20, 'cook_time': 20, 'servings': 4, 'difficulty': 'easy',
                'tags': ['tradycyjne', 'wegetariańskie'],
                'ingredients': [
                    ('Ziemniaki', '1', 'kg'), ('Jajko', '1', 'szt.'), ('Mąka', '2', 'łyżki'),
                    ('Sól', '1', 'szczypta'), ('Olej', '100', 'ml'),
                ],
            },
            {
                'title': 'Sernik na zimno',
                'category': 'Desery',
                'description': 'Kremowy sernik bez pieczenia, idealny na lato.',
                'instructions': '1. Pokrusz herbatniki i wymieszaj z masłem.\n2. Wyłóż masą dno formy i wstaw do lodówki.\n3. Wymieszaj ser z cukrem i śmietaną.\n4. Rozpuść żelatynę i dodaj do masy serowej.\n5. Wylej na spód z herbatników.\n6. Wstaw do lodówki na minimum 4 godziny.',
                'prep_time': 30, 'cook_time': 0, 'servings': 10, 'difficulty': 'easy',
                'tags': ['wegetariańskie'],
                'ingredients': [
                    ('Ser mascarpone', '500', 'g'), ('Herbatniki', '200', 'g'), ('Masło', '100', 'g'),
                    ('Cukier', '100', 'g'), ('Śmietana 30%', '200', 'ml'), ('Żelatyna', '20', 'g'),
                ],
            },
            {
                'title': 'Sałatka grecka',
                'category': 'Sałatki',
                'description': 'Lekka sałatka z serem feta i oliwkami.',
                'instructions': '1. Pokrój pomidory, ogórek i paprykę w kostkę.\n2. Dodaj oliwki i pokrojoną fetę.\n3. Skrop oliwą i sokiem z cytryny.\n4. Dopraw oregano, solą i pieprzem.\n5. Delikatnie wymieszaj.',
                'prep_time': 15, 'cook_time': 0, 'servings': 4, 'difficulty': 'easy',
                'tags': ['wegetariańskie', 'szybkie', 'fit'],
                'ingredients': [
                    ('Pomidory', '4', 'szt.'), ('Ogórek', '1', 'szt.'), ('Papryka', '1', 'szt.'),
                    ('Ser feta', '200', 'g'), ('Oliwki', '100', 'g'), ('Oliwa z oliwek', '3', 'łyżki'),
                ],
            },
            {
                'title': 'Bruschetta z pomidorami',
                'category': 'Przekąski',
                'description': 'Włoska grzanka z pomidorami i bazylią.',
                'instructions': '1. Pokrój bagietkę w plastry i podpiecz na grillu.\n2. Pokrój pomidory w kosteczkę.\n3. Wymieszaj z oliwą, bazylią, solą i pieprzem.\n4. Natrzyj grzanki czosnkiem.\n5. Nałóż masę pomidorową na grzanki.',
                'prep_time': 10, 'cook_time': 5, 'servings': 6, 'difficulty': 'easy',
                'tags': ['wegetariańskie', 'szybkie'],
                'ingredients': [
                    ('Bagietka', '1', 'szt.'), ('Pomidory', '4', 'szt.'), ('Czosnek', '2', 'ząbki'),
                    ('Bazylia', '1', 'pęczek'), ('Oliwa', '2', 'łyżki'),
                ],
            },
            {
                'title': 'Żurek na zakwasie',
                'category': 'Zupy',
                'description': 'Tradycyjny żurek z białą kiełbasą i jajkiem.',
                'instructions': '1. Przygotuj zakwas żytni (lub użyj gotowego).\n2. Ugotuj bulion z warzyw i białej kiełbasy.\n3. Dodaj zakwas do bulionu i zagotuj.\n4. Dopraw czosnkiem, majerankiem, solą i pieprzem.\n5. Pokrój kiełbasę na plastry.\n6. Ugotuj jajka na twardo i przekrój na pół.\n7. Podawaj z kiełbasą, jajkiem i chlebem.',
                'prep_time': 15, 'cook_time': 45, 'servings': 6, 'difficulty': 'medium',
                'tags': ['tradycyjne'],
                'ingredients': [
                    ('Zakwas żytni', '500', 'ml'), ('Biała kiełbasa', '400', 'g'),
                    ('Jajka', '4', 'szt.'), ('Czosnek', '4', 'ząbki'),
                    ('Majeranek', '1', 'łyżeczka'), ('Marchew', '2', 'szt.'),
                    ('Cebula', '1', 'szt.'), ('Liść laurowy', '2', 'szt.'),
                ],
            },
            {
                'title': 'Krem z pieczarek',
                'category': 'Zupy',
                'description': 'Aksamitny krem z pieczarek z grzankami.',
                'instructions': '1. Pokrój pieczarki i cebulę.\n2. Podsmaż cebulę na maśle aż się zeszkli.\n3. Dodaj pieczarki i smaż 10 minut.\n4. Zalej bulionem i gotuj 15 minut.\n5. Zblenduj na gładki krem.\n6. Dodaj śmietankę, dopraw solą i pieprzem.\n7. Podawaj z grzankami i natką pietruszki.',
                'prep_time': 10, 'cook_time': 30, 'servings': 4, 'difficulty': 'easy',
                'tags': ['wegetariańskie'],
                'ingredients': [
                    ('Pieczarki', '500', 'g'), ('Cebula', '1', 'szt.'),
                    ('Masło', '30', 'g'), ('Bulion warzywny', '500', 'ml'),
                    ('Śmietanka 18%', '200', 'ml'), ('Chleb na grzanki', '4', 'kromki'),
                ],
            },
            {
                'title': 'Spaghetti carbonara',
                'category': 'Dania główne',
                'description': 'Klasyczne włoskie spaghetti carbonara z guanciale.',
                'instructions': '1. Ugotuj makaron al dente w osolonej wodzie.\n2. Pokrój boczek na małe kawałki i podsmaż na patelni.\n3. Wymieszaj żółtka z tartym parmezanem i pecorino.\n4. Odcedź makaron, zachowując szklankę wody.\n5. Wrzuć makaron na patelnię z boczkiem (ogień wyłączony).\n6. Wlej masę jajeczno-serową i szybko mieszaj.\n7. Dodaj odrobinę wody z makaronu dla kremowej konsystencji.\n8. Dopraw świeżo mielonym pieprzem.',
                'prep_time': 10, 'cook_time': 20, 'servings': 4, 'difficulty': 'medium',
                'tags': ['szybkie'],
                'ingredients': [
                    ('Spaghetti', '400', 'g'), ('Boczek lub guanciale', '200', 'g'),
                    ('Żółtka', '4', 'szt.'), ('Parmezan', '100', 'g'),
                    ('Pecorino Romano', '50', 'g'), ('Pieprz czarny', '1', 'łyżeczka'),
                ],
            },
            {
                'title': 'Pierogi ruskie',
                'category': 'Dania główne',
                'description': 'Domowe pierogi z nadzieniem z ziemniaków i twarogu.',
                'instructions': '1. Zagnieć ciasto z mąki, jajka, wody i szczypty soli.\n2. Ugotuj ziemniaki i rozgnieć je na purée.\n3. Wymieszaj ziemniaki z twarogiem i smażoną cebulą.\n4. Rozwałkuj ciasto i wycinaj kółka.\n5. Nakładaj farsz i zlepiaj pierogi.\n6. Gotuj w osolonej wodzie aż wypłyną.\n7. Podsmaż na maśle ze smażoną cebulą.',
                'prep_time': 60, 'cook_time': 15, 'servings': 6, 'difficulty': 'hard',
                'tags': ['tradycyjne', 'wegetariańskie'],
                'ingredients': [
                    ('Mąka pszenna', '500', 'g'), ('Jajko', '1', 'szt.'),
                    ('Ziemniaki', '500', 'g'), ('Twaróg', '250', 'g'),
                    ('Cebula', '3', 'szt.'), ('Masło', '50', 'g'),
                    ('Sól', '1', 'łyżeczka'), ('Pieprz', '1', 'szczypta'),
                ],
            },
            {
                'title': 'Kurczak tikka masala',
                'category': 'Dania główne',
                'description': 'Aromatyczne indyjskie danie z kurczakiem w sosie pomidorowym.',
                'instructions': '1. Zamarynuj kawałki kurczaka w jogurcie z przyprawami (kurkuma, garam masala, chili) na 2 godziny.\n2. Podsmaż kurczaka na patelni na złoty kolor.\n3. Na osobnej patelni podsmaż cebulę, czosnek i imbir.\n4. Dodaj pomidory z puszki i gotuj 15 minut.\n5. Dodaj garam masala, kurkumę i paprykę.\n6. Wrzuć kurczaka do sosu i gotuj 10 minut.\n7. Wlej śmietankę kokosową i wymieszaj.\n8. Podawaj z ryżem basmati i kolendrą.',
                'prep_time': 30, 'cook_time': 40, 'servings': 4, 'difficulty': 'medium',
                'tags': ['bez glutenu'],
                'ingredients': [
                    ('Pierś z kurczaka', '600', 'g'), ('Jogurt naturalny', '150', 'ml'),
                    ('Pomidory krojone (puszka)', '400', 'g'), ('Cebula', '2', 'szt.'),
                    ('Czosnek', '4', 'ząbki'), ('Imbir', '3', 'cm'),
                    ('Garam masala', '2', 'łyżki'), ('Kurkuma', '1', 'łyżeczka'),
                    ('Śmietanka kokosowa', '200', 'ml'), ('Ryż basmati', '300', 'g'),
                ],
            },
            {
                'title': 'Tiramisu',
                'category': 'Desery',
                'description': 'Klasyczny włoski deser z mascarpone i kawą.',
                'instructions': '1. Zaparz mocną kawę espresso i ostudź.\n2. Oddziel żółtka od białek.\n3. Żółtka ubij z cukrem na puszysty krem.\n4. Dodaj mascarpone i delikatnie wymieszaj.\n5. Białka ubij na sztywną pianę i dodaj do masy.\n6. Maczaj biszkopty w kawie i układaj w naczyniu.\n7. Na warstwę biszkoptów nałóż krem mascarpone.\n8. Powtórz warstwy.\n9. Wstaw do lodówki na minimum 4 godziny.\n10. Posyp kakao przed podaniem.',
                'prep_time': 30, 'cook_time': 0, 'servings': 8, 'difficulty': 'medium',
                'tags': ['wegetariańskie'],
                'ingredients': [
                    ('Mascarpone', '500', 'g'), ('Jajka', '4', 'szt.'),
                    ('Cukier', '100', 'g'), ('Biszkopty', '300', 'g'),
                    ('Kawa espresso', '300', 'ml'), ('Kakao', '2', 'łyżki'),
                    ('Amaretto (opcjonalnie)', '2', 'łyżki'),
                ],
            },
            {
                'title': 'Szarlotka',
                'category': 'Desery',
                'description': 'Tradycyjna polska szarlotka z kruchym ciastem.',
                'instructions': '1. Wymieszaj mąkę z cukrem pudrem i proszkiem do pieczenia.\n2. Dodaj pokrojone zimne masło i posiekaj nożem na kruszonkę.\n3. Dodaj żółtka i zagnieć ciasto.\n4. Podziel ciasto na dwie części i schłodź.\n5. Obierz jabłka, pokrój w plastry i podsmaż z cynamonem i cukrem.\n6. Rozwałkuj jedną część ciasta i wyłóż formę.\n7. Nałóż jabłka, przykryj drugą częścią ciasta.\n8. Piecz 45 minut w 180°C.\n9. Posyp cukrem pudrem po ostygnięciu.',
                'prep_time': 30, 'cook_time': 45, 'servings': 10, 'difficulty': 'medium',
                'tags': ['tradycyjne', 'wegetariańskie'],
                'ingredients': [
                    ('Mąka pszenna', '400', 'g'), ('Masło', '250', 'g'),
                    ('Cukier puder', '150', 'g'), ('Żółtka', '4', 'szt.'),
                    ('Jabłka', '1.5', 'kg'), ('Cynamon', '2', 'łyżeczki'),
                    ('Proszek do pieczenia', '1', 'łyżeczka'),
                ],
            },
            {
                'title': 'Sałatka Cezar z kurczakiem',
                'category': 'Sałatki',
                'description': 'Klasyczna sałatka Cezar z grillowanym kurczakiem i grzankami.',
                'instructions': '1. Grilluj pierś z kurczaka, dopraw solą i pieprzem.\n2. Porwij sałatę rzymską na kawałki.\n3. Przygotuj grzanki: pokrój bagietkę w kostkę i podsmaż na oliwie z czosnkiem.\n4. Sos: wymieszaj majonez, parmezan, sok z cytryny, czosnek i anchovis.\n5. Pokrój kurczaka w paski.\n6. Wymieszaj sałatę z sosem, dodaj grzanki i kurczaka.\n7. Posyp parmezanem.',
                'prep_time': 20, 'cook_time': 15, 'servings': 4, 'difficulty': 'easy',
                'tags': ['fit'],
                'ingredients': [
                    ('Pierś z kurczaka', '400', 'g'), ('Sałata rzymska', '2', 'szt.'),
                    ('Bagietka', '1/2', 'szt.'), ('Parmezan', '80', 'g'),
                    ('Majonez', '3', 'łyżki'), ('Cytryna', '1', 'szt.'),
                    ('Czosnek', '2', 'ząbki'), ('Anchovis', '4', 'szt.'),
                ],
            },
            {
                'title': 'Sałatka z awokado i krewetkami',
                'category': 'Sałatki',
                'description': 'Lekka sałatka z awokado, krewetkami i limonką.',
                'instructions': '1. Obierz i pokrój awokado w kostkę.\n2. Podsmaż krewetki na oliwie z czosnkiem 3-4 minuty.\n3. Pokrój pomidorki koktajlowe na połówki.\n4. Pokrój czerwoną cebulę w cienkie piórka.\n5. Wymieszaj wszystko w misce.\n6. Skrop sokiem z limonki i oliwą.\n7. Dopraw solą, pieprzem i kolendrą.',
                'prep_time': 15, 'cook_time': 5, 'servings': 2, 'difficulty': 'easy',
                'tags': ['szybkie', 'fit', 'bez glutenu'],
                'ingredients': [
                    ('Krewetki', '200', 'g'), ('Awokado', '2', 'szt.'),
                    ('Pomidorki koktajlowe', '150', 'g'), ('Czerwona cebula', '1/2', 'szt.'),
                    ('Limonka', '1', 'szt.'), ('Kolendra', '1', 'pęczek'),
                    ('Oliwa', '2', 'łyżki'), ('Czosnek', '1', 'ząbek'),
                ],
            },
            {
                'title': 'Hummus',
                'category': 'Przekąski',
                'description': 'Kremowy hummus z ciecierzycy z tahini.',
                'instructions': '1. Odcedź ciecierkę z puszki (zachowaj płyn).\n2. Wrzuć ciecierkę do blendera.\n3. Dodaj tahini, sok z cytryny, czosnek i oliwę.\n4. Blenduj, dodając płyn z ciecierzycy aż uzyskasz kremową konsystencję.\n5. Dopraw solą i kminkiem.\n6. Wyłóż na talerz, zrób wgłębienie i wlej oliwę.\n7. Posyp papryką wędzoną i podawaj z pitą.',
                'prep_time': 10, 'cook_time': 0, 'servings': 6, 'difficulty': 'easy',
                'tags': ['wegetariańskie', 'szybkie', 'fit', 'bez glutenu'],
                'ingredients': [
                    ('Ciecierzyca (puszka)', '400', 'g'), ('Tahini', '3', 'łyżki'),
                    ('Cytryna', '1', 'szt.'), ('Czosnek', '2', 'ząbki'),
                    ('Oliwa z oliwek', '3', 'łyżki'), ('Kminek', '1', 'łyżeczka'),
                    ('Papryka wędzona', '1', 'szczypta'),
                ],
            },
            {
                'title': 'Guacamole',
                'category': 'Przekąski',
                'description': 'Meksykański dip z awokado z nachos.',
                'instructions': '1. Przekrój awokado, wyjmij pestkę i wyłóż miąższ do miski.\n2. Rozgnieć widelcem (nie za gładko).\n3. Dodaj posiekany pomidor (bez pestek).\n4. Dodaj drobno posiekaną cebulę i chili.\n5. Wyciśnij sok z limonki.\n6. Dodaj posiekaną kolendrę.\n7. Dopraw solą.\n8. Podawaj od razu z nachos lub warzywami.',
                'prep_time': 10, 'cook_time': 0, 'servings': 4, 'difficulty': 'easy',
                'tags': ['wegetariańskie', 'szybkie', 'fit', 'bez glutenu'],
                'ingredients': [
                    ('Awokado', '3', 'szt.'), ('Pomidor', '1', 'szt.'),
                    ('Czerwona cebula', '1/2', 'szt.'), ('Chili jalapeño', '1', 'szt.'),
                    ('Limonka', '1', 'szt.'), ('Kolendra', '1', 'pęczek'),
                    ('Sól', '1', 'szczypta'),
                ],
            },
            {
                'title': 'Bigos staropolski',
                'category': 'Dania główne',
                'description': 'Tradycyjny polski bigos z kapustą kiszoną i mięsem.',
                'instructions': '1. Pokrój kapustę kiszoną i białą na paski.\n2. Pokrój mięsa (kiełbasę, boczek, łopatkę) w kostkę.\n3. Podsmaż mięso na patelni.\n4. W dużym garnku połóż warstwami kapustę i mięso.\n5. Dodaj suszone grzyby (namoczone wcześniej), śliwki, liść laurowy i ziele angielskie.\n6. Zalej bulionem i gotuj na wolnym ogniu 2-3 godziny.\n7. Dopraw solą, pieprzem i cukrem.\n8. Bigos smakuje najlepiej odgrzewany następnego dnia.',
                'prep_time': 30, 'cook_time': 180, 'servings': 10, 'difficulty': 'hard',
                'tags': ['tradycyjne'],
                'ingredients': [
                    ('Kapusta kiszona', '500', 'g'), ('Kapusta biała', '500', 'g'),
                    ('Kiełbasa myśliwska', '300', 'g'), ('Boczek wędzony', '200', 'g'),
                    ('Łopatka wieprzowa', '300', 'g'), ('Grzyby suszone', '30', 'g'),
                    ('Śliwki suszone', '100', 'g'), ('Liść laurowy', '3', 'szt.'),
                    ('Ziele angielskie', '5', 'szt.'),
                ],
            },
            {
                'title': 'Pancakes amerykańskie',
                'category': 'Desery',
                'description': 'Puszyste pancakes z syropem klonowym i owocami.',
                'instructions': '1. Wymieszaj mąkę, proszek do pieczenia, cukier i sól.\n2. W osobnej misce wymieszaj mleko, jajko i roztopione masło.\n3. Połącz składniki suche z mokrymi (nie mieszaj za długo).\n4. Rozgrzej patelnię na średnim ogniu i lekko nasmaruj masłem.\n5. Nakładaj ciasto porcjami (ok. 1/4 szklanki).\n6. Smaż aż pojawią się bąbelki, obróć i smaż drugą stronę.\n7. Podawaj z syropem klonowym, masłem i owocami.',
                'prep_time': 10, 'cook_time': 15, 'servings': 4, 'difficulty': 'easy',
                'tags': ['wegetariańskie', 'szybkie'],
                'ingredients': [
                    ('Mąka pszenna', '200', 'g'), ('Mleko', '250', 'ml'),
                    ('Jajko', '1', 'szt.'), ('Masło', '30', 'g'),
                    ('Cukier', '2', 'łyżki'), ('Proszek do pieczenia', '2', 'łyżeczki'),
                    ('Syrop klonowy', '100', 'ml'), ('Owoce (borówki/banany)', '150', 'g'),
                ],
            },
            {
                'title': 'Zupa krem z dyni',
                'category': 'Zupy',
                'description': 'Rozgrzewająca zupa krem z dyni z imbirem i chili.',
                'instructions': '1. Obierz dynię i pokrój w kostkę.\n2. Podsmaż cebulę i czosnek na oliwie.\n3. Dodaj dynię, imbir i gotuj 2 minuty.\n4. Zalej bulionem i gotuj 20 minut aż dynia będzie miękka.\n5. Zblenduj na gładki krem.\n6. Dodaj mleczko kokosowe i dopraw.\n7. Podawaj z pestkami dyni i odrobiną chili.',
                'prep_time': 15, 'cook_time': 30, 'servings': 6, 'difficulty': 'easy',
                'tags': ['wegetariańskie', 'fit', 'bez glutenu'],
                'ingredients': [
                    ('Dynia hokkaido', '1', 'kg'), ('Cebula', '1', 'szt.'),
                    ('Czosnek', '3', 'ząbki'), ('Imbir', '3', 'cm'),
                    ('Bulion warzywny', '700', 'ml'), ('Mleczko kokosowe', '200', 'ml'),
                    ('Pestki dyni', '2', 'łyżki'), ('Chili', '1', 'szczypta'),
                ],
            },
        ]

        for data in recipes_data:
            slug = slugify(data['title'])
            if Recipe.objects.filter(slug=slug).exists():
                self.stdout.write(f'  Przepis "{data["title"]}" już istnieje, pomijam.')
                continue

            recipe = Recipe.objects.create(
                title=data['title'],
                slug=slug,
                author=user,
                category=categories[data['category']],
                description=data['description'],
                instructions=data['instructions'],
                prep_time=data['prep_time'],
                cook_time=data['cook_time'],
                servings=data['servings'],
                difficulty=data['difficulty'],
            )
            for tag_name in data['tags']:
                recipe.tags.add(tags[tag_name])

            for name, qty, unit in data['ingredients']:
                Ingredient.objects.create(recipe=recipe, name=name, quantity=qty, unit=unit)

            self.stdout.write(f'  Dodano: {data["title"]}')

        self.stdout.write(self.style.SUCCESS('Baza danych została wypełniona przykładowymi danymi!'))
