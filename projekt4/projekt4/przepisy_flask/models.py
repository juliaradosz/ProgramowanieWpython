"""Modele danych (ORM SQLAlchemy).

Odpowiednik modeli z wersji Django (Projekt II) przeniesiony na Flask +
SQLAlchemy. Zachowano te same encje i relacje:

* :class:`User`      – użytkownik wraz z danymi profilu,
* :class:`Category`  – kategoria przepisów,
* :class:`Tag`       – tag (relacja wiele-do-wielu z przepisem),
* :class:`Recipe`    – przepis,
* :class:`Ingredient`– składnik przepisu,
* :class:`Comment`   – komentarz z oceną,
* :class:`Favorite`  – ulubiony przepis użytkownika.
"""

from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, login_manager

# Poziomy trudności przepisu (wartość w bazie -> etykieta wyświetlana).
DIFFICULTY_CHOICES: dict[str, str] = {
    "easy": "Łatwy",
    "medium": "Średni",
    "hard": "Trudny",
}

# Tabela łącząca dla relacji wiele-do-wielu między przepisami a tagami.
recipe_tags = db.Table(
    "recipe_tags",
    db.Column("recipe_id", db.ForeignKey("recipe.id"), primary_key=True),
    db.Column("tag_id", db.ForeignKey("tag.id"), primary_key=True),
)


@login_manager.user_loader
def load_user(user_id: str) -> "User | None":
    """Wczytuje użytkownika na podstawie identyfikatora (wymagane przez Flask-Login)."""
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    """Użytkownik aplikacji (łączy konto i dane profilu)."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email = db.Column(db.String(254), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Dane profilu (w Django osobny model UserProfile, tu scalone dla prostoty).
    bio = db.Column(db.Text, default="")
    favorite_cuisine = db.Column(db.String(100), default="")
    avatar = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    recipes = db.relationship("Recipe", back_populates="author", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    favorites = db.relationship("Favorite", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        """Zapisuje hash hasła (czystego hasła nie przechowujemy nigdy)."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Sprawdza, czy podane hasło zgadza się z zapisanym hashem."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Category(db.Model):
    """Kategoria przepisów (np. Zupy, Desery, Sałatki)."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, default="")

    recipes = db.relationship("Recipe", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category {self.name}>"


class Tag(db.Model):
    """Tag opisujący przepis (np. wegetariańskie, szybkie)."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"


class Recipe(db.Model):
    """Przepis kulinarny."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)

    author_id = db.Column(db.ForeignKey("user.id"), nullable=False)
    category_id = db.Column(db.ForeignKey("category.id"), nullable=True)

    description = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    prep_time = db.Column(db.Integer, nullable=False)
    cook_time = db.Column(db.Integer, nullable=False)
    servings = db.Column(db.Integer, default=4)
    difficulty = db.Column(db.String(10), default="medium")
    image = db.Column(db.String(255), nullable=True)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = db.relationship("User", back_populates="recipes")
    category = db.relationship("Category", back_populates="recipes")
    tags = db.relationship("Tag", secondary=recipe_tags, backref="recipes")
    ingredients = db.relationship(
        "Ingredient", back_populates="recipe", cascade="all, delete-orphan"
    )
    comments = db.relationship(
        "Comment",
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="Comment.created_at.desc()",
    )
    favorited_by = db.relationship(
        "Favorite", back_populates="recipe", cascade="all, delete-orphan"
    )

    @property
    def total_time(self) -> int:
        """Łączny czas przygotowania (przygotowanie + gotowanie)."""
        return self.prep_time + self.cook_time

    @property
    def average_rating(self) -> float:
        """Średnia ocena na podstawie komentarzy (0, gdy brak ocen)."""
        if not self.comments:
            return 0.0
        return sum(c.rating for c in self.comments) / len(self.comments)

    @property
    def difficulty_label(self) -> str:
        """Etykieta poziomu trudności w języku polskim."""
        return DIFFICULTY_CHOICES.get(self.difficulty, self.difficulty)

    def __repr__(self) -> str:
        return f"<Recipe {self.title}>"


class Ingredient(db.Model):
    """Składnik przepisu."""

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.ForeignKey("recipe.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(50), default="")

    recipe = db.relationship("Recipe", back_populates="ingredients")

    def __str__(self) -> str:
        if self.unit:
            return f"{self.quantity} {self.unit} - {self.name}"
        return f"{self.quantity} - {self.name}"


class Comment(db.Model):
    """Komentarz do przepisu wraz z oceną (1-5)."""

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.ForeignKey("recipe.id"), nullable=False)
    author_id = db.Column(db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    recipe = db.relationship("Recipe", back_populates="comments")
    author = db.relationship("User", back_populates="comments")

    # Jeden użytkownik może dodać tylko jeden komentarz do danego przepisu.
    __table_args__ = (db.UniqueConstraint("recipe_id", "author_id"),)


class Favorite(db.Model):
    """Powiązanie użytkownika z ulubionym przepisem."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)
    recipe_id = db.Column(db.ForeignKey("recipe.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="favorites")
    recipe = db.relationship("Recipe", back_populates="favorited_by")

    __table_args__ = (db.UniqueConstraint("user_id", "recipe_id"),)
