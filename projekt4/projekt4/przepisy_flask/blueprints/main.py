"""Trasy domeny przepisów: strona główna, lista, szczegóły, CRUD, kategorie,
wyszukiwanie i ulubione.

Odpowiednik ``views.py`` z wersji Django.
"""

from __future__ import annotations

import os
import uuid

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from extensions import db
from forms import CommentForm, RecipeForm
from models import Category, Comment, Favorite, Ingredient, Recipe
from utils import slugify

main_bp = Blueprint("main", __name__)


# --- Funkcje pomocnicze ------------------------------------------------------
def _unique_slug(title: str) -> str:
    """Tworzy unikalny slug dla przepisu (dokleja licznik przy kolizji)."""
    base = slugify(title)
    slug = base
    counter = 1
    while db.session.scalar(db.select(Recipe).filter_by(slug=slug)):
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def _save_image(file_storage) -> str | None:
    """Zapisuje przesłany obraz pod unikalną nazwą i zwraca tę nazwę."""
    if not file_storage or not file_storage.filename:
        return None
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"
    file_storage.save(os.path.join(current_app.config["UPLOAD_FOLDER"], secure_filename(name)))
    return name


def _populate_category_choices(form: RecipeForm) -> None:
    """Uzupełnia listę wyboru kategorii w formularzu przepisu."""
    categories = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    form.category.choices = [(c.id, c.name) for c in categories]


def _parse_ingredients() -> list[tuple[str, str, str]]:
    """Odczytuje składniki z formularza (pola name[], quantity[], unit[])."""
    names = request.form.getlist("ingredient_name")
    quantities = request.form.getlist("ingredient_quantity")
    units = request.form.getlist("ingredient_unit")
    result = []
    for name, qty, unit in zip(names, quantities, units):
        if name.strip():
            result.append((name.strip(), qty.strip() or "-", unit.strip()))
    return result


# --- Trasy -------------------------------------------------------------------
@main_bp.route("/")
def home():
    """Strona główna: najnowsze przepisy i kategorie."""
    latest = db.session.scalars(
        db.select(Recipe).filter_by(is_published=True).order_by(Recipe.created_at.desc()).limit(6)
    ).all()
    categories = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    top_rated = sorted(
        db.session.scalars(db.select(Recipe).filter_by(is_published=True)).all(),
        key=lambda r: r.average_rating,
        reverse=True,
    )[:3]
    return render_template(
        "home.html", latest_recipes=latest, categories=categories, top_rated=top_rated
    )


@main_bp.route("/przepisy/")
def recipe_list():
    """Lista wszystkich opublikowanych przepisów."""
    recipes = db.session.scalars(
        db.select(Recipe).filter_by(is_published=True).order_by(Recipe.created_at.desc())
    ).all()
    return render_template("recipe_list.html", recipes=recipes)


@main_bp.route("/przepis/<slug>/", methods=["GET", "POST"])
def recipe_detail(slug: str):
    """Szczegóły przepisu wraz z komentarzami i formularzem komentarza."""
    recipe = db.session.scalar(db.select(Recipe).filter_by(slug=slug, is_published=True))
    if recipe is None:
        abort(404)

    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = (
            db.session.scalar(
                db.select(Favorite).filter_by(user_id=current_user.id, recipe_id=recipe.id)
            )
            is not None
        )

    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Zaloguj się, aby dodać komentarz.", "warning")
            return redirect(url_for("auth.login"))
        existing = db.session.scalar(
            db.select(Comment).filter_by(recipe_id=recipe.id, author_id=current_user.id)
        )
        if existing:
            flash("Już dodałeś komentarz do tego przepisu.", "warning")
        else:
            db.session.add(
                Comment(
                    recipe_id=recipe.id,
                    author_id=current_user.id,
                    content=form.content.data,
                    rating=int(form.rating.data),
                )
            )
            db.session.commit()
            flash("Komentarz został dodany.", "success")
        return redirect(url_for("main.recipe_detail", slug=slug))

    return render_template(
        "recipe_detail.html", recipe=recipe, comment_form=form, is_favorite=is_favorite
    )


@main_bp.route("/przepis/nowy/", methods=["GET", "POST"])
@login_required
def recipe_create():
    """Tworzenie nowego przepisu."""
    form = RecipeForm()
    _populate_category_choices(form)

    if form.validate_on_submit():
        recipe = Recipe(
            title=form.title.data,
            slug=_unique_slug(form.title.data),
            author_id=current_user.id,
            category_id=form.category.data,
            description=form.description.data,
            instructions=form.instructions.data,
            prep_time=form.prep_time.data,
            cook_time=form.cook_time.data,
            servings=form.servings.data,
            difficulty=form.difficulty.data,
            image=_save_image(form.image.data),
        )
        for name, qty, unit in _parse_ingredients():
            recipe.ingredients.append(Ingredient(name=name, quantity=qty, unit=unit))
        db.session.add(recipe)
        db.session.commit()
        flash("Przepis został dodany!", "success")
        return redirect(url_for("main.recipe_detail", slug=recipe.slug))

    return render_template("recipe_form.html", form=form, title="Dodaj przepis", recipe=None)


@main_bp.route("/przepis/<slug>/edytuj/", methods=["GET", "POST"])
@login_required
def recipe_update(slug: str):
    """Edycja istniejącego przepisu (tylko autor lub administrator)."""
    recipe = db.session.scalar(db.select(Recipe).filter_by(slug=slug))
    if recipe is None:
        abort(404)
    if recipe.author_id != current_user.id and not current_user.is_admin:
        flash("Nie masz uprawnień do edycji tego przepisu.", "danger")
        return redirect(url_for("main.recipe_detail", slug=slug))

    form = RecipeForm(obj=recipe)
    _populate_category_choices(form)
    if request.method == "GET":
        form.category.data = recipe.category_id

    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.category_id = form.category.data
        recipe.description = form.description.data
        recipe.instructions = form.instructions.data
        recipe.prep_time = form.prep_time.data
        recipe.cook_time = form.cook_time.data
        recipe.servings = form.servings.data
        recipe.difficulty = form.difficulty.data
        if form.image.data:
            recipe.image = _save_image(form.image.data)

        ingredients = _parse_ingredients()
        if ingredients:
            recipe.ingredients.clear()
            for name, qty, unit in ingredients:
                recipe.ingredients.append(Ingredient(name=name, quantity=qty, unit=unit))
        db.session.commit()
        flash("Przepis został zaktualizowany!", "success")
        return redirect(url_for("main.recipe_detail", slug=recipe.slug))

    return render_template("recipe_form.html", form=form, title="Edytuj przepis", recipe=recipe)


@main_bp.route("/przepis/<slug>/usun/", methods=["POST"])
@login_required
def recipe_delete(slug: str):
    """Usuwanie przepisu (tylko autor lub administrator)."""
    recipe = db.session.scalar(db.select(Recipe).filter_by(slug=slug))
    if recipe is None:
        abort(404)
    if recipe.author_id != current_user.id and not current_user.is_admin:
        flash("Nie masz uprawnień do usunięcia tego przepisu.", "danger")
        return redirect(url_for("main.recipe_detail", slug=slug))

    db.session.delete(recipe)
    db.session.commit()
    flash("Przepis został usunięty.", "info")
    return redirect(url_for("main.recipe_list"))


@main_bp.route("/kategorie/")
def category_list():
    """Lista kategorii."""
    categories = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    return render_template("category_list.html", categories=categories)


@main_bp.route("/kategoria/<slug>/")
def category_detail(slug: str):
    """Przepisy w wybranej kategorii."""
    category = db.session.scalar(db.select(Category).filter_by(slug=slug))
    if category is None:
        abort(404)
    recipes = [r for r in category.recipes if r.is_published]
    return render_template("category_detail.html", category=category, recipes=recipes)


@main_bp.route("/szukaj/")
def search():
    """Wyszukiwanie przepisów po tytule, opisie, składnikach i trudności."""
    query = (request.args.get("query") or "").strip()
    difficulty = request.args.get("difficulty") or ""

    stmt = db.select(Recipe).filter_by(is_published=True)
    if query:
        like = f"%{query}%"
        stmt = stmt.where(
            db.or_(
                Recipe.title.ilike(like),
                Recipe.description.ilike(like),
                Recipe.ingredients.any(Ingredient.name.ilike(like)),
            )
        )
    if difficulty:
        stmt = stmt.where(Recipe.difficulty == difficulty)

    recipes = db.session.scalars(stmt.order_by(Recipe.created_at.desc())).all()
    return render_template(
        "search.html", recipes=recipes, query=query, difficulty=difficulty
    )


@main_bp.route("/przepis/<slug>/ulubione/", methods=["POST"])
@login_required
def toggle_favorite(slug: str):
    """Dodaje lub usuwa przepis z ulubionych użytkownika."""
    recipe = db.session.scalar(db.select(Recipe).filter_by(slug=slug))
    if recipe is None:
        abort(404)

    favorite = db.session.scalar(
        db.select(Favorite).filter_by(user_id=current_user.id, recipe_id=recipe.id)
    )
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        flash("Usunięto z ulubionych.", "info")
    else:
        db.session.add(Favorite(user_id=current_user.id, recipe_id=recipe.id))
        db.session.commit()
        flash("Dodano do ulubionych.", "success")
    return redirect(url_for("main.recipe_detail", slug=slug))


@main_bp.route("/ulubione/")
@login_required
def favorite_list():
    """Lista ulubionych przepisów zalogowanego użytkownika."""
    recipes = [fav.recipe for fav in current_user.favorites]
    return render_template("favorites.html", recipes=recipes)
