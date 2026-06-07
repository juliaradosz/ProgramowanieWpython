from django.test import TestCase
from django.contrib.auth.models import User
from recipes.models import Recipe, Category


class RecipeModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="test123"
        )

        self.category = Category.objects.create(
            name="Zupy",
            slug="zupy"
        )

    def create_recipe(self, slug="testowa-zupa"):
        return Recipe.objects.create(
            title="Testowa zupa",
            slug=slug,
            author=self.user,
            category=self.category,
            description="Opis",
            instructions="Instrukcja",
            prep_time=10,
            cook_time=20,
            servings=2,
            difficulty="easy",
            is_published=True
        )

    def test_recipe_creation(self):
        recipe = self.create_recipe()
        self.assertEqual(recipe.title, "Testowa zupa")

    def test_recipe_author(self):
        recipe = self.create_recipe()
        self.assertEqual(recipe.author.username, "testuser")

    def test_recipe_category(self):
        recipe = self.create_recipe()
        self.assertEqual(recipe.category.name, "Zupy")

    def test_recipe_slug(self):
        recipe = self.create_recipe()
        self.assertEqual(recipe.slug, "testowa-zupa")

    def test_recipe_description(self):
        recipe = self.create_recipe()
        self.assertTrue(recipe.description)

    def test_recipe_instructions(self):
        recipe = self.create_recipe()
        self.assertTrue(recipe.instructions)

    def test_recipe_prep_time(self):
        recipe = self.create_recipe()
        self.assertEqual(recipe.prep_time, 10)

    def test_recipe_cook_time(self):
        recipe = self.create_recipe()
        self.assertEqual(recipe.cook_time, 20)

    def test_recipe_servings(self):
        recipe = self.create_recipe()
        self.assertEqual(recipe.servings, 2)

    def test_recipe_difficulty(self):
        recipe = self.create_recipe()
        self.assertEqual(recipe.difficulty, "easy")

    def test_category_creation(self):
        self.assertEqual(Category.objects.count(), 1)

    def test_category_slug(self):
        self.assertEqual(self.category.slug, "zupy")

    def test_recipe_str(self):
        recipe = self.create_recipe()
        self.assertEqual(str(recipe), recipe.title)

    def test_recipe_count(self):
        self.create_recipe()
        self.assertEqual(Recipe.objects.count(), 1)

    def test_multiple_recipes(self):
        self.create_recipe("zupa1")
        self.create_recipe("zupa2")
        self.assertEqual(Recipe.objects.count(), 2)