"""SQLAlchemy models for Bible CLI application."""

from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Index,
    Boolean,
    DateTime,
    create_engine,
    MetaData,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session, joinedload
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()
metadata = MetaData()


class Book(Base):
    """Bible book model."""

    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    abbreviation = Column(String(10), nullable=False, unique=True)
    testament = Column(String(3), nullable=False)  # 'old' or 'new'
    order = Column(Integer, nullable=False)
    chapters = Column(Integer, nullable=False)

    verses = relationship("Verse", back_populates="book", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Book(name='{self.name}', testament='{self.testament}')>"


class Verse(Base):
    """Bible verse model."""

    __tablename__ = "verses"

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    chapter = Column(Integer, nullable=False)
    verse = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    translation = Column(String(10), nullable=False, default="NIV")

    book = relationship("Book", back_populates="verses", lazy="joined")

    __table_args__ = (
        Index("idx_verses_reference", "book_id", "chapter", "verse"),
        Index("idx_verses_translation", "translation"),
        Index("idx_verses_text", "text"),
    )

    @property
    def reference(self) -> str:
        """Get formatted reference string."""
        return f"{self.book.name} {self.chapter}:{self.verse}"

    def __repr__(self) -> str:
        return f"<Verse(reference='{self.reference}', translation='{self.translation}')>"


class Bookmark(Base):
    """User bookmark model."""

    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True)
    verse_id = Column(Integer, ForeignKey("verses.id"), nullable=False)
    name = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    verse = relationship("Verse", lazy="joined")

    def __repr__(self) -> str:
        return f"<Bookmark(verse='{self.verse.reference}', name='{self.name}')>"


class ReadingHistory(Base):
    """Reading history model."""

    __tablename__ = "reading_history"

    id = Column(Integer, primary_key=True)
    verse_id = Column(Integer, ForeignKey("verses.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    duration_seconds = Column(Integer, nullable=True)

    verse = relationship("Verse", lazy="joined")

    def __repr__(self) -> str:
        return f"<ReadingHistory(verse='{self.verse.reference}', timestamp='{self.timestamp}')>"


class SearchIndex(Base):
    """Full-text search index model."""

    __tablename__ = "search_index"

    id = Column(Integer, primary_key=True)
    verse_id = Column(Integer, ForeignKey("verses.id"), nullable=False)
    content = Column(Text, nullable=False)
    translation = Column(String(10), nullable=False)

    verse = relationship("Verse", lazy="joined")

    __table_args__ = (Index("idx_search_content", "content"),)


class DatabaseManager:
    """Database manager for Bible CLI."""

    def __init__(self, database_url: str = "sqlite:///bible.db"):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()

    def get_verse(self, book: str, chapter: int, verse: int, translation: str = "BBE") -> Optional[Verse]:
        """Get a specific verse."""
        # Get the book first to ensure exact match
        book_obj = self.get_book_by_name(book)
        if not book_obj:
            return None
            
        with self.get_session() as session:
            return (
                session.query(Verse)
                .filter(
                    Verse.book_id == book_obj.id,
                    Verse.chapter == chapter,
                    Verse.verse == verse,
                    Verse.translation == translation,
                )
                .first()
            )

    def get_verses(
        self,
        book: str,
        chapter: int,
        start_verse: int = 1,
        end_verse: Optional[int] = None,
        translation: str = "BBE",
    ) -> List[Verse]:
        """Get multiple verses."""
        # Get the book first to ensure exact match
        book_obj = self.get_book_by_name(book)
        if not book_obj:
            return []
            
        with self.get_session() as session:
            query = (
                session.query(Verse)
                .filter(
                    Verse.book_id == book_obj.id,
                    Verse.chapter == chapter,
                    Verse.verse >= start_verse,
                    Verse.translation == translation,
                )
            )
            if end_verse:
                query = query.filter(Verse.verse <= end_verse)
            return query.order_by(Verse.verse).all()

    def get_chapter(self, book: str, chapter: int, translation: str = "BBE") -> List[Verse]:
        """Get all verses in a chapter."""
        # Get the book first to ensure exact match
        book_obj = self.get_book_by_name(book)
        if not book_obj:
            return []
            
        with self.get_session() as session:
            return (
                session.query(Verse)
                .filter(
                    Verse.book_id == book_obj.id,
                    Verse.chapter == chapter,
                    Verse.translation == translation,
                )
                .order_by(Verse.verse)
                .all()
            )

    def search_verses(
        self,
        query: str,
        translation: str = "BBE",
        exact: bool = False,
        case_sensitive: bool = False,
        limit: int = 50,
    ) -> List[Verse]:
        """Search for verses containing query."""
        with self.get_session() as session:
            search_query = session.query(Verse).filter(Verse.translation == translation)

            if exact:
                if case_sensitive:
                    search_query = search_query.filter(Verse.text.contains(query))
                else:
                    search_query = search_query.filter(Verse.text.ilike(f"%{query}%"))
            else:
                if case_sensitive:
                    search_query = search_query.filter(Verse.text.contains(query))
                else:
                    search_query = search_query.filter(Verse.text.ilike(f"%{query}%"))

            return search_query.limit(limit).all()

    def get_random_verse(self, translation: str = "BBE") -> Optional[Verse]:
        """Get a random verse."""
        with self.get_session() as session:
            return (
                session.query(Verse)
                .filter(Verse.translation == translation)
                .order_by(func.random())
                .first()
            )

    def add_bookmark(self, verse_id: int, name: Optional[str] = None, notes: Optional[str] = None) -> Bookmark:
        """Add a bookmark."""
        with self.get_session() as session:
            bookmark = Bookmark(verse_id=verse_id, name=name, notes=notes)
            session.add(bookmark)
            session.commit()
            session.refresh(bookmark)
            return bookmark

    def get_bookmarks(self) -> List[Bookmark]:
        """Get all bookmarks."""
        with self.get_session() as session:
            return (
                session.query(Bookmark)
                .order_by(Bookmark.created_at.desc())
                .all()
            )

    def add_reading_history(self, verse_id: int, duration_seconds: Optional[int] = None) -> ReadingHistory:
        """Add reading history entry."""
        with self.get_session() as session:
            history = ReadingHistory(verse_id=verse_id, duration_seconds=duration_seconds)
            session.add(history)
            session.commit()
            session.refresh(history)
            return history

    def get_reading_history(self, limit: int = 50) -> List[ReadingHistory]:
        """Get reading history."""
        with self.get_session() as session:
            return (
                session.query(ReadingHistory)
                .order_by(ReadingHistory.timestamp.desc())
                .limit(limit)
                .all()
            )

    def get_books(self) -> List[Book]:
        """Get all books."""
        with self.get_session() as session:
            return session.query(Book).order_by(Book.order).all()

    def get_book_by_name(self, name: str) -> Optional[Book]:
        """Get book by name or abbreviation."""
        with self.get_session() as session:
            # Try exact match first
            book = session.query(Book).filter(
                (Book.name.ilike(name)) | (Book.abbreviation.ilike(name))
            ).first()
            
            if book:
                return book
            
            # Try partial match, but prefer exact word matches
            books = session.query(Book).filter(
                (Book.name.ilike(f"%{name}%")) | (Book.abbreviation.ilike(f"%{name}%"))
            ).all()
            
            # Prefer books that start with the name or have exact word matches
            for book in books:
                if (book.name.lower().startswith(name.lower()) or 
                    book.abbreviation.lower().startswith(name.lower()) or
                    name.lower() in book.name.lower().split()):
                    return book
            
            # Return first match if no better match found
            return books[0] if books else None