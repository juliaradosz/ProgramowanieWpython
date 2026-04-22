from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@magic.pl', is_admin=True)
        admin.password_hash = "puchatek123"
        db.session.add(admin)

    if not User.query.filter_by(username='kopciuszek').first():
        user = User(username='kopciuszek', email='user@magic.pl', is_admin=False)
        user.password_hash = "pantofelek"
        db.session.add(user)

    db.session.commit()
    print("Magiczna baza danych zainicjalizowana!")

if __name__ == '__main__':
    app.run(debug=True)