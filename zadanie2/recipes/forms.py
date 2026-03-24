from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Recipe, Comment, Ingredient, UserProfile


class UserRegisterForm(UserCreationForm):
    """Formularz rejestracji użytkownika."""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    """Formularz edycji profilu użytkownika."""
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'favorite_cuisine']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class RecipeForm(forms.ModelForm):
    """Formularz dodawania/edycji przepisu."""
    class Meta:
        model = Recipe
        fields = ['title', 'category', 'tags', 'description', 'instructions',
                  'prep_time', 'cook_time', 'servings', 'difficulty', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'instructions': forms.Textarea(attrs={'rows': 8}),
            'tags': forms.CheckboxSelectMultiple(),
        }


class IngredientForm(forms.ModelForm):
    """Formularz składnika."""
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity', 'unit']


IngredientFormSet = forms.inlineformset_factory(
    Recipe, Ingredient,
    form=IngredientForm,
    extra=5,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class CommentForm(forms.ModelForm):
    """Formularz dodawania komentarza."""
    class Meta:
        model = Comment
        fields = ['content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Napisz komentarz...'}),
            'rating': forms.RadioSelect(choices=[(i, f'{i} ★') for i in range(1, 6)]),
        }


class SearchForm(forms.Form):
    """Formularz wyszukiwania przepisów."""
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Szukaj przepisów...', 'class': 'form-control'})
    )
    category = forms.CharField(required=False)
    difficulty = forms.ChoiceField(
        choices=[('', 'Wszystkie')] + Recipe.DIFFICULTY_CHOICES,
        required=False,
    )
