from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class UserProfile(models.Model):
    """Profil użytkownika z dodatkowymi informacjami."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, verbose_name='O mnie')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Zdjęcie profilowe')
    favorite_cuisine = models.CharField(max_length=100, blank=True, verbose_name='Ulubiona kuchnia')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Profil użytkownika'
        verbose_name_plural = 'Profile użytkowników'

    def __str__(self):
        return f'Profil: {self.user.username}'


class Category(models.Model):
    """Kategoria przepisów (np. Zupy, Desery, Dania główne)."""
    name = models.CharField(max_length=100, unique=True, verbose_name='Nazwa')
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, verbose_name='Opis')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Zdjęcie')

    class Meta:
        verbose_name = 'Kategoria'
        verbose_name_plural = 'Kategorie'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipes:category_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    """Tag do oznaczania przepisów (np. wegetariańskie, szybkie, fit)."""
    name = models.CharField(max_length=50, unique=True, verbose_name='Nazwa')
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tagi'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Przepis kulinarny."""
    DIFFICULTY_CHOICES = [
        ('easy', 'Łatwy'),
        ('medium', 'Średni'),
        ('hard', 'Trudny'),
    ]

    title = models.CharField(max_length=200, verbose_name='Tytuł')
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', verbose_name='Autor')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='recipes', verbose_name='Kategoria')
    tags = models.ManyToManyField(Tag, blank=True, related_name='recipes', verbose_name='Tagi')
    description = models.TextField(verbose_name='Opis')
    instructions = models.TextField(verbose_name='Instrukcje przygotowania')
    prep_time = models.PositiveIntegerField(verbose_name='Czas przygotowania (min)')
    cook_time = models.PositiveIntegerField(verbose_name='Czas gotowania (min)')
    servings = models.PositiveIntegerField(default=4, verbose_name='Liczba porcji')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium', verbose_name='Poziom trudności')
    image = models.ImageField(upload_to='recipes/', blank=True, null=True, verbose_name='Zdjęcie')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True, verbose_name='Opublikowany')

    class Meta:
        verbose_name = 'Przepis'
        verbose_name_plural = 'Przepisy'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recipes:recipe_detail', kwargs={'slug': self.slug})

    @property
    def total_time(self):
        return self.prep_time + self.cook_time

    @property
    def average_rating(self):
        ratings = self.comments.aggregate(avg=models.Avg('rating'))
        return ratings['avg'] or 0


class Ingredient(models.Model):
    """Składnik przepisu."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients', verbose_name='Przepis')
    name = models.CharField(max_length=200, verbose_name='Nazwa')
    quantity = models.CharField(max_length=50, verbose_name='Ilość')
    unit = models.CharField(max_length=50, blank=True, verbose_name='Jednostka')

    class Meta:
        verbose_name = 'Składnik'
        verbose_name_plural = 'Składniki'

    def __str__(self):
        if self.unit:
            return f'{self.quantity} {self.unit} - {self.name}'
        return f'{self.quantity} - {self.name}'


class Comment(models.Model):
    """Komentarz do przepisu."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments', verbose_name='Przepis')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='Autor')
    content = models.TextField(verbose_name='Treść')
    rating = models.PositiveIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name='Ocena'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Komentarz'
        verbose_name_plural = 'Komentarze'
        ordering = ['-created_at']
        unique_together = ['recipe', 'author']

    def __str__(self):
        return f'Komentarz {self.author.username} do {self.recipe.title}'
    
class Favorite(models.Model):
    """Ulubione przepisy użytkownika."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'recipe']
        verbose_name = 'Ulubiony przepis'
        verbose_name_plural = 'Ulubione przepisy'

    def __str__(self):
        return f'{self.user.username} ❤️ {self.recipe.title}'