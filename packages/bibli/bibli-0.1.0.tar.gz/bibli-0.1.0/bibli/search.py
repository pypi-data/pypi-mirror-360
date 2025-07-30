"""Search functionality for Bible CLI."""

import re
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import Session, joinedload

from .models import DatabaseManager, Verse, Book


class SearchEngine:
    """Advanced search engine for Bible verses."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def search(
        self,
        query: str,
        translation: str = "NIV",
        exact: bool = False,
        case_sensitive: bool = False,
        book: Optional[str] = None,
        testament: Optional[str] = None,
        regex: bool = False,
        limit: int = 50,
    ) -> List[Verse]:
        """Search for verses matching the query."""
        with self.db_manager.get_session() as session:
            # Start with base query
            search_query = session.query(Verse).options(joinedload(Verse.book)).join(Book).filter(
                Verse.translation == translation
            )

            # Apply text search
            if regex:
                search_query = self._apply_regex_search(search_query, query, case_sensitive)
            elif exact:
                search_query = self._apply_exact_search(search_query, query, case_sensitive)
            else:
                search_query = self._apply_fuzzy_search(search_query, query, case_sensitive)

            # Apply book filter
            if book:
                search_query = search_query.filter(
                    or_(
                        Book.name.ilike(f"%{book}%"),
                        Book.abbreviation.ilike(f"%{book}%")
                    )
                )

            # Apply testament filter
            if testament:
                search_query = search_query.filter(Book.testament == testament)

            # Order by relevance (book order, then chapter, then verse)
            search_query = search_query.order_by(Book.order, Verse.chapter, Verse.verse)

            return search_query.limit(limit).all()

    def _apply_exact_search(self, query, search_term: str, case_sensitive: bool):
        """Apply exact phrase matching."""
        if case_sensitive:
            return query.filter(Verse.text.contains(search_term))
        else:
            return query.filter(Verse.text.ilike(f"%{search_term}%"))

    def _apply_fuzzy_search(self, query, search_term: str, case_sensitive: bool):
        """Apply fuzzy word matching."""
        words = search_term.split()
        
        if case_sensitive:
            conditions = [Verse.text.contains(word) for word in words]
        else:
            conditions = [Verse.text.ilike(f"%{word}%") for word in words]
        
        # All words must be present (AND logic)
        return query.filter(and_(*conditions))

    def _apply_regex_search(self, query, pattern: str, case_sensitive: bool):
        """Apply regex pattern matching."""
        if case_sensitive:
            return query.filter(Verse.text.op('REGEXP')(pattern))
        else:
            return query.filter(func.lower(Verse.text).op('REGEXP')(pattern.lower()))

    def search_with_context(
        self,
        query: str,
        context_verses: int = 2,
        translation: str = "NIV",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search with context verses around matches."""
        matches = self.search(query, translation=translation, **kwargs)
        results = []

        for match in matches:
            # Get context verses
            context_start = max(1, match.verse - context_verses)
            context_end = match.verse + context_verses
            
            context = self.db_manager.get_verses(
                match.book.name,
                match.chapter,
                context_start,
                context_end,
                translation
            )
            
            results.append({
                'match': match,
                'context': context,
                'match_verse': match.verse
            })

        return results

    def search_by_reference(self, reference: str, translation: str = "NIV") -> List[Verse]:
        """Search by Bible reference (e.g., 'John 3:16', 'Genesis 1:1-5')."""
        try:
            # Parse reference
            parts = reference.split()
            if len(parts) < 2:
                return []

            book_name = parts[0]
            ref_part = parts[1]

            # Handle chapter:verse format
            if ':' in ref_part:
                chapter_str, verse_str = ref_part.split(':')
                chapter = int(chapter_str)
                
                if '-' in verse_str:
                    # Range of verses
                    start_verse, end_verse = map(int, verse_str.split('-'))
                    return self.db_manager.get_verses(
                        book_name, chapter, start_verse, end_verse, translation
                    )
                else:
                    # Single verse
                    verse = int(verse_str)
                    result = self.db_manager.get_verse(book_name, chapter, verse, translation)
                    return [result] if result else []
            else:
                # Entire chapter
                chapter = int(ref_part)
                return self.db_manager.get_chapter(book_name, chapter, translation)

        except (ValueError, IndexError):
            return []

    def get_cross_references(self, verse: Verse) -> List[Verse]:
        """Get cross-references for a verse (simplified implementation)."""
        # This is a simplified version - in a full implementation, 
        # you'd have a cross-reference database
        
        # For now, search for verses with similar keywords
        keywords = self._extract_keywords(verse.text)
        if not keywords:
            return []

        # Search for verses containing similar keywords
        results = []
        for keyword in keywords[:3]:  # Limit to top 3 keywords
            matches = self.search(
                keyword,
                translation=verse.translation,
                exact=False,
                limit=5
            )
            # Filter out the original verse
            matches = [v for v in matches if v.id != verse.id]
            results.extend(matches)

        # Remove duplicates and limit results
        seen = set()
        unique_results = []
        for result in results:
            if result.id not in seen:
                seen.add(result.id)
                unique_results.append(result)

        return unique_results[:10]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from verse text."""
        # Remove common words
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'his', 'her', 'him', 'she',
            'they', 'their', 'them', 'this', 'these', 'those', 'you', 'your',
            'i', 'me', 'my', 'we', 'our', 'us', 'but', 'not', 'no', 'all',
            'any', 'can', 'had', 'have', 'if', 'into', 'may', 'more', 'must',
            'said', 'shall', 'should', 'so', 'than', 'up', 'who', 'would'
        }

        # Extract words (remove punctuation)
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Return unique keywords
        return list(set(keywords))

    def get_verse_statistics(self, translation: str = "NIV") -> Dict[str, Any]:
        """Get statistics about verses in the database."""
        with self.db_manager.get_session() as session:
            total_verses = session.query(Verse).filter(Verse.translation == translation).count()
            total_books = session.query(Book).count()
            old_testament_books = session.query(Book).filter(Book.testament == 'old').count()
            new_testament_books = session.query(Book).filter(Book.testament == 'new').count()

            return {
                'total_verses': total_verses,
                'total_books': total_books,
                'old_testament_books': old_testament_books,
                'new_testament_books': new_testament_books,
                'translation': translation
            }

    def find_similar_verses(self, verse: Verse, limit: int = 10) -> List[Verse]:
        """Find verses similar to the given verse."""
        # Extract keywords from the verse
        keywords = self._extract_keywords(verse.text)
        if not keywords:
            return []

        # Search for verses containing these keywords
        with self.db_manager.get_session() as session:
            # Create a query that scores verses by keyword matches
            conditions = []
            for keyword in keywords:
                conditions.append(Verse.text.ilike(f"%{keyword}%"))

            if not conditions:
                return []

            # Find verses that match any of the keywords
            similar_verses = (
                session.query(Verse)
                .filter(
                    and_(
                        Verse.translation == verse.translation,
                        Verse.id != verse.id,  # Exclude the original verse
                        or_(*conditions)
                    )
                )
                .limit(limit)
                .all()
            )

            return similar_verses