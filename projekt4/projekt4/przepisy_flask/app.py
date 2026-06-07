"""Punkt wejścia aplikacji Flask z asystentem kulinarnym AI (Groq)."""

from __future__ import annotations

import click
from flask import Flask, render_template

from ai_assistant import ChatAssistant
from config import Config
from extensions import csrf, db, login_manager


def create_app(config_class: type[Config] = Config) -> Flask:
    """Tworzy i konfiguruje instancję aplikacji Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    import os
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    app.chat_assistant = ChatAssistant(
        api_key=app.config["GROQ_API_KEY"],
        model=app.config["GROQ_MODEL"],
    )

    from blueprints.auth import auth_bp
    from blueprints.chat import chat_bp
    from blueprints.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)

    _register_error_handlers(app)
    _register_cli(app)
    _register_context(app)

    return app


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return render_template("errors/500.html"), 500


def _register_context(app: Flask) -> None:
    @app.context_processor
    def inject_globals():
        return {"ai_enabled": app.chat_assistant.available}


def _register_cli(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db() -> None:
        """Tworzy wszystkie tabele w bazie danych."""
        db.create_all()
        click.echo("Utworzono tabele bazy danych.")

    @app.cli.command("seed")
    def seed() -> None:
        """Wypełnia bazę przykładowymi danymi."""
        from seed import seed_data
        db.create_all()
        seed_data()
        click.echo("Baza danych została wypełniona przykładowymi danymi.")


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)