from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.utils.text import slugify

from .models import Recipe, Category, Tag, Comment, UserProfile, Favorite
from .forms import (
    RecipeForm, IngredientFormSet, CommentForm,
    UserRegisterForm, UserProfileForm, SearchForm,
)


def home(request):
    """Strona główna z najnowszymi przepisami."""
    latest_recipes = Recipe.objects.filter(is_published=True).select_related('author', 'category')[:6]
    categories = Category.objects.all()
    top_rated = (
        Recipe.objects.filter(is_published=True)
        .annotate(avg_rating=Avg('comments__rating'))
        .order_by('-avg_rating')[:3]
    )
    return render(request, 'recipes/home.html', {
        'latest_recipes': latest_recipes,
        'categories': categories,
        'top_rated': top_rated,
    })


def recipe_list(request):
    """Lista wszystkich przepisów."""
    recipes = Recipe.objects.filter(is_published=True).select_related('author', 'category')
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})


def recipe_detail(request, slug):
    """Szczegóły przepisu z komentarzami."""
    recipe = get_object_or_404(Recipe, slug=slug, is_published=True)
    comments = recipe.comments.select_related('author')
    ingredients = recipe.ingredients.all()

    # SPRAWDZENIE ULUBIONYCH
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            # Sprawdź czy użytkownik już skomentował
            if Comment.objects.filter(recipe=recipe, author=request.user).exists():
                messages.warning(request, 'Już dodałeś komentarz do tego przepisu.')
            else:
                comment = comment_form.save(commit=False)
                comment.recipe = recipe
                comment.author = request.user
                comment.save()
                messages.success(request, 'Komentarz został dodany.')
                return redirect('recipes:recipe_detail', slug=slug)
    else:
        comment_form = CommentForm()

    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'comments': comments,
        'ingredients': ingredients,
        'comment_form': comment_form,
        'is_favorite': is_favorite,
    })


@login_required
def recipe_create(request):
    """Tworzenie nowego przepisu."""
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        formset = IngredientFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.slug = slugify(recipe.title)
            # Upewnij się że slug jest unikalny
            base_slug = recipe.slug
            counter = 1
            while Recipe.objects.filter(slug=recipe.slug).exists():
                recipe.slug = f'{base_slug}-{counter}'
                counter += 1
            recipe.save()
            form.save_m2m()  # Zapisz tagi ManyToMany
            formset.instance = recipe
            formset.save()
            messages.success(request, 'Przepis został dodany!')
            return redirect('recipes:recipe_detail', slug=recipe.slug)
    else:
        form = RecipeForm()
        formset = IngredientFormSet()

    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Dodaj przepis',
    })


@login_required
def recipe_update(request, slug):
    """Edycja przepisu."""
    recipe = get_object_or_404(Recipe, slug=slug)
    if recipe.author != request.user and not request.user.is_staff:
        messages.error(request, 'Nie masz uprawnień do edycji tego przepisu.')
        return redirect('recipes:recipe_detail', slug=slug)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        formset = IngredientFormSet(request.POST, instance=recipe)
        if form.is_valid() and formset.is_valid():
            recipe = form.save()
            formset.save()
            messages.success(request, 'Przepis został zaktualizowany!')
            return redirect('recipes:recipe_detail', slug=recipe.slug)
    else:
        form = RecipeForm(instance=recipe)
        formset = IngredientFormSet(instance=recipe)

    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Edytuj przepis',
    })


@login_required
def recipe_delete(request, slug):
    """Usuwanie przepisu."""
    recipe = get_object_or_404(Recipe, slug=slug)
    if recipe.author != request.user and not request.user.is_staff:
        messages.error(request, 'Nie masz uprawnień do usunięcia tego przepisu.')
        return redirect('recipes:recipe_detail', slug=slug)

    if request.method == 'POST':
        recipe.delete()
        messages.success(request, 'Przepis został usunięty.')
        return redirect('recipes:recipe_list')

    return render(request, 'recipes/recipe_confirm_delete.html', {'recipe': recipe})


def category_list(request):
    categories = Category.objects.all()

    for category in categories:
        category.preview_recipe = category.recipes.filter(
            image__isnull=False
        ).order_by('?').first()

    return render(request, 'recipes/category_list.html', {
        'categories': categories
    })


def category_detail(request, slug):
    """Przepisy w danej kategorii."""
    category = get_object_or_404(Category, slug=slug)
    recipes = category.recipes.filter(is_published=True)
    return render(request, 'recipes/category_detail.html', {
        'category': category,
        'recipes': recipes,
    })


def search(request):
    """Wyszukiwanie przepisów."""
    form = SearchForm(request.GET)
    recipes = Recipe.objects.filter(is_published=True)

    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        difficulty = form.cleaned_data.get('difficulty')

        if query:
            recipes = recipes.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(ingredients__name__icontains=query)
            ).distinct()
        if category:
            recipes = recipes.filter(category__slug=category)
        if difficulty:
            recipes = recipes.filter(difficulty=difficulty)

    return render(request, 'recipes/search.html', {
        'form': form,
        'recipes': recipes,
    })


def register(request):
    """Rejestracja nowego użytkownika."""
    if request.user.is_authenticated:
        return redirect('recipes:home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Witaj {user.username}! Konto zostało utworzone.')
            return redirect('recipes:home')
    else:
        form = UserRegisterForm()

    return render(request, 'recipes/register.html', {'form': form})


def user_login(request):
    """Logowanie użytkownika."""
    if request.user.is_authenticated:
        return redirect('recipes:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Witaj {user.username}!')
            next_url = request.GET.get('next', 'recipes:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Nieprawidłowa nazwa użytkownika lub hasło.')

    return render(request, 'recipes/login.html')


def user_logout(request):
    """Wylogowanie użytkownika."""
    logout(request)
    messages.info(request, 'Zostałeś wylogowany.')
    return redirect('recipes:home')


def profile(request, username):
    """Profil użytkownika."""
    from django.contrib.auth.models import User

    user = get_object_or_404(User, username=username)

    user_profile, _ = UserProfile.objects.get_or_create(user=user)

    user_recipes = Recipe.objects.filter(
        author=user,
        is_published=True
    )

    favorite_recipes = Recipe.objects.filter(
        favorited_by__user=user
    )

    return render(request, 'recipes/profile.html', {
        'profile_user': user,
        'user_profile': user_profile,
        'user_recipes': user_recipes,
        'favorite_recipes': favorite_recipes,
    })


@login_required
def profile_edit(request, username):
    """Edycja profilu użytkownika."""
    if request.user.username != username:
        messages.error(request, 'Nie możesz edytować cudzego profilu.')
        return redirect('recipes:profile', username=username)

    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil został zaktualizowany.')
            return redirect('recipes:profile', username=username)
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'recipes/profile_edit.html', {'form': form})


# FUNKCJE ULUBIONYCH
@login_required
def add_to_favorites(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        recipe=recipe
    )

    if created:
        messages.success(request, "Dodano do ulubionych.")
    else:
        favorite.delete()
        messages.info(request, "Usunięto z ulubionych.")

    return redirect('recipes:recipe_detail', slug=slug)


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('recipe')

    recipes = [fav.recipe for fav in favorites]

    return render(request, 'recipes/favorites.html', {
        'recipes': recipes
    })


def handler404(request, exception):
    """Własna strona błędu 404."""
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    """Własna strona błędu 500."""
    return render(request, 'errors/500.html', status=500)