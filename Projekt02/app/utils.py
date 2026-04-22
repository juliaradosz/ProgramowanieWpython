import requests


def fetch_books_by_query(query, max_results=12):
    """
    Pobiera książki z Open Library Search API.
    Darmowe, bez klucza API.
    """
    url = (
        "https://openlibrary.org/search.json"
        f"?q={requests.utils.quote(query)}"
        "&language=eng"
        f"&limit=50"
        "&fields=key,title,author_name,cover_i,first_publish_year,"
        "subject,publisher,number_of_pages_median,first_sentence"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("docs"):
            return []

        return _process_docs(data["docs"], max_results)

    except Exception as e:
        print(f"Search error: {e}")
        return []


def fetch_books_by_subject(subject, max_results=16):
    """
    Pobiera książki z Open Library Subject API.
    Zwraca dużo więcej i lepiej dopasowanych wyników niż wyszukiwanie.
    Np. subject='fantasy' zwraca setki znanych książek fantasy.
    """
    url = (
        f"https://openlibrary.org/subjects/{requests.utils.quote(subject)}.json"
        f"?limit=50"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        works = data.get("works", [])
        if not works:
            return []

        results = []
        authors_seen = {}
        boring_words = [
            'textbook', 'workbook', 'journal', 'proceedings',
            'encyclopedia', 'dictionary', 'study guide',
            'summary', 'analysis of', 'book review',
        ]

        for work in works:
            title = work.get("title", "")
            authors = work.get("authors", [])
            cover_id = work.get("cover_id") or work.get("cover_edition_key")

            if not authors:
                continue

            if any(word in title.lower() for word in boring_words):
                continue

            cover_i = work.get("cover_id")
            if cover_i:
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_i}-M.jpg"
            else:
                ed_key = work.get("cover_edition_key", "")
                if ed_key:
                    cover_url = f"https://covers.openlibrary.org/b/olid/{ed_key}-M.jpg"
                else:
                    continue

            author_name = authors[0].get("name", "Unknown")

            if authors_seen.get(author_name, 0) >= 2:
                continue
            authors_seen[author_name] = authors_seen.get(author_name, 0) + 1

            ol_key = work.get("key", "").replace("/works/", "")

            results.append({
                "google_id": ol_key,
                "title": title,
                "author": author_name,
                "description": work.get("description", f"A {subject} book by {author_name}.")[:400] + "...",
                "cover_url": cover_url,
                "year": str(work.get("first_publish_year", "----")),
                "genre": subject.replace("_", " ").title(),
                "publisher": "Open Library",
                "page_count": "—",
                "author_photo": (
                    f"https://covers.openlibrary.org/a/name/"
                    f"{requests.utils.quote(author_name)}-M.jpg"
                ),
            })

            if len(results) >= max_results:
                break

        return results

    except Exception as e:
        print(f"Subject error ({subject}): {e}")
        return []


def _process_docs(docs, max_results):
    """Przetwarza wyniki z Open Library Search API."""
    results = []
    authors_seen = {}
    boring_words = [
        'textbook', 'workbook', 'journal', 'proceedings',
        'encyclopedia', 'dictionary', 'study guide',
        'summary', 'analysis of', 'book review',
    ]

    for doc in docs:
        title = doc.get("title", "")
        authors = doc.get("author_name", [])
        cover_i = doc.get("cover_i")

        if not authors or not cover_i:
            continue

        if any(word in title.lower() for word in boring_words):
            continue

        author_name = authors[0]

        if authors_seen.get(author_name, 0) >= 2:
            continue
        authors_seen[author_name] = authors_seen.get(author_name, 0) + 1

        cover_url = f"https://covers.openlibrary.org/b/id/{cover_i}-M.jpg"

        first_sentence = doc.get("first_sentence", [])
        if isinstance(first_sentence, list) and first_sentence:
            desc = first_sentence[0]
        elif isinstance(first_sentence, str):
            desc = first_sentence
        else:
            desc = f"A book by {author_name}."

        subjects = doc.get("subject", ["Fiction"])
        genre = subjects[0][:50] if subjects else "Fiction"
        publishers = doc.get("publisher", ["Unknown"])
        publisher = publishers[0][:100] if publishers else "Unknown"
        ol_key = doc.get("key", "").replace("/works/", "")

        results.append({
            "google_id": ol_key,
            "title": title,
            "author": author_name,
            "description": str(desc)[:400] + "...",
            "cover_url": cover_url,
            "year": str(doc.get("first_publish_year", "----")),
            "genre": genre,
            "publisher": publisher,
            "page_count": doc.get("number_of_pages_median", "—"),
            "author_photo": (
                f"https://covers.openlibrary.org/a/name/"
                f"{requests.utils.quote(author_name)}-M.jpg"
            ),
        })

        if len(results) >= max_results:
            break

    return results