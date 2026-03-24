import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from ddgs import DDGS
from recipes.models import Recipe


class Command(BaseCommand):
    help = "Pobiera zdjęcia dla przepisów z internetu"

    def handle(self, *args, **kwargs):

        for recipe in Recipe.objects.all():

            if recipe.image:
                self.stdout.write(f"Pominięto (ma już zdjęcie): {recipe.title}")
                continue

            query = recipe.title + " food dish"

            try:
                with DDGS() as ddgs:
                    results = ddgs.images(query, max_results=1)

                    for r in results:
                        url = r["image"]

                        response = requests.get(url, timeout=10)

                        if response.status_code == 200:
                            filename = recipe.slug + ".jpg"

                            recipe.image.save(
                                filename,
                                ContentFile(response.content),
                                save=True
                            )

                            self.stdout.write(
                                self.style.SUCCESS(f"Dodano zdjęcie: {recipe.title}")
                            )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Błąd przy {recipe.title}: {str(e)}")
                )

        self.stdout.write(self.style.SUCCESS("Gotowe!"))