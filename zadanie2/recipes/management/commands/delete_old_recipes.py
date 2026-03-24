"""
Komenda do usuwania starych, nieopublikowanych przepisów.

Użycie: python manage.py delete_old_recipes --days 30
"""
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from recipes.models import Recipe


class Command(BaseCommand):
    help = 'Usuwa nieopublikowane przepisy starsze niż podana liczba dni'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Liczba dni (domyślnie 30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Tylko pokaż co zostałoby usunięte, bez usuwania',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)

        old_recipes = Recipe.objects.filter(
            is_published=False,
            updated_at__lt=cutoff_date,
        )

        count = old_recipes.count()

        if count == 0:
            self.stdout.write('Brak przepisów do usunięcia.')
            return

        for recipe in old_recipes:
            self.stdout.write(
                f'  {"[DRY RUN] " if dry_run else ""}'
                f'Usuwanie: "{recipe.title}" (ostatnia edycja: {recipe.updated_at.strftime("%d.%m.%Y")})'
            )

        if not dry_run:
            old_recipes.delete()
            self.stdout.write(self.style.SUCCESS(f'Usunięto {count} nieopublikowanych przepisów.'))
        else:
            self.stdout.write(self.style.WARNING(f'[DRY RUN] Znaleziono {count} przepisów do usunięcia.'))
