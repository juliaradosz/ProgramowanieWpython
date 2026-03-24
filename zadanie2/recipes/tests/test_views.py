from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from recipes.models import Recipe, Category


class RecipeViewsTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="test123"
        )

        self.category = Category.objects.create(
            name="Zupy",
            slug="zupy"
        )

        self.recipe = Recipe.objects.create(
            title="Testowa zupa",
            slug="testowa-zupa",
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

    def test_home_page(self):
        response = self.client.get(reverse("recipes:home"))
        self.assertEqual(response.status_code, 200)

    def test_recipe_list(self):
        response = self.client.get(reverse("recipes:recipe_list"))
        self.assertEqual(response.status_code, 200)

    def test_recipe_detail(self):
        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.recipe.slug])
        )
        self.assertEqual(response.status_code, 200)

    def test_recipe_title_visible(self):
        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.recipe.slug])
        )
        self.assertContains(response, "Testowa zupa")

    def test_category_list(self):
        response = self.client.get(reverse("recipes:category_list"))
        self.assertEqual(response.status_code, 200)

    def test_category_detail(self):
        response = self.client.get(
            reverse("recipes:category_detail", args=[self.category.slug])
        )
        self.assertEqual(response.status_code, 200)

    def test_search_page(self):
        response = self.client.get(reverse("recipes:search"))
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get(reverse("recipes:login"))
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.client.get(reverse("recipes:register"))
        self.assertEqual(response.status_code, 200)

    def test_profile_page(self):
        response = self.client.get(
            reverse("recipes:profile", args=[self.user.username])
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_recipe(self):
        response = self.client.get("/przepis/nie-istnieje/")
        self.assertEqual(response.status_code, 404)

    def test_home_template(self):
        response = self.client.get(reverse("recipes:home"))
        self.assertTemplateUsed(response, "recipes/home.html")

    def test_category_template(self):
        response = self.client.get(reverse("recipes:category_list"))
        self.assertTemplateUsed(response, "recipes/category_list.html")

    def test_recipe_template(self):
        response = self.client.get(
            reverse("recipes:recipe_detail", args=[self.recipe.slug])
        )
        self.assertTemplateUsed(response, "recipes/recipe_detail.html")

    def test_home_context(self):
        response = self.client.get(reverse("recipes:home"))
        self.assertIn("latest_recipes", response.context)