"""Trasy uwierzytelniania i profili użytkowników.

Odpowiednik widoków ``register``, ``login``, ``logout``, ``profile`` oraz
``profile_edit`` z wersji Django.
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
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from extensions import db
from forms import LoginForm, ProfileForm, RegisterForm
from models import Recipe, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/rejestracja/", methods=["GET", "POST"])
def register():
    """Rejestracja nowego użytkownika."""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegisterForm()
    if form.validate_on_submit():
        if db.session.scalar(db.select(User).filter_by(username=form.username.data)):
            flash("Ta nazwa użytkownika jest już zajęta.", "danger")
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f"Witaj {user.username}! Konto zostało utworzone.", "success")
            return redirect(url_for("main.home"))

    return render_template("register.html", form=form)


@auth_bp.route("/logowanie/", methods=["GET", "POST"])
def login():
    """Logowanie użytkownika."""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).filter_by(username=form.username.data))
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Witaj {user.username}!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.home"))
        flash("Nieprawidłowa nazwa użytkownika lub hasło.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/wyloguj/")
@login_required
def logout():
    """Wylogowanie użytkownika."""
    logout_user()
    flash("Zostałeś wylogowany.", "info")
    return redirect(url_for("main.home"))


@auth_bp.route("/profil/<username>/")
def profile(username: str):
    """Profil użytkownika: jego przepisy i ulubione dania."""
    user = db.session.scalar(db.select(User).filter_by(username=username))
    if user is None:
        abort(404)
    user_recipes = [r for r in user.recipes if r.is_published]
    favorite_recipes = [fav.recipe for fav in user.favorites]
    return render_template(
        "profile.html",
        profile_user=user,
        user_recipes=user_recipes,
        favorite_recipes=favorite_recipes,
    )


@auth_bp.route("/profil/<username>/edytuj/", methods=["GET", "POST"])
@login_required
def profile_edit(username: str):
    """Edycja własnego profilu."""
    if current_user.username != username:
        flash("Nie możesz edytować cudzego profilu.", "danger")
        return redirect(url_for("auth.profile", username=username))

    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.bio = form.bio.data or ""
        current_user.favorite_cuisine = form.favorite_cuisine.data or ""
        if form.avatar.data and form.avatar.data.filename:
            ext = form.avatar.data.filename.rsplit(".", 1)[-1].lower()
            name = f"{uuid.uuid4().hex}.{ext}"
            form.avatar.data.save(
                os.path.join(current_app.config["UPLOAD_FOLDER"], secure_filename(name))
            )
            current_user.avatar = name
        db.session.commit()
        flash("Profil został zaktualizowany.", "success")
        return redirect(url_for("auth.profile", username=username))

    return render_template("profile_edit.html", form=form)
