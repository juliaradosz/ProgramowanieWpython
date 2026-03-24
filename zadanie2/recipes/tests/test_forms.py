from django.test import TestCase
from recipes.forms import RecipeForm


class RecipeFormTests(TestCase):

    def get_valid_data(self):
        return {
            "title": "Testowy przepis",
            "description": "Opis przepisu",
            "instructions": "Instrukcja przygotowania",
            "prep_time": 10,
            "cook_time": 20,
            "servings": 2,
            "difficulty": "easy",
            "is_published": True
        }

    def test_form_valid(self):
        form = RecipeForm(data=self.get_valid_data())
        self.assertIsNotNone(form)

    def test_title_required(self):
        data = self.get_valid_data()
        data["title"] = ""
        form = RecipeForm(data=data)
        self.assertFalse(form.is_valid())

    def test_description_required(self):
        data = self.get_valid_data()
        data["description"] = ""
        form = RecipeForm(data=data)
        self.assertFalse(form.is_valid())

    def test_instructions_required(self):
        data = self.get_valid_data()
        data["instructions"] = ""
        form = RecipeForm(data=data)
        self.assertFalse(form.is_valid())

    def test_prep_time_positive(self):
        data = self.get_valid_data()
        data["prep_time"] = 15
        form = RecipeForm(data=data)
        self.assertIsNotNone(form)

    def test_cook_time_positive(self):
        data = self.get_valid_data()
        data["cook_time"] = 25
        form = RecipeForm(data=data)
        self.assertIsNotNone(form)

    def test_servings_positive(self):
        data = self.get_valid_data()
        data["servings"] = 4
        form = RecipeForm(data=data)
        self.assertIsNotNone(form)

    def test_difficulty_easy(self):
        data = self.get_valid_data()
        data["difficulty"] = "easy"
        form = RecipeForm(data=data)
        self.assertIsNotNone(form)

    def test_difficulty_medium(self):
        data = self.get_valid_data()
        data["difficulty"] = "medium"
        form = RecipeForm(data=data)
        self.assertIsNotNone(form)

    def test_difficulty_hard(self):
        data = self.get_valid_data()
        data["difficulty"] = "hard"
        form = RecipeForm(data=data)
        self.assertIsNotNone(form)

    def test_title_length(self):
        data = self.get_valid_data()
        data["title"] = "A" * 50
        form = RecipeForm(data=data)
        self.assertIsNotNone(form)

    def test_description_length(self):
        data = self.get_valid_data()
        data["description"] = "Opis " * 20
        form = RecipeForm(data=data)
        self.assertIsNotNone(form)

    def test_instruction_length(self):
        data = self.get_valid_data()
        data["instructions"] = "Instrukcja " * 20
        form = RecipeForm(data=data)
        self.assertIsNotNone(form)

    def test_zero_servings(self):
        data = self.get_valid_data()
        data["servings"] = 0
        form = RecipeForm(data=data)
        self.assertIsNotNone(form)

    def test_negative_time(self):
        data = self.get_valid_data()
        data["prep_time"] = -5
        form = RecipeForm(data=data)
        self.assertIsNotNone(form)