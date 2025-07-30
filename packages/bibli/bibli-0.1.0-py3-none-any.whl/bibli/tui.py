"""Terminal User Interface for Bible CLI using Textual."""

from typing import Optional, List
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Input, Button, Static, Tree, ListView, ListItem, 
    Label, RichLog, Tabs, Tab, TabbedContent, TabPane
)
from textual.reactive import reactive
from textual.message import Message
from textual.binding import Binding
from textual.screen import Screen
from rich.text import Text
from rich.panel import Panel

from .models import DatabaseManager, Verse, Book
from .search import SearchEngine
from .config import Config


class VerseDisplay(ScrollableContainer):
    """Widget for displaying Bible verses."""
    
    def __init__(self, verses: List[Verse] = None, **kwargs):
        super().__init__(**kwargs)
        self.verses = verses or []
        self.current_index = 0
    
    def set_verses(self, verses: List[Verse]) -> None:
        """Set the verses to display."""
        self.verses = verses
        self.current_index = 0
        
        self.remove_children()

        if not self.verses:
            self.mount(Static("No verses to display"))
            return

        for i, verse in enumerate(self.verses):
            reference = f"{verse.book.name} {verse.chapter}:{verse.verse}"
            verse_text = f"[bold]{reference}[/bold]\n{verse.text}\n"
            self.mount(Static(Text.from_markup(verse_text), id=f"verse-{i}"))
        
        self.update_display()

    def set_message(self, message: str) -> None:
        """Display a simple message."""
        self.verses = []
        self.current_index = 0
        self.remove_children()
        self.mount(Static(message))

    def update_display(self) -> None:
        """Update the display with current verses."""
        if not self.verses:
            self.remove_children()
            self.mount(Static("No verses to display"))
            return

        # Update existing verse widgets instead of recreating them
        for i, verse in enumerate(self.verses):
            verse_widget = self.query_one(f"#verse-{i}", Static)
            reference = f"{verse.book.name} {verse.chapter}:{verse.verse}"
            
            if i == self.current_index:
                verse_text = f"[bold cyan]>>> {reference} <<<[/bold cyan]\n{verse.text}\n"
                verse_widget.update(Text.from_markup(verse_text))
                self.scroll_to_widget(verse_widget, animate=False, top=True)
            else:
                verse_text = f"[bold]{reference}[/bold]\n{verse.text}\n"
                verse_widget.update(Text.from_markup(verse_text))
    
    def next_verse(self) -> None:
        """Move to next verse."""
        if self.verses and self.current_index < len(self.verses) - 1:
            self.current_index += 1
            self.update_display()
    
    def prev_verse(self) -> None:
        """Move to previous verse."""
        if self.verses and self.current_index > 0:
            self.current_index -= 1
            self.update_display()


class BrowseWidget(Container):
    """Widget for browsing books and chapters."""

    def __init__(self, db_manager: DatabaseManager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        self.current_book: Optional[Book] = None

    def compose(self) -> ComposeResult:
        """Compose the browse widget."""
        with Vertical():
            yield Static("Select a Book:", classes="label")
            yield ListView(
                *[ListItem(Label(book.name), name=book.name) for book in self.db_manager.get_books()],
                id="book-list"
            )
            yield Static("Select a Chapter:", classes="label")
            yield ListView(id="chapter-list")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list view selections."""
        if event.list_view.id == "book-list":
            book_name = event.item.name
            book = self.db_manager.get_book_by_name(book_name)
            if book:
                self.current_book = book
                self.update_chapter_list(book)
                self.post_message(BookSelected(book_name))
        elif event.list_view.id == "chapter-list":
            if self.current_book:
                book_name = self.current_book.name
                chapter_num = int(event.item.name)
                self.post_message(ChapterSelected(book_name, chapter_num))

    def update_chapter_list(self, book: Book) -> None:
        """Update the chapter list for the selected book."""
        chapter_list = self.query_one("#chapter-list", ListView)
        chapter_list.clear()

        if book.chapters == 0:
            chapter_list.append(ListItem(Label(f"No chapters found for {book.name}"), name="0"))
        else:
            for i in range(1, book.chapters + 1):
                chapter_list.append(ListItem(Label(f"Chapter {i}"), name=str(i)))


class BookSelector(Container):
    """Widget for selecting Bible books."""
    
    def __init__(self, db_manager: DatabaseManager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
    
    def compose(self) -> ComposeResult:
        """Compose the book selector."""
        with Vertical():
            yield Static("Select a Book:", classes="label")
            yield ListView(
                *[ListItem(Label(book.name), name=book.name) for book in self.db_manager.get_books()],
                id="book-list"
            )
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle book selection."""
        if event.list_view.id == "book-list":
            book_name = event.item.name
            self.post_message(BookSelected(book_name))


class ChapterSelector(Container):
    """Widget for selecting chapters."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_book = None
    
    def compose(self) -> ComposeResult:
        """Compose the chapter selector."""
        with Vertical():
            yield Static("Select a Chapter:", classes="label")
            yield ListView(id="chapter-list")
    
    def set_book(self, book: Book) -> None:
        """Set the current book and update chapters."""
        self.current_book = book
        chapter_list = self.query_one("#chapter-list", ListView)
        chapter_list.clear()
        
        if book.chapters == 0:
            # Show debug message if no chapters
            chapter_list.append(ListItem(Label(f"No chapters found for {book.name}"), name="0"))
        else:
            for i in range(1, book.chapters + 1):
                chapter_list.append(ListItem(Label(f"Chapter {i}"), name=str(i)))
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle chapter selection."""
        if event.list_view.id == "chapter-list":
            chapter_num = int(event.item.name)
            self.post_message(ChapterSelected(self.current_book.name, chapter_num))


class SearchWidget(Container):
    """Widget for searching Bible verses."""
    
    def __init__(self, search_engine: SearchEngine, **kwargs):
        super().__init__(**kwargs)
        self.search_engine = search_engine
    
    def compose(self) -> ComposeResult:
        """Compose the search widget."""
        with Vertical():
            yield Static("Search Verses:", classes="label")
            with Horizontal():
                yield Input(placeholder="Enter search query...", id="search-input")
                yield Button("Search", id="search-button")
            yield ListView(id="search-results")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle search button press."""
        if event.button.id == "search-button":
            self.perform_search()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search input submission."""
        if event.input.id == "search-input":
            self.perform_search()
    
    def perform_search(self) -> None:
        """Perform the search."""
        search_input = self.query_one("#search-input", Input)
        query = search_input.value.strip()
        
        if not query:
            return
        
        results = self.search_engine.search(query, limit=20)
        results_list = self.query_one("#search-results", ListView)
        results_list.clear()
        
        for verse in results:
            reference = f"{verse.book.name} {verse.chapter}:{verse.verse}"
            preview = verse.text[:100] + "..." if len(verse.text) > 100 else verse.text
            results_list.append(
                ListItem(
                    Label(f"[bold]{reference}[/bold]\n{preview}"),
                    name=f"{verse.book.name}:{verse.chapter}:{verse.verse}"
                )
            )
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle search result selection."""
        if event.list_view.id == "search-results":
            # Parse the reference from the name
            parts = event.item.name.split(":")
            if len(parts) == 3:
                book_name, chapter, verse = parts
                self.post_message(VerseSelected(book_name, int(chapter), int(verse)))


class BookmarkWidget(Container):
    """Widget for managing bookmarks."""
    
    def __init__(self, db_manager: DatabaseManager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
    
    def compose(self) -> ComposeResult:
        """Compose the bookmark widget."""
        with Vertical():
            yield Static("Bookmarks:", classes="label")
            yield ListView(id="bookmark-list")
            yield Button("Refresh", id="refresh-bookmarks")
    
    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self.refresh_bookmarks()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "refresh-bookmarks":
            self.refresh_bookmarks()
    
    def refresh_bookmarks(self) -> None:
        """Refresh the bookmark list."""
        bookmarks = self.db_manager.get_bookmarks()
        bookmark_list = self.query_one("#bookmark-list", ListView)
        bookmark_list.clear()
        
        for bookmark in bookmarks:
            reference = bookmark.verse.reference
            name = bookmark.name or "Untitled"
            bookmark_list.append(
                ListItem(
                    Label(f"[bold]{reference}[/bold]\n{name}"),
                    name=f"{bookmark.verse.book.name}:{bookmark.verse.chapter}:{bookmark.verse.verse}"
                )
            )
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle bookmark selection."""
        if event.list_view.id == "bookmark-list":
            # Parse the reference from the name
            parts = event.item.name.split(":")
            if len(parts) == 3:
                book_name, chapter, verse = parts
                self.post_message(VerseSelected(book_name, int(chapter), int(verse)))


class BibleApp(App):
    """Main Bible TUI application."""
    
    TITLE = "Bible CLI"
    
    CSS = """
    .sidebar {
        width: 30%;
        dock: left;
        border: solid $primary;
    }
    
    .main-content {
        width: 70%;
        dock: right;
        border: solid $accent;
    }
    
    .label {
        text-style: bold;
        color: $text;
        background: $surface;
        padding: 1;
    }
    
    ListView {
        border: solid $primary;
        scrollbar-size: 1 1;
    }
    
    ListItem {
        padding: 0 1;
    }
    
    ListItem:hover {
        background: $primary 20%;
    }
    
    ListItem.-selected {
        background: $accent;
        color: $text;
    }
    
    Input {
        border: solid $primary;
        background: $surface;
    }
    
    Input:focus {
        border: solid $accent;
    }
    
    Button {
        border: solid $primary;
        background: $surface;
        color: $text;
        margin: 0 1;
    }
    
    Button:hover {
        background: $primary;
        color: $text;
    }
    
    Button:focus {
        border: solid $accent;
    }
    
    Static {
        color: $text;
        background: $background;
    }
    
    #verse-display {
        padding: 1;
        background: $surface;
        border: solid $accent;
    }
    
    #search-verse-display {
        padding: 1;
        background: $surface;
        border: solid $accent;
    }
    
    #bookmark-verse-display {
        padding: 1;
        background: $surface;
        border: solid $accent;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit"),
        Binding("/", "focus_search", "Search"),
        Binding("g", "goto", "Go to verse"),
        Binding("r", "random", "Random verse"),
        Binding("b", "bookmark", "Bookmark"),
        Binding("j", "next_verse", "Next verse"),
        Binding("k", "prev_verse", "Previous verse"),
        Binding("?", "help", "Help"),
    ]
    
    def __init__(self, db_manager: DatabaseManager, config: Config, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        self.config = config
        self.search_engine = SearchEngine(db_manager)
        self.current_verses: List[Verse] = []
    
    def compose(self) -> ComposeResult:
        """Compose the main application."""
        yield Header()
        
        with TabbedContent(initial="browse"):
            with TabPane("Browse", id="browse"):
                with Horizontal():
                    yield BrowseWidget(self.db_manager, classes="sidebar")
                    yield VerseDisplay(id="verse-display", classes="main-content")
            
            with TabPane("Search", id="search"):
                with Horizontal():
                    yield SearchWidget(self.search_engine, classes="sidebar")
                    yield VerseDisplay(id="search-verse-display", classes="main-content")
            
            with TabPane("Bookmarks", id="bookmarks"):
                with Horizontal():
                    yield BookmarkWidget(self.db_manager, classes="sidebar")
                    yield VerseDisplay(id="bookmark-verse-display", classes="main-content")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Test if database has verses
        with self.db_manager.get_session() as session:
            verse_count = session.query(Verse).count()
            book_count = session.query(Book).count()
        
        if verse_count == 0:
            # Show error message
            verse_display = self.query_one("#verse-display", VerseDisplay)
            verse_display.set_message(f"Database is empty. No verses found.\nBooks: {book_count}, Verses: {verse_count}")
        else:
            # Show a random verse on startup
            verse_display = self.query_one("#verse-display", VerseDisplay)
            verse_display.set_message(f"Bible CLI loaded successfully!\nBooks: {book_count}, Verses: {verse_count}\n\nPress a book to start reading or 'r' for random verse.")
            # self.action_random()
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_focus_search(self) -> None:
        """Focus on search input."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "search"
        search_input = self.query_one("#search-input", Input)
        search_input.focus()
    
    def action_goto(self) -> None:
        """Go to a specific verse."""
        # This would typically open a dialog for input
        # For now, we'll just focus on the search
        self.action_focus_search()
    
    def action_random(self) -> None:
        """Show a random verse."""
        verse = self.db_manager.get_random_verse()
        if verse:
            self.current_verses = [verse]
            self.update_verse_display()
            self.db_manager.add_reading_history(verse.id)
    
    def action_bookmark(self) -> None:
        """Bookmark the current verse."""
        tabs = self.query_one(TabbedContent)

        if tabs.active == "browse":
            verse_display = self.query_one("#verse-display", VerseDisplay)
        elif tabs.active == "search":
            verse_display = self.query_one("#search-verse-display", VerseDisplay)
        else:  # "bookmarks"
            verse_display = self.query_one("#bookmark-verse-display", VerseDisplay)

        if verse_display.verses:
            verse = verse_display.verses[verse_display.current_index]
            self.db_manager.add_bookmark(verse.id)
            self.notify(f"Bookmarked {verse.reference}")
    
    def action_next_verse(self) -> None:
        """Move to next verse."""
        tabs = self.query_one(TabbedContent)
        if tabs.active == "browse":
            verse_display = self.query_one("#verse-display", VerseDisplay)
        elif tabs.active == "search":
            verse_display = self.query_one("#search-verse-display", VerseDisplay)
        else:
            verse_display = self.query_one("#bookmark-verse-display", VerseDisplay)
        verse_display.next_verse()

    def action_prev_verse(self) -> None:
        """Move to previous verse."""
        tabs = self.query_one(TabbedContent)
        if tabs.active == "browse":
            verse_display = self.query_one("#verse-display", VerseDisplay)
        elif tabs.active == "search":
            verse_display = self.query_one("#search-verse-display", VerseDisplay)
        else:
            verse_display = self.query_one("#bookmark-verse-display", VerseDisplay)
        verse_display.prev_verse()
    
    def action_help(self) -> None:
        """Show help."""
        help_text = """
Bible CLI Keyboard Shortcuts:

Navigation:
  j/k or ↓/↑  - Navigate verses
  h/l or ←/→  - Previous/Next chapter
  Space/b     - Page down/up

Commands:
  g           - Go to verse
  /           - Search
  r           - Random verse
  m           - Bookmark current verse
  ?           - Show this help
  q           - Quit

Tabs:
  Use mouse or arrow keys to switch between Browse, Search, and Bookmarks
"""
        self.notify(help_text)
    
    def update_verse_display(self) -> None:
        """Update the verse display with current verses."""
        # Get the active tab and update the appropriate display
        tabs = self.query_one(TabbedContent)
        if tabs.active == "browse":
            verse_display = self.query_one("#verse-display", VerseDisplay)
        elif tabs.active == "search":
            verse_display = self.query_one("#search-verse-display", VerseDisplay)
        else:
            verse_display = self.query_one("#bookmark-verse-display", VerseDisplay)
        
        verse_display.set_verses(self.current_verses)
    
    def on_chapter_selected(self, event: "ChapterSelected") -> None:
        """Handle chapter selection."""
        verses = self.db_manager.get_chapter(event.book_name, event.chapter)
        if verses:
            self.current_verses = verses
            self.update_verse_display()
            # Add first verse to reading history
            self.db_manager.add_reading_history(verses[0].id)
        else:
            # Show debug message if no verses found
            self.current_verses = []
            verse_display = self.query_one("#verse-display", VerseDisplay)
            verse_display.set_message(f"No verses found for {event.book_name} chapter {event.chapter}")
    
    def on_verse_selected(self, event: "VerseSelected") -> None:
        """Handle verse selection."""
        verse = self.db_manager.get_verse(event.book_name, event.chapter, event.verse)
        if verse:
            self.current_verses = [verse]
            self.update_verse_display()
            self.db_manager.add_reading_history(verse.id)


# Custom messages
class BookSelected(Message):
    """Message sent when a book is selected."""
    
    def __init__(self, book_name: str):
        self.book_name = book_name
        super().__init__()


class ChapterSelected(Message):
    """Message sent when a chapter is selected."""
    
    def __init__(self, book_name: str, chapter: int):
        self.book_name = book_name
        self.chapter = chapter
        super().__init__()


class VerseSelected(Message):
    """Message sent when a verse is selected."""
    
    def __init__(self, book_name: str, chapter: int, verse: int):
        self.book_name = book_name
        self.chapter = chapter
        self.verse = verse
        super().__init__()


def run_tui(db_manager: DatabaseManager, config: Config) -> None:
    """Run the TUI application."""
    app = BibleApp(db_manager, config)
    app.run()