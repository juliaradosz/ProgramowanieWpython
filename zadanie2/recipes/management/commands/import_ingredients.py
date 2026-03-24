import csv
from django.core.management.base import BaseCommand
from recipes.models import Recipe, Ingredient


class Command(BaseCommand):
    help = "Import składników z pliku CSV"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        with open(csv_file, encoding="cp1250") as f:
            reader = csv.DictReader(f)

            count = 0

            for row in reader:
                recipe_title = row["recipe"]

                try:
                    recipe = Recipe.objects.get(title=recipe_title)

                    Ingredient.objects.create(
                        recipe=recipe,
                        name=row["name"],
                        quantity=row["quantity"],
                        unit=row["unit"],
                    )

                    count += 1
                    self.stdout.write(f"Dodano {row['name']} → {recipe_title}")

                except Recipe.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Nie znaleziono przepisu: {recipe_title}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS(f"Zaimportowano {count} składników"))