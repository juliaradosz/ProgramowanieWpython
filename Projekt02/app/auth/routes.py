from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.models import User, Review, UserBookStatus
from werkzeug.security import generate_password_hash, check_password_hash


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Logowanie użytkowników."""
    if current_user.is_authenticated:
        return redirect(url_for('books.index'))

    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user)
            flash(f'Witaj, {user.username}!')
            return redirect(url_for('books.index'))
        flash('Błędna nazwa użytkownika lub hasło!')

    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Rejestracja nowego użytkownika."""
    if current_user.is_authenticated:
        return redirect(url_for('books.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')

        if not username or not email or not password:
            flash('Wszystkie pola są wymagane.')
            return render_template('register.html')

        if password != password2:
            flash('Hasła nie są zgodne.')
            return render_template('register.html')

        if len(password) < 6:
            flash('Hasło musi mieć co najmniej 6 znaków.')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Ta nazwa użytkownika jest już zajęta.')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Ten adres e-mail jest już zarejestrowany.')
            return render_template('register.html')

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=False,
        )
        db.session.add(user)
        db.session.commit()

        flash('Konto zostało utworzone! Możesz się teraz zalogować.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@bp.route('/logout')
def logout():
    """Wylogowanie użytkownika."""
    logout_user()
    flash('Zostałeś wylogowany.')
    return redirect(url_for('books.index'))


@bp.route('/admin')
@login_required
def admin_panel():
    """Panel administratora — recenzje i użytkownicy."""
    if not current_user.is_admin:
        flash('Brak uprawnień do panelu administratora!')
        return redirect(url_for('books.index'))

    all_reviews = Review.query.all()
    all_users = User.query.filter_by(is_admin=False).all()
    return render_template('admin.html', reviews=all_reviews, users=all_users)


@bp.route('/delete_review/<int:id>')
@login_required
def delete_review(id):
    """CRUD: Delete — administrator usuwa recenzję."""
    if not current_user.is_admin:
        return redirect(url_for('books.index'))

    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    flash('Recenzja została usunięta.')
    return redirect(url_for('auth.admin_panel'))


@bp.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    """CRUD: Delete — administrator usuwa użytkownika wraz z jego danymi."""
    if not current_user.is_admin:
        return redirect(url_for('books.index'))

    user = User.query.get_or_404(id)

    Review.query.filter_by(user_id=user.id).delete()
    UserBookStatus.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()

    flash(f'Użytkownik „{user.username}" został usunięty.')
    return redirect(url_for('auth.admin_panel'))