"""
Komenda do importu przepisów z pliku CSV.

Użycie: python manage.py import_recipes plik.csv

Format CSV: title,category,description,instructions,prep_time,cook_time,servings,difficulty
"""
import csv
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils.text import slugify
from recipes.models import Recipe, Category


class Command(BaseCommand):
    help = 'Importuje przepisy z pliku CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ścieżka do pliku CSV')
        parser.add_argument(
            '--author',
            type=str,
            default='admin',
            help='Nazwa użytkownika autora przepisów (domyślnie: admin)',
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        author_username = options['author']

        # Szukamy autora
        author = User.objects.filter(username=author_username).first()

        # Jeśli nie ma takiego użytkownika — bierzemy pierwszego z bazy
        if not author:
            author = User.objects.first()

        if not author:
            raise CommandError("Brak użytkowników w bazie danych.")

        try:
            with open(csv_file, 'r', encoding='cp1250') as f:
                reader = csv.DictReader(f)
                count = 0

                for row in reader:

                    category, _ = Category.objects.get_or_create(
                        name=row['category'],
                        defaults={'slug': slugify(row['category'])},
                    )

                    slug = slugify(row['title'])
                    counter = 1
                    base_slug = slug

                    while Recipe.objects.filter(slug=slug).exists():
                        slug = f'{base_slug}-{counter}'
                        counter += 1

                    Recipe.objects.create(
                        title=row['title'],
                        slug=slug,
                        author=author,
                        category=category,
                        description=row.get('description', ''),
                        instructions=row.get('instructions', ''),
                        prep_time=int(row.get('prep_time', 15)),
                        cook_time=int(row.get('cook_time', 30)),
                        servings=int(row.get('servings', 4)),
                        difficulty=row.get('difficulty', 'medium'),
                    )

                    count += 1
                    self.stdout.write(f'  Zaimportowano: {row["title"]}')

        except FileNotFoundError:
            raise CommandError(f'Plik "{csv_file}" nie został znaleziony.')

        self.stdout.write(self.style.SUCCESS(f'Zaimportowano {count} przepisów.'))