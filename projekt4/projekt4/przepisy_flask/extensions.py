"""Inicjalizacja rozszerzeń Flask.

Rozszerzenia tworzone są tutaj jako "puste" obiekty, a ich powiązanie
z aplikacją następuje w fabryce :func:`app.create_app`. Taki podział
unika cyklicznych importów i ułatwia testowanie.
"""

from __future__ import annotations

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

# ORM (mapowanie modeli na tabele bazy danych).
db = SQLAlchemy()

# Zarządzanie sesją logowania użytkowników.
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Zaloguj się, aby uzyskać dostęp do tej strony."
login_manager.login_message_category = "warning"

# Ochrona formularzy przed atakami CSRF.
csrf = CSRFProtect()
