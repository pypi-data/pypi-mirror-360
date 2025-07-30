"""Command-line interface for Bible CLI."""

import click
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from bibli.data_import import import_bible_data
from bibli.models import DatabaseManager
from bibli.tui import run_tui
from bibli.config import Config


console = Console()


@click.group(invoke_without_command=True)
@click.option('--config', type=click.Path(exists=True), help='Path to config file')
@click.option('--db', type=click.Path(), help='Database file path')
@click.pass_context
def main(ctx: click.Context, config: Optional[str], db: Optional[str]) -> None:
    """Bible CLI - A command-line interface for Bible reading and study."""
    
    # Initialize configuration
    config_obj = Config(config_file=config)
    
    # Initialize database
    db_path = db or config_obj.get_database_path()
    db_manager = DatabaseManager(f"sqlite:///{db_path}")
    
    # Store in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['config'] = config_obj
    ctx.obj['db_manager'] = db_manager
    
    # Initialize database if needed
    try:
        initialize_database(db_manager)
    except Exception as e:
        console.print(f"[red]Error initializing database: {e}[/red]")
        return
    
    # If no subcommand is given, run interactive mode
    if ctx.invoked_subcommand is None:
        run_tui(db_manager, config_obj)


@main.command()
@click.argument('book')
@click.argument('reference')
@click.option('--translation', '-t', default='BBE', help='Bible translation')
@click.option('--context', '-c', type=int, help='Number of context verses')
@click.option('--interactive', '-i', is_flag=True, help='Interactive navigation mode')
@click.pass_context
def read(ctx: click.Context, book: str, reference: str, translation: str, context: Optional[int], interactive: bool) -> None:
    """Read specific verse(s) or chapter.
    
    Examples:
      bible read john 3:16
      bible read genesis 1:1-5
      bible read psalms 23
      bible read john 3:16 --interactive  (navigate with n/p/g/b/q)
    """
    db_manager = ctx.obj['db_manager']
    
    try:
        # Parse reference (chapter:verse or just chapter)
        if ':' in reference:
            chapter_str, verse_str = reference.split(':')
            chapter = int(chapter_str)
            
            if '-' in verse_str:
                # Range of verses
                start_verse, end_verse = map(int, verse_str.split('-'))
                verses = db_manager.get_verses(book, chapter, start_verse, end_verse, translation)
                if interactive:
                    run_interactive_reader(db_manager, book, chapter, start_verse, translation)
                    return
            else:
                # Single verse
                verse_num = int(verse_str)
                if interactive:
                    run_interactive_reader(db_manager, book, chapter, verse_num, translation)
                    return
                verses = [db_manager.get_verse(book, chapter, verse_num, translation)]
                verses = [v for v in verses if v is not None]
        else:
            # Entire chapter
            chapter = int(reference)
            if interactive:
                run_interactive_reader(db_manager, book, chapter, 1, translation)
                return
            verses = db_manager.get_chapter(book, chapter, translation)
        
        if not verses:
            console.print(f"[red]No verses found for {book} {reference}[/red]")
            return
        
        # Add context if requested
        if context and len(verses) == 1:
            verse = verses[0]
            start_verse = max(1, verse.verse - context)
            end_verse = verse.verse + context
            verses = db_manager.get_verses(book, verse.chapter, start_verse, end_verse, translation)
        
        # Display verses
        for verse in verses:
            if verse:
                display_verse(verse, highlight_verse=verses[0].verse if context else None)
                
        # Add to reading history
        for verse in verses:
            if verse:
                db_manager.add_reading_history(verse.id)
                
    except ValueError:
        console.print(f"[red]Invalid reference format: {reference}[/red]")
    except Exception as e:
        console.print(f"[red]Error reading verse: {e}[/red]")


@main.command()
@click.argument('query')
@click.option('--exact', is_flag=True, help='Exact phrase matching')
@click.option('--case-sensitive', is_flag=True, help='Case-sensitive search')
@click.option('--book', help='Limit search to specific book')
@click.option('--testament', type=click.Choice(['old', 'new']), help='Limit to testament')
@click.option('--context', '-c', type=int, default=0, help='Show n verses of context')
@click.option('--translation', '-t', default='BBE', help='Bible translation')
@click.option('--limit', '-l', type=int, default=20, help='Maximum number of results')
@click.pass_context
def search(ctx: click.Context, query: str, exact: bool, case_sensitive: bool, 
           book: Optional[str], testament: Optional[str], context: int, 
           translation: str, limit: int) -> None:
    """Search for words or phrases in the Bible."""
    db_manager = ctx.obj['db_manager']
    search_engine = SearchEngine(db_manager)
    
    try:
        results = search_engine.search(
            query=query,
            translation=translation,
            exact=exact,
            case_sensitive=case_sensitive,
            book=book,
            testament=testament,
            limit=limit
        )
        
        if not results:
            console.print(f"[yellow]No results found for '{query}'[/yellow]")
            return
        
        console.print(f"[green]Found {len(results)} results for '{query}'[/green]\n")
        
        for i, verse in enumerate(results, 1):
            # Get context verses if requested
            if context > 0:
                context_verses = db_manager.get_verses(
                    verse.book.name, 
                    verse.chapter, 
                    max(1, verse.verse - context),
                    verse.verse + context,
                    translation
                )
                
                console.print(f"[bold cyan]Result {i}:[/bold cyan]")
                for ctx_verse in context_verses:
                    display_verse(ctx_verse, highlight_verse=verse.verse, search_query=query)
                console.print()
            else:
                console.print(f"[bold cyan]Result {i}:[/bold cyan]")
                display_verse(verse, search_query=query)
                console.print()
                
    except Exception as e:
        console.print(f"[red]Error searching: {e}[/red]")


@main.command()
@click.argument('reference')
@click.option('--interactive', '-i', is_flag=True, help='Interactive navigation mode')
@click.pass_context
def goto(ctx: click.Context, reference: str, interactive: bool) -> None:
    """Jump directly to a reference."""
    # Parse reference like "john 3:16"
    parts = reference.split()
    if len(parts) >= 2:
        book = parts[0]
        ref = parts[1]
        ctx.invoke(read, book=book, reference=ref, interactive=interactive)
    else:
        console.print(f"[red]Invalid reference format: {reference}[/red]")


@main.command()
@click.option('--translation', '-t', default='BBE', help='Bible translation')
@click.pass_context
def random(ctx: click.Context, translation: str) -> None:
    """Display a random verse."""
    db_manager = ctx.obj['db_manager']
    
    try:
        verse = db_manager.get_random_verse(translation)
        if verse:
            display_verse(verse)
            db_manager.add_reading_history(verse.id)
        else:
            console.print("[red]No verses found[/red]")
    except Exception as e:
        console.print(f"[red]Error getting random verse: {e}[/red]")


@main.command()
@click.pass_context
def daily(ctx: click.Context) -> None:
    """Show verse of the day."""
    # For now, just show a random verse
    # In the future, this could be based on date or a predefined schedule
    ctx.invoke(random)


@main.command()
@click.pass_context
def bookmarks(ctx: click.Context) -> None:
    """List saved bookmarks."""
    db_manager = ctx.obj['db_manager']
    
    try:
        bookmarks = db_manager.get_bookmarks()
        if not bookmarks:
            console.print("[yellow]No bookmarks found[/yellow]")
            return
        
        table = Table(title="Bookmarks")
        table.add_column("Reference", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Date", style="yellow")
        
        for bookmark in bookmarks:
            table.add_row(
                bookmark.verse.reference,
                bookmark.name or "Untitled",
                bookmark.created_at.strftime("%Y-%m-%d %H:%M")
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing bookmarks: {e}[/red]")


@main.group()
def bookmark() -> None:
    """Bookmark management commands."""
    pass


@bookmark.command('add')
@click.argument('reference')
@click.option('--name', '-n', help='Bookmark name')
@click.option('--notes', help='Bookmark notes')
@click.pass_context
def add_bookmark(ctx: click.Context, reference: str, name: Optional[str], notes: Optional[str]) -> None:
    """Add a bookmark."""
    db_manager = ctx.obj['db_manager']
    
    try:
        # Parse reference
        parts = reference.split()
        if len(parts) >= 2:
            book = parts[0]
            ref_parts = parts[1].split(':')
            chapter = int(ref_parts[0])
            verse = int(ref_parts[1]) if len(ref_parts) > 1 else 1
            
            verse_obj = db_manager.get_verse(book, chapter, verse)
            if verse_obj:
                bookmark = db_manager.add_bookmark(verse_obj.id, name, notes)
                console.print(f"[green]Bookmark added: {bookmark.verse.reference}[/green]")
            else:
                console.print(f"[red]Verse not found: {reference}[/red]")
        else:
            console.print(f"[red]Invalid reference format: {reference}[/red]")
            
    except Exception as e:
        console.print(f"[red]Error adding bookmark: {e}[/red]")


@main.command()
@click.option('--limit', '-l', type=int, default=20, help='Number of entries to show')
@click.pass_context
def history(ctx: click.Context, limit: int) -> None:
    """Show reading history."""
    db_manager = ctx.obj['db_manager']
    
    try:
        history = db_manager.get_reading_history(limit)
        if not history:
            console.print("[yellow]No reading history found[/yellow]")
            return
        
        table = Table(title="Reading History")
        table.add_column("Reference", style="cyan")
        table.add_column("Date", style="yellow")
        table.add_column("Time", style="green")
        
        for entry in history:
            table.add_row(
                entry.verse.reference,
                entry.timestamp.strftime("%Y-%m-%d"),
                entry.timestamp.strftime("%H:%M:%S")
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error showing history: {e}[/red]")


@main.command()
@click.pass_context
def interactive(ctx: click.Context) -> None:
    """Launch interactive TUI mode."""
    db_manager = ctx.obj['db_manager']
    config = ctx.obj['config']
    run_tui(db_manager, config)


@main.command()
@click.argument('book')
@click.argument('reference')
@click.option('--translation', '-t', default='BBE', help='Bible translation')
@click.pass_context
def nav(ctx: click.Context, book: str, reference: str, translation: str) -> None:
    """Navigate Bible interactively (shortcut for read --interactive)."""
    ctx.invoke(read, book=book, reference=reference, translation=translation, interactive=True)


@main.group()
def mcp() -> None:
    """MCP (Model Context Protocol) commands."""
    pass


@mcp.command('serve')
@click.option('--port', type=int, default=8000, help='Port to serve on')
@click.option('--host', default='localhost', help='Host to serve on')
@click.pass_context
def serve_mcp(ctx: click.Context, port: int, host: str) -> None:
    """Start MCP server."""
    try:
        from .mcp_server import run_server
        db_manager = ctx.obj['db_manager']
        run_server(db_manager, host, port)
    except ImportError:
        console.print("[red]MCP server dependencies not installed[/red]")
    except Exception as e:
        console.print(f"[red]Error starting MCP server: {e}[/red]")


def display_verse(verse, highlight_verse: Optional[int] = None, search_query: Optional[str] = None) -> None:
    """Display a verse with formatting."""
    reference = f"{verse.book.name} {verse.chapter}:{verse.verse}"
    
    # Highlight search query if provided
    text = verse.text
    if search_query:
        # Simple highlighting - replace with rich markup
        text = text.replace(search_query, f"[bold yellow]{search_query}[/bold yellow]")
    
    # Style based on whether this is the highlighted verse
    if highlight_verse and verse.verse == highlight_verse:
        style = "bold cyan"
    else:
        style = "white"
    
    verse_panel = Panel(
        Text(text, style=style),
        title=f"[bold]{reference}[/bold]",
        border_style="blue" if highlight_verse and verse.verse == highlight_verse else "dim"
    )
    
    console.print(verse_panel)


def run_interactive_reader(db_manager, book_name: str, start_chapter: int, start_verse: int, translation: str = "BBE") -> None:
    """Run interactive verse reader with simple command navigation."""
    from rich.panel import Panel
    from rich.text import Text
    
    # Get book info
    book = db_manager.get_book_by_name(book_name)
    if not book:
        console.print(f"[red]Book not found: {book_name}[/red]")
        return
    
    current_chapter = start_chapter
    current_verse = start_verse
    
    def get_max_verse_in_chapter():
        """Get the maximum verse number in current chapter."""
        verses = db_manager.get_chapter(book.name, current_chapter, translation)
        return max(v.verse for v in verses) if verses else 1
    
    def get_current_verse():
        """Get the current verse."""
        return db_manager.get_verse(book.name, current_chapter, current_verse, translation)
    
    def get_verse_context():
        """Get current verse with context."""
        context_verses = db_manager.get_verses(
            book.name, current_chapter, 
            max(1, current_verse - 2), 
            current_verse + 2, 
            translation
        )
        return context_verses
    
    def display_current():
        """Display current verse with context."""
        console.clear()
        verses = get_verse_context()
        if not verses:
            console.print(Panel("No verses found", title="Error"))
            return
        
        for verse in verses:
            if verse.verse == current_verse:
                # Highlight current verse
                verse_panel = Panel(
                    Text(verse.text, style="bold cyan"),
                    title=f"[bold yellow]>>> {verse.reference} <<<[/bold yellow]",
                    border_style="bright_blue"
                )
            else:
                verse_panel = Panel(
                    Text(verse.text),
                    title=f"[dim]{verse.reference}[/dim]",
                    border_style="dim"
                )
            console.print(verse_panel)
        
        console.print("\n[bold]Commands:[/bold]")
        console.print("  [cyan]n[/cyan] = next verse    [cyan]p[/cyan] = previous verse")
        console.print("  [cyan]N[/cyan] = next chapter  [cyan]P[/cyan] = previous chapter")
        console.print("  [cyan]g[/cyan] = goto verse    [cyan]b[/cyan] = bookmark")
        console.print("  [cyan]q[/cyan] = quit\n")
    
    # Main interactive loop
    while True:
        display_current()
        
        try:
            command = input("Command: ").strip().lower()
            
            if command in ['q', 'quit']:
                break
            elif command in ['n', 'next', '']:  # Empty enters next verse
                # Next verse
                next_verse = db_manager.get_verse(book.name, current_chapter, current_verse + 1, translation)
                if next_verse:
                    current_verse += 1
                elif current_chapter < book.chapters:
                    # Go to next chapter, verse 1
                    current_chapter += 1
                    current_verse = 1
                    next_verse = db_manager.get_verse(book.name, current_chapter, current_verse, translation)
                    if not next_verse:
                        current_chapter -= 1
                        current_verse = get_max_verse_in_chapter()
                else:
                    console.print("[yellow]End of book reached[/yellow]")
            elif command in ['p', 'prev', 'previous']:
                # Previous verse
                if current_verse > 1:
                    current_verse -= 1
                elif current_chapter > 1:
                    # Go to previous chapter, last verse
                    current_chapter -= 1
                    current_verse = get_max_verse_in_chapter()
                else:
                    console.print("[yellow]Beginning of book reached[/yellow]")
            elif command.upper() in ['N', 'NEXTCHAPTER']:
                # Next chapter
                if current_chapter < book.chapters:
                    current_chapter += 1
                    current_verse = 1
                else:
                    console.print("[yellow]End of book reached[/yellow]")
            elif command.upper() in ['P', 'PREVCHAPTER']:
                # Previous chapter
                if current_chapter > 1:
                    current_chapter -= 1
                    current_verse = 1
                else:
                    console.print("[yellow]Beginning of book reached[/yellow]")
            elif command.startswith('g'):
                # Go to specific verse
                try:
                    if ' ' in command:
                        _, ref = command.split(' ', 1)
                    else:
                        ref = input("Go to (chapter:verse): ").strip()
                    
                    if ':' in ref:
                        ch, v = ref.split(':')
                        new_chapter, new_verse = int(ch), int(v)
                    else:
                        new_chapter, new_verse = int(ref), 1
                    
                    # Validate
                    test_verse = db_manager.get_verse(book.name, new_chapter, new_verse, translation)
                    if test_verse:
                        current_chapter, current_verse = new_chapter, new_verse
                    else:
                        console.print("[red]Invalid reference[/red]")
                        input("Press Enter to continue...")
                except (ValueError, IndexError):
                    console.print("[red]Invalid format. Use: chapter:verse[/red]")
                    input("Press Enter to continue...")
            elif command in ['b', 'bookmark']:
                # Bookmark current verse
                verse = get_current_verse()
                if verse:
                    db_manager.add_bookmark(verse.id)
                    console.print(f"[green]Bookmarked {verse.reference}[/green]")
                    input("Press Enter to continue...")
            else:
                console.print("[yellow]Unknown command. Try 'n' (next), 'p' (previous), 'g' (goto), 'b' (bookmark), or 'q' (quit)[/yellow]")
                input("Press Enter to continue...")
                
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    # Add current verse to reading history
    verse = get_current_verse()
    if verse:
        db_manager.add_reading_history(verse.id)
    
    console.print(f"\n[green]Finished reading {book.name} {current_chapter}:{current_verse}[/green]")


if __name__ == '__main__':
    main()