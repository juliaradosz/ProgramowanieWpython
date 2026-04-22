import requests
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.books import bp
from app.models import Book, Review, UserBookStatus
from app.utils import fetch_books_by_query, fetch_books_by_subject


CATEGORY_QUERIES = {
    'Fantasy':  [
        'Brandon Sanderson Mistborn',
        'Patrick Rothfuss Kingkiller',
        'Robin Hobb Farseer',
        'Joe Abercrombie First Law',
    ],
    'Thriller': [
        'Gillian Flynn Gone Girl',
        'Harlan Coben thriller',
        'Lee Child Jack Reacher',
        'James Patterson thriller',
    ],
    'Romance':  [
        'Colleen Hoover It Ends with Us',
        'Emily Henry Beach Read',
        'Taylor Jenkins Reid Daisy Jones',
        'Lisa Kleypas romance',
    ],
    'Horror':   [
        'Stephen King The Shining',
        'Stephen King It',
        'Dean Koontz horror',
        'Paul Tremblay horror',
    ],
    'History':  [
        'Ken Follett Pillars of the Earth',
        'Hilary Mantel Wolf Hall',
        'Anthony Doerr All the Light',
        'Kristin Hannah historical',
    ],
    'Science':  [
        'Yuval Noah Harari Sapiens',
        'Malcolm Gladwell Outliers',
        'Bill Bryson Short History',
        'Richard Dawkins Selfish Gene',
    ],
}

CATEGORY_SUBJECTS = {
    'Fantasy':  'fantasy_fiction',
    'Thriller': 'thriller',
    'Romance':  'romance',
    'Horror':   'horror_fiction',
    'History':  'historical_fiction',
    'Science':  'popular_science',
}

HOMEPAGE_QUERY = 'bestseller fiction'


@bp.route('/')
def index():
    """
    Strona główna biblioteki.
    Wyświetla bestsellery, wyniki wyszukiwania lub książki z wybranego gatunku.
    """
    query = request.args.get('query')
    category = request.args.get('category')

    if query:
        books = fetch_books_by_query(query, max_results=16)
        shelf_title = f'Search results: "{query}"'

    elif category and category in CATEGORY_SUBJECTS:
        books = fetch_books_by_subject(CATEGORY_SUBJECTS[category], max_results=16)
        shelf_title = f'Top: {category}'

    else:
        books = fetch_books_by_query(HOMEPAGE_QUERY, max_results=12)
        shelf_title = "🔥 World Bestsellers"

    return render_template(
        'index.html',
        books=books,
        genres=list(CATEGORY_SUBJECTS.keys()),
        category_previews={
            'Fantasy':  '/static/images/genre_fantasy.jpg',
            'Thriller': '/static/images/genre_thriller.jpg',
            'Romance':  '/static/images/genre_romance.jpg',
            'Horror':   '/static/images/genre_horror.jpg',
            'History':  '/static/images/genre_history.jpg',
            'Science':  '/static/images/genre_science.jpg',
        },
        recommendations=[],
        shelf_title=shelf_title,
    )


@bp.route('/book/<ol_id>')
def book_details(ol_id):
    """
    Szczegóły książki z Open Library: tytuł, opis, okładka, autor (ze zdjęciem),
    rok wydania, liczba stron i wydawca pobierane z works + editions + authors API.
    """
    book_data = None
    try:
        work = requests.get(
            f"https://openlibrary.org/works/{ol_id}.json", timeout=10
        ).json()

        title = work.get("title", "Unknown")

        desc = work.get("description", "")
        if isinstance(desc, dict):
            desc = desc.get("value", "")
        desc = str(desc)[:600] if desc else "No description available."

        covers = work.get("covers", [])
        cover_url = (
            f"https://covers.openlibrary.org/b/id/{covers[0]}-L.jpg"
            if covers else ""
        )

        subjects = work.get("subjects", ["Fiction"])
        genre = subjects[0][:50] if subjects else "Fiction"

        author_name = "Unknown"
        author_bio = ""
        author_photo = ""
        authors_data = work.get("authors", [])
        if authors_data:
            author_key = authors_data[0].get("author", {}).get("key", "")
            if author_key:
                a_data = requests.get(
                    f"https://openlibrary.org{author_key}.json", timeout=8
                ).json()
                author_name = a_data.get("name", "Unknown")
                bio = a_data.get("bio", "")
                if isinstance(bio, dict):
                    bio = bio.get("value", "")
                author_bio = str(bio)[:300] if bio else ""
                author_photos = a_data.get("photos", [])
                if author_photos:
                    author_photo = f"https://covers.openlibrary.org/a/id/{author_photos[0]}-M.jpg"
                else:
                    author_photo = (
                        f"https://covers.openlibrary.org/a/name/"
                        f"{requests.utils.quote(author_name)}-M.jpg"
                    )

        year = "----"
        page_count = "—"
        publisher = "Unknown"
        try:
            eds = requests.get(
                f"https://openlibrary.org/works/{ol_id}/editions.json?limit=10",
                timeout=8
            ).json().get("entries", [])
            for ed in eds:
                if not year or year == "----":
                    year = ed.get("publish_date", "----")
                    if year and len(year) >= 4:
                        year = year[-4:]
                if page_count == "—":
                    page_count = ed.get("number_of_pages", "—")
                if publisher == "Unknown":
                    pubs = ed.get("publishers", [])
                    publisher = pubs[0] if pubs else "Unknown"
                if year != "----" and page_count != "—" and publisher != "Unknown":
                    break
        except Exception:
            pass

        book_data = {
            "google_id": ol_id,
            "title": title,
            "author": author_name,
            "author_bio": author_bio,
            "description": desc + "...",
            "cover_url": cover_url,
            "year": year,
            "genre": genre,
            "publisher": publisher,
            "page_count": page_count,
            "author_photo": author_photo,
        }

    except Exception as e:
        print(f"Error fetching {ol_id}: {e}")
        book_data = None

    title = book_data["title"] if book_data else ""
    author = book_data["author"] if book_data else ""
    db_book = Book.query.filter_by(title=title, author=author).first()
    reviews = db_book.reviews.all() if db_book else []

    return render_template(
        'book_details.html',
        book=book_data,
        db_book=db_book,
        reviews=reviews,
    )

@bp.route('/update_status', methods=['POST'])
@login_required
def update_status():
    """Dodaje lub aktualizuje status książki na półce użytkownika."""
    title = request.form.get('title')
    author = request.form.get('author')

    book = Book.query.filter_by(title=title, author=author).first()

    if not book:
        book = Book(
            google_id=request.form.get('google_id'),
            title=title,
            author=author,
            genre=request.form.get('genre'),
            year=request.form.get('year'),
            description=request.form.get('description'),
            cover_url=request.form.get('cover_url'),
            publisher=request.form.get('publisher'),
            page_count=request.form.get('page_count'),
        )
        db.session.add(book)
        db.session.commit()

    status = request.form.get('status')
    user_status = UserBookStatus.query.filter_by(
        user_id=current_user.id,
        book_id=book.id,
    ).first()

    if user_status:
        user_status.status = status
    else:
        user_status = UserBookStatus(
            user_id=current_user.id,
            book_id=book.id,
            status=status,
        )
        db.session.add(user_status)

    db.session.commit()
    flash("Book saved to your shelf!")
    return redirect(url_for('books.profile'))


@bp.route('/profile')
@login_required
def profile():
    """Profil użytkownika z jego półką książek."""
    statuses = UserBookStatus.query.filter_by(user_id=current_user.id).all()

    return render_template(
        'profile.html',
        reading=[s for s in statuses if s.status == 'Reading'],
        to_read=[s for s in statuses if s.status == 'To Read'],
        read=[s for s in statuses if s.status == 'Read'],
    )


@bp.route('/add_review', methods=['POST'])
@login_required
def add_review():
    """Dodaje recenzję do książki (wymaga, by książka była już w bazie)."""
    title = request.form.get('title')
    author = request.form.get('author')

    book = Book.query.filter_by(title=title, author=author).first()

    if not book:
        flash("Add the book to your shelf first!")
        return redirect(request.referrer)

    review = Review(
        rating=int(request.form.get('rating')),
        content=request.form.get('content'),
        user_id=current_user.id,
        book_id=book.id,
    )

    db.session.add(review)
    db.session.commit()

    flash("Review added!")
    return redirect(request.referrer)