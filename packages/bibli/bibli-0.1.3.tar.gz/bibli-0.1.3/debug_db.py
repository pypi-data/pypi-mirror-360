#!/usr/bin/env python3
"""Debug script to check Bible database contents."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bibli.models import DatabaseManager
from bibli.config import Config


def main():
    config = Config()
    db_path = config.get_database_path()
    db_manager = DatabaseManager(f"sqlite:///{db_path}")

    print(f"Database path: {db_path}")
    print(f"Database exists: {os.path.exists(db_path)}")

    try:
        from bibli.models import Verse

        with db_manager.get_session() as session:
            # Count books and verses
            books = db_manager.get_books()
            total_verses = session.query(Verse).count()

            print(f"\nBooks: {len(books)}")
            print(f"Total verses: {total_verses}")

            if books:
                print(f"\nFirst 5 books:")
                for book in books[:5]:
                    verse_count = (
                        session.query(Verse).filter_by(book_id=book.id).count()
                    )
                    print(
                        f"  {book.name} ({book.abbreviation}) - Chapters: {book.chapters}, Verses in DB: {verse_count}"
                    )

                # Test getting a chapter
                first_book = books[0]
                print(f"\nTesting chapter 1 of {first_book.name}:")
                verses = db_manager.get_chapter(first_book.name, 1)
                print(f"  Found {len(verses)} verses")
                if verses:
                    with db_manager.get_session() as session:
                        # Re-query to get the verse with book loaded
                        verse = session.query(Verse).filter_by(id=verses[0].id).first()
                        print(
                            f"  First verse: {verse.reference} - {verse.text[:100]}..."
                        )

    except Exception as e:
        print(f"Error accessing database: {e}")


if __name__ == "__main__":
    main()
