"""MCP (Model Context Protocol) server for Bible CLI."""

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import uvicorn
from datetime import datetime

from .models import DatabaseManager, Verse, Book


# Pydantic models for API responses
class VerseResponse(BaseModel):
    """Response model for a single verse."""
    id: int
    reference: str
    text: str
    translation: str
    book: str
    chapter: int
    verse: int
    testament: str
    
    class Config:
        from_attributes = True


class BookResponse(BaseModel):
    """Response model for a book."""
    id: int
    name: str
    abbreviation: str
    testament: str
    order: int
    chapters: int
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Response model for search results."""
    query: str
    results: List[VerseResponse]
    total_count: int
    translation: str
    search_time: float


class ContextResponse(BaseModel):
    """Response model for verse with context."""
    main_verse: VerseResponse
    context_verses: List[VerseResponse]
    context_range: str


class BookmarkResponse(BaseModel):
    """Response model for bookmarks."""
    id: int
    verse: VerseResponse
    name: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class ExportRequest(BaseModel):
    """Request model for export operations."""
    reference: str
    translation: str = "NIV"
    format: str = Field(..., regex="^(json|xml|markdown|text)$")
    include_headers: bool = True
    include_verse_numbers: bool = True


class MCPServer:
    """MCP server for Bible CLI."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.app = FastAPI(
            title="Bible CLI MCP Server",
            description="Model Context Protocol server for Bible CLI",
            version="1.0.0"
        )
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/", response_model=Dict[str, str])
        async def root():
            """Root endpoint."""
            return {
                "message": "Bible CLI MCP Server",
                "version": "1.0.0",
                "endpoints": {
                    "verse": "/api/verse/{reference}",
                    "search": "/api/search",
                    "book": "/api/book/{book_name}",
                    "books": "/api/books",
                    "random": "/api/random",
                    "context": "/api/context/{reference}",
                    "export": "/api/export",
                    "bookmarks": "/api/bookmarks",
                    "stats": "/api/stats"
                }
            }
        
        @self.app.get("/api/verse/{reference}", response_model=VerseResponse)
        async def get_verse(
            reference: str,
            translation: str = Query(default="NIV", description="Bible translation")
        ):
            """Get a specific verse by reference."""
            try:
                # Parse reference (e.g., "John 3:16")
                parts = reference.split()
                if len(parts) < 2:
                    raise HTTPException(status_code=400, detail="Invalid reference format")
                
                book_name = parts[0]
                ref_part = parts[1]
                
                if ':' not in ref_part:
                    raise HTTPException(status_code=400, detail="Reference must include verse number")
                
                chapter_str, verse_str = ref_part.split(':')
                chapter = int(chapter_str)
                verse_num = int(verse_str)
                
                verse = self.db_manager.get_verse(book_name, chapter, verse_num, translation)
                if not verse:
                    raise HTTPException(status_code=404, detail="Verse not found")
                
                return VerseResponse(
                    id=verse.id,
                    reference=verse.reference,
                    text=verse.text,
                    translation=verse.translation,
                    book=verse.book.name,
                    chapter=verse.chapter,
                    verse=verse.verse,
                    testament=verse.book.testament
                )
            
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid reference format")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/search", response_model=SearchResponse)
        async def search_verses(
            q: str = Query(..., description="Search query"),
            translation: str = Query(default="NIV", description="Bible translation"),
            exact: bool = Query(default=False, description="Exact phrase matching"),
            case_sensitive: bool = Query(default=False, description="Case sensitive search"),
            book: Optional[str] = Query(default=None, description="Limit to specific book"),
            testament: Optional[str] = Query(default=None, description="Limit to testament"),
            limit: int = Query(default=50, ge=1, le=200, description="Maximum results")
        ):
            """Search for verses."""
            import time
            start_time = time.time()
            
            try:
                from .search import SearchEngine
                search_engine = SearchEngine(self.db_manager)
                
                results = search_engine.search(
                    query=q,
                    translation=translation,
                    exact=exact,
                    case_sensitive=case_sensitive,
                    book=book,
                    testament=testament,
                    limit=limit
                )
                
                search_time = time.time() - start_time
                
                verse_responses = [
                    VerseResponse(
                        id=verse.id,
                        reference=verse.reference,
                        text=verse.text,
                        translation=verse.translation,
                        book=verse.book.name,
                        chapter=verse.chapter,
                        verse=verse.verse,
                        testament=verse.book.testament
                    )
                    for verse in results
                ]
                
                return SearchResponse(
                    query=q,
                    results=verse_responses,
                    total_count=len(verse_responses),
                    translation=translation,
                    search_time=search_time
                )
            
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/books", response_model=List[BookResponse])
        async def get_books():
            """Get all books."""
            try:
                books = self.db_manager.get_books()
                return [
                    BookResponse(
                        id=book.id,
                        name=book.name,
                        abbreviation=book.abbreviation,
                        testament=book.testament,
                        order=book.order,
                        chapters=book.chapters
                    )
                    for book in books
                ]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/book/{book_name}", response_model=BookResponse)
        async def get_book(book_name: str):
            """Get a specific book."""
            try:
                book = self.db_manager.get_book_by_name(book_name)
                if not book:
                    raise HTTPException(status_code=404, detail="Book not found")
                
                return BookResponse(
                    id=book.id,
                    name=book.name,
                    abbreviation=book.abbreviation,
                    testament=book.testament,
                    order=book.order,
                    chapters=book.chapters
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/random", response_model=VerseResponse)
        async def get_random_verse(
            translation: str = Query(default="NIV", description="Bible translation")
        ):
            """Get a random verse."""
            try:
                verse = self.db_manager.get_random_verse(translation)
                if not verse:
                    raise HTTPException(status_code=404, detail="No verses found")
                
                return VerseResponse(
                    id=verse.id,
                    reference=verse.reference,
                    text=verse.text,
                    translation=verse.translation,
                    book=verse.book.name,
                    chapter=verse.chapter,
                    verse=verse.verse,
                    testament=verse.book.testament
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/context/{reference}", response_model=ContextResponse)
        async def get_verse_with_context(
            reference: str,
            translation: str = Query(default="NIV", description="Bible translation"),
            context: int = Query(default=3, ge=1, le=10, description="Number of context verses")
        ):
            """Get verse with surrounding context."""
            try:
                # Parse reference and get main verse
                parts = reference.split()
                if len(parts) < 2:
                    raise HTTPException(status_code=400, detail="Invalid reference format")
                
                book_name = parts[0]
                ref_part = parts[1]
                
                if ':' not in ref_part:
                    raise HTTPException(status_code=400, detail="Reference must include verse number")
                
                chapter_str, verse_str = ref_part.split(':')
                chapter = int(chapter_str)
                verse_num = int(verse_str)
                
                main_verse = self.db_manager.get_verse(book_name, chapter, verse_num, translation)
                if not main_verse:
                    raise HTTPException(status_code=404, detail="Verse not found")
                
                # Get context verses
                start_verse = max(1, verse_num - context)
                end_verse = verse_num + context
                
                context_verses = self.db_manager.get_verses(
                    book_name, chapter, start_verse, end_verse, translation
                )
                
                return ContextResponse(
                    main_verse=VerseResponse(
                        id=main_verse.id,
                        reference=main_verse.reference,
                        text=main_verse.text,
                        translation=main_verse.translation,
                        book=main_verse.book.name,
                        chapter=main_verse.chapter,
                        verse=main_verse.verse,
                        testament=main_verse.book.testament
                    ),
                    context_verses=[
                        VerseResponse(
                            id=verse.id,
                            reference=verse.reference,
                            text=verse.text,
                            translation=verse.translation,
                            book=verse.book.name,
                            chapter=verse.chapter,
                            verse=verse.verse,
                            testament=verse.book.testament
                        )
                        for verse in context_verses
                    ],
                    context_range=f"{start_verse}-{end_verse}"
                )
            
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid reference format")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/export")
        async def export_verses(request: ExportRequest):
            """Export verses in various formats."""
            try:
                # Parse reference and get verses
                parts = request.reference.split()
                if len(parts) < 2:
                    raise HTTPException(status_code=400, detail="Invalid reference format")
                
                book_name = parts[0]
                ref_part = parts[1]
                
                if ':' in ref_part:
                    chapter_str, verse_str = ref_part.split(':')
                    chapter = int(chapter_str)
                    
                    if '-' in verse_str:
                        start_verse, end_verse = map(int, verse_str.split('-'))
                        verses = self.db_manager.get_verses(
                            book_name, chapter, start_verse, end_verse, request.translation
                        )
                    else:
                        verse_num = int(verse_str)
                        verse = self.db_manager.get_verse(book_name, chapter, verse_num, request.translation)
                        verses = [verse] if verse else []
                else:
                    chapter = int(ref_part)
                    verses = self.db_manager.get_chapter(book_name, chapter, request.translation)
                
                if not verses:
                    raise HTTPException(status_code=404, detail="No verses found")
                
                # Export in requested format
                if request.format == "json":
                    return {
                        "reference": request.reference,
                        "translation": request.translation,
                        "verses": [
                            {
                                "reference": verse.reference,
                                "text": verse.text,
                                "book": verse.book.name,
                                "chapter": verse.chapter,
                                "verse": verse.verse if request.include_verse_numbers else None
                            }
                            for verse in verses
                        ]
                    }
                elif request.format == "markdown":
                    content = []
                    if request.include_headers:
                        content.append(f"# {verses[0].book.name} {verses[0].chapter}")
                        content.append("")
                    
                    for verse in verses:
                        if request.include_verse_numbers:
                            content.append(f"**{verse.verse}** {verse.text}")
                        else:
                            content.append(verse.text)
                    
                    return {"content": "\n".join(content)}
                elif request.format == "text":
                    content = []
                    for verse in verses:
                        if request.include_verse_numbers:
                            content.append(f"{verse.reference}: {verse.text}")
                        else:
                            content.append(verse.text)
                    
                    return {"content": "\n".join(content)}
                else:
                    raise HTTPException(status_code=400, detail="Unsupported format")
            
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid reference format")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/bookmarks", response_model=List[BookmarkResponse])
        async def get_bookmarks():
            """Get all bookmarks."""
            try:
                bookmarks = self.db_manager.get_bookmarks()
                return [
                    BookmarkResponse(
                        id=bookmark.id,
                        verse=VerseResponse(
                            id=bookmark.verse.id,
                            reference=bookmark.verse.reference,
                            text=bookmark.verse.text,
                            translation=bookmark.verse.translation,
                            book=bookmark.verse.book.name,
                            chapter=bookmark.verse.chapter,
                            verse=bookmark.verse.verse,
                            testament=bookmark.verse.book.testament
                        ),
                        name=bookmark.name,
                        notes=bookmark.notes,
                        created_at=bookmark.created_at,
                        updated_at=bookmark.updated_at
                    )
                    for bookmark in bookmarks
                ]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/stats")
        async def get_statistics():
            """Get Bible statistics."""
            try:
                from .search import SearchEngine
                search_engine = SearchEngine(self.db_manager)
                stats = search_engine.get_verse_statistics()
                
                return {
                    "database_stats": stats,
                    "server_info": {
                        "name": "Bible CLI MCP Server",
                        "version": "1.0.0",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))


def run_server(db_manager: DatabaseManager, host: str = "localhost", port: int = 8000):
    """Run the MCP server."""
    server = MCPServer(db_manager)
    uvicorn.run(server.app, host=host, port=port)