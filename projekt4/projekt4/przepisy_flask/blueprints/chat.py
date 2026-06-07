"""Trasy asystenta kulinarnego AI (czat z modelem Claude).

* ``GET  /asystent/``           – strona z interfejsem czatu,
* ``POST /asystent/wiadomosc``  – punkt JSON zwracający odpowiedź asystenta.

Historia rozmowy przechowywana jest po stronie przeglądarki i przesyłana
przy każdym żądaniu (API modelu jest bezstanowe).
"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template, request

from extensions import db
from models import Recipe

chat_bp = Blueprint("chat", __name__)

# Maksymalna liczba wcześniejszych wiadomości przekazywanych do modelu
# (ogranicza koszt i rozmiar żądania).
_MAX_HISTORY = 12


def _recipe_context(slug: str | None) -> str | None:
    """Buduje krótki opis przepisu, jeśli czat dotyczy konkretnej strony."""
    if not slug:
        return None
    recipe = db.session.scalar(db.select(Recipe).filter_by(slug=slug))
    if recipe is None:
        return None
    ingredients = ", ".join(f"{i.quantity} {i.unit} {i.name}".strip() for i in recipe.ingredients)
    return (
        f"Tytuł: {recipe.title}\n"
        f"Kategoria: {recipe.category.name if recipe.category else 'brak'}\n"
        f"Liczba porcji: {recipe.servings}\n"
        f"Składniki: {ingredients}\n"
        f"Opis: {recipe.description}"
    )


@chat_bp.route("/asystent/")
def chat_page():
    """Renderuje stronę czatu z asystentem AI."""
    slug = request.args.get("recipe")
    recipe = db.session.scalar(db.select(Recipe).filter_by(slug=slug)) if slug else None
    return render_template("chat.html", recipe=recipe)


@chat_bp.route("/asystent/wiadomosc", methods=["POST"])
def message():
    """Przyjmuje wiadomość użytkownika i zwraca odpowiedź asystenta (JSON)."""
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return jsonify({"error": "Pusta wiadomość."}), 400

    # Przyjmujemy tylko poprawne wpisy historii (rola user/assistant + treść).
    raw_history = data.get("history") or []
    history = [
        {"role": m.get("role"), "content": (m.get("content") or "").strip()}
        for m in raw_history
        if m.get("role") in ("user", "assistant") and (m.get("content") or "").strip()
    ][-_MAX_HISTORY:]

    context = _recipe_context(data.get("recipe"))

    reply = current_app.chat_assistant.reply(history, user_message, context)
    return jsonify({"reply": reply})
