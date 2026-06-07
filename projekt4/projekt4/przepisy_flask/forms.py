"""Formularze aplikacji (Flask-WTF / WTForms).

Odpowiednik formularzy Django. Zapewniają walidację danych po stronie
serwera oraz ochronę CSRF (token wstawiany automatycznie w szablonach).
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    Optional,
)

from models import DIFFICULTY_CHOICES

_IMAGES = ["png", "jpg", "jpeg", "gif", "webp"]


class RegisterForm(FlaskForm):
    """Rejestracja nowego użytkownika."""

    username = StringField("Nazwa użytkownika", validators=[DataRequired(), Length(3, 150)])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Hasło", validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        "Powtórz hasło",
        validators=[DataRequired(), EqualTo("password", message="Hasła muszą być takie same.")],
    )


class LoginForm(FlaskForm):
    """Logowanie użytkownika."""

    username = StringField("Nazwa użytkownika", validators=[DataRequired()])
    password = PasswordField("Hasło", validators=[DataRequired()])
    remember = BooleanField("Zapamiętaj mnie")


class ProfileForm(FlaskForm):
    """Edycja profilu użytkownika."""

    bio = TextAreaField("O mnie", validators=[Optional(), Length(max=1000)])
    favorite_cuisine = StringField("Ulubiona kuchnia", validators=[Optional(), Length(max=100)])
    avatar = FileField("Zdjęcie profilowe", validators=[FileAllowed(_IMAGES, "Tylko obrazy!")])


class RecipeForm(FlaskForm):
    """Dodawanie i edycja przepisu."""

    title = StringField("Tytuł", validators=[DataRequired(), Length(max=200)])
    category = SelectField("Kategoria", coerce=int, validators=[Optional()])
    description = TextAreaField("Opis", validators=[DataRequired()])
    instructions = TextAreaField("Instrukcje przygotowania", validators=[DataRequired()])
    prep_time = IntegerField("Czas przygotowania (min)", validators=[DataRequired(), NumberRange(min=0)])
    cook_time = IntegerField("Czas gotowania (min)", validators=[DataRequired(), NumberRange(min=0)])
    servings = IntegerField("Liczba porcji", validators=[DataRequired(), NumberRange(min=1)])
    difficulty = SelectField("Poziom trudności", choices=list(DIFFICULTY_CHOICES.items()))
    image = FileField("Zdjęcie", validators=[FileAllowed(_IMAGES, "Tylko obrazy!")])


class CommentForm(FlaskForm):
    """Komentarz z oceną w skali 1-5."""

    content = TextAreaField("Treść", validators=[DataRequired(), Length(max=2000)])
    rating = SelectField(
        "Ocena",
        choices=[(str(i), f"{i} ★") for i in range(1, 6)],
        validators=[DataRequired()],
    )
