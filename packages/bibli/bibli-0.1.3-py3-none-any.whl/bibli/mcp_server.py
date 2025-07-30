"""MCP (Model Context Protocol) server for Bible CLI."""

import asyncio
import json
from typing import Any
from urllib.parse import urlparse

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from .config import Config
from .data_import import initialize_database
from .models import DatabaseManager
from .search import SearchEngine


class BibleMCPServer:
    """MCP server for Bible CLI functionality."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.search_engine = SearchEngine(db_manager)
        self.server = Server("bible-mcp-server")

        # Setup handlers
        self._setup_tool_handlers()
        self._setup_resource_handlers()
        self._setup_prompt_handlers()

    def _setup_tool_handlers(self):
        """Setup tool handlers for MCP server."""

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="search_verses",
                    description="Search for Bible verses containing specific text",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query text",
                            },
                            "translation": {
                                "type": "string",
                                "description": "Bible translation (default: BBE)",
                                "default": "BBE",
                            },
                            "exact": {
                                "type": "boolean",
                                "description": "Whether to search for exact phrase match",
                                "default": False,
                            },
                            "case_sensitive": {
                                "type": "boolean",
                                "description": "Whether search should be case sensitive",
                                "default": False,
                            },
                            "book": {
                                "type": "string",
                                "description": "Limit search to specific book (optional)",
                            },
                            "testament": {
                                "type": "string",
                                "description": "Limit search to testament: 'old' or 'new' (optional)",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 100,
                            },
                        },
                        "required": ["query"],
                    },
                ),
                types.Tool(
                    name="get_verse",
                    description="Get a specific Bible verse by reference",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "reference": {
                                "type": "string",
                                "description": "Bible verse reference (e.g., 'John 3:16', 'Genesis 1:1')",
                            },
                            "translation": {
                                "type": "string",
                                "description": "Bible translation (default: BBE)",
                                "default": "BBE",
                            },
                        },
                        "required": ["reference"],
                    },
                ),
                types.Tool(
                    name="get_chapter",
                    description="Get all verses from a Bible chapter",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "book": {
                                "type": "string",
                                "description": "Book name (e.g., 'John', 'Genesis')",
                            },
                            "chapter": {
                                "type": "integer",
                                "description": "Chapter number",
                                "minimum": 1,
                            },
                            "translation": {
                                "type": "string",
                                "description": "Bible translation (default: BBE)",
                                "default": "BBE",
                            },
                        },
                        "required": ["book", "chapter"],
                    },
                ),
                types.Tool(
                    name="get_random_verse",
                    description="Get a random Bible verse",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "translation": {
                                "type": "string",
                                "description": "Bible translation (default: BBE)",
                                "default": "BBE",
                            },
                            "testament": {
                                "type": "string",
                                "description": "Limit to testament: 'old' or 'new' (optional)",
                            },
                        },
                        "required": [],
                    },
                ),
                types.Tool(
                    name="get_cross_references",
                    description="Get cross-references for a Bible verse",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "reference": {
                                "type": "string",
                                "description": "Bible verse reference (e.g., 'John 3:16')",
                            },
                            "translation": {
                                "type": "string",
                                "description": "Bible translation (default: BBE)",
                                "default": "BBE",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of cross-references (default: 5)",
                                "default": 5,
                                "minimum": 1,
                                "maximum": 20,
                            },
                        },
                        "required": ["reference"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any]
        ) -> list[types.TextContent]:
            """Handle tool calls."""
            try:
                if name == "search_verses":
                    return await self._handle_search_verses(arguments)
                elif name == "get_verse":
                    return await self._handle_get_verse(arguments)
                elif name == "get_chapter":
                    return await self._handle_get_chapter(arguments)
                elif name == "get_random_verse":
                    return await self._handle_get_random_verse(arguments)
                elif name == "get_cross_references":
                    return await self._handle_get_cross_references(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    def _setup_resource_handlers(self):
        """Setup resource handlers for MCP server."""

        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """List available resources."""
            resources = [
                types.Resource(
                    uri="bible://books",
                    name="Bible Books",
                    description="List of all Bible books with metadata",
                    mimeType="application/json",
                )
            ]

            # Add book-specific resources
            books = self.db_manager.get_books()
            for book in books:
                resources.append(
                    types.Resource(
                        uri=f"bible://book/{book.name.replace(' ', '_')}",
                        name=f"Book: {book.name}",
                        description=f"Information about the book of {book.name}",
                        mimeType="application/json",
                    )
                )

            return resources

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Handle resource reading."""
            try:
                parsed_uri = urlparse(uri)

                if parsed_uri.scheme != "bible":
                    raise ValueError(f"Unsupported URI scheme: {parsed_uri.scheme}")

                path_parts = parsed_uri.path.strip("/").split("/")

                if path_parts[0] == "books":
                    return await self._get_books_resource()
                elif path_parts[0] == "book" and len(path_parts) > 1:
                    book_name = path_parts[1].replace("_", " ")
                    return await self._get_book_resource(book_name)
                else:
                    raise ValueError(f"Unknown resource path: {parsed_uri.path}")

            except Exception as e:
                raise ValueError(f"Error reading resource: {str(e)}")

    def _setup_prompt_handlers(self):
        """Setup prompt handlers for MCP server."""

        @self.server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            """List available prompts."""
            return [
                types.Prompt(
                    name="bible-study",
                    description="Generate Bible study questions and insights for a passage",
                    arguments=[
                        types.PromptArgument(
                            name="passage",
                            description="Bible passage or verse reference",
                            required=True,
                        ),
                        types.PromptArgument(
                            name="study_type",
                            description="Type of study: 'personal', 'group', 'teaching', 'devotional'",
                            required=False,
                        ),
                        types.PromptArgument(
                            name="focus",
                            description="Study focus: 'theological', 'practical', 'historical', 'literary'",
                            required=False,
                        ),
                    ],
                ),
                types.Prompt(
                    name="verse-explanation",
                    description="Provide detailed explanation and context for a Bible verse",
                    arguments=[
                        types.PromptArgument(
                            name="verse",
                            description="Bible verse reference to explain",
                            required=True,
                        ),
                        types.PromptArgument(
                            name="context_level",
                            description="Level of context: 'basic', 'detailed', 'academic'",
                            required=False,
                        ),
                    ],
                ),
                types.Prompt(
                    name="devotional",
                    description="Create a devotional reflection based on a Bible passage",
                    arguments=[
                        types.PromptArgument(
                            name="passage",
                            description="Bible passage for devotional",
                            required=True,
                        ),
                        types.PromptArgument(
                            name="theme",
                            description="Devotional theme or focus",
                            required=False,
                        ),
                        types.PromptArgument(
                            name="length",
                            description="Devotional length: 'short', 'medium', 'long'",
                            required=False,
                        ),
                    ],
                ),
                types.Prompt(
                    name="sermon-outline",
                    description="Generate a sermon outline based on a Bible passage",
                    arguments=[
                        types.PromptArgument(
                            name="text",
                            description="Bible text for sermon",
                            required=True,
                        ),
                        types.PromptArgument(
                            name="audience",
                            description="Target audience: 'general', 'youth', 'children', 'seniors'",
                            required=False,
                        ),
                        types.PromptArgument(
                            name="sermon_type",
                            description="Sermon type: 'expository', 'topical', 'narrative'",
                            required=False,
                        ),
                    ],
                ),
            ]

        @self.server.get_prompt()
        async def handle_get_prompt(
            name: str, arguments: dict[str, str] | None
        ) -> types.GetPromptResult:
            """Handle prompt requests."""
            try:
                if name == "bible-study":
                    return await self._generate_bible_study_prompt(arguments or {})
                elif name == "verse-explanation":
                    return await self._generate_verse_explanation_prompt(
                        arguments or {}
                    )
                elif name == "devotional":
                    return await self._generate_devotional_prompt(arguments or {})
                elif name == "sermon-outline":
                    return await self._generate_sermon_outline_prompt(arguments or {})
                else:
                    raise ValueError(f"Unknown prompt: {name}")
            except Exception as e:
                raise ValueError(f"Error generating prompt: {str(e)}")

    # Tool implementation methods
    async def _handle_search_verses(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle verse search tool."""
        query = arguments["query"]
        translation = arguments.get("translation", "BBE")
        exact = arguments.get("exact", False)
        case_sensitive = arguments.get("case_sensitive", False)
        book = arguments.get("book")
        testament = arguments.get("testament")
        limit = arguments.get("limit", 10)

        verses = self.search_engine.search(
            query=query,
            translation=translation,
            exact=exact,
            case_sensitive=case_sensitive,
            book=book,
            testament=testament,
            limit=limit,
        )

        if not verses:
            return [
                types.TextContent(
                    type="text", text=f"No verses found for query: {query}"
                )
            ]

        results = []
        results.append(
            types.TextContent(
                type="text", text=f"Found {len(verses)} verse(s) for '{query}':\n"
            )
        )

        for verse in verses:
            verse_text = (
                f"\n**{verse.reference}** ({verse.translation})\n{verse.text}\n"
            )
            results.append(types.TextContent(type="text", text=verse_text))

        return results

    async def _handle_get_verse(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle get verse tool."""
        reference = arguments["reference"]
        translation = arguments.get("translation", "BBE")

        # Parse reference
        try:
            parts = reference.split()
            if len(parts) < 2:
                raise ValueError("Invalid reference format")

            book_name = parts[0]
            ref_part = parts[1]

            if ":" not in ref_part:
                raise ValueError(
                    "Reference must include verse number (e.g., 'John 3:16')"
                )

            chapter_str, verse_str = ref_part.split(":")
            chapter = int(chapter_str)
            verse_num = int(verse_str)

            verse = self.db_manager.get_verse(
                book_name, chapter, verse_num, translation
            )
            if not verse:
                return [
                    types.TextContent(type="text", text=f"Verse not found: {reference}")
                ]

            verse_text = f"**{verse.reference}** ({verse.translation})\n{verse.text}"
            return [types.TextContent(type="text", text=verse_text)]

        except (ValueError, IndexError) as e:
            return [
                types.TextContent(
                    type="text", text=f"Error parsing reference '{reference}': {str(e)}"
                )
            ]

    async def _handle_get_chapter(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle get chapter tool."""
        book = arguments["book"]
        chapter = arguments["chapter"]
        translation = arguments.get("translation", "BBE")

        verses = self.db_manager.get_chapter(book, chapter, translation)
        if not verses:
            return [
                types.TextContent(
                    type="text", text=f"Chapter not found: {book} {chapter}"
                )
            ]

        results = []
        results.append(
            types.TextContent(
                type="text", text=f"**{book} Chapter {chapter}** ({translation})\n"
            )
        )

        for verse in verses:
            verse_text = f"\n**{verse.verse}.** {verse.text}"
            results.append(types.TextContent(type="text", text=verse_text))

        return results

    async def _handle_get_random_verse(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle get random verse tool."""
        translation = arguments.get("translation", "BBE")
        testament = arguments.get("testament")

        # Use the search engine to get a random verse
        # For simplicity, we'll search for common words and pick randomly
        import random

        common_words = [
            "love",
            "peace",
            "joy",
            "hope",
            "faith",
            "truth",
            "light",
            "life",
        ]
        search_word = random.choice(common_words)

        verses = self.search_engine.search(
            query=search_word, translation=translation, testament=testament, limit=50
        )

        if not verses:
            return [types.TextContent(type="text", text="No verses found")]

        random_verse = random.choice(verses)
        verse_text = f"**Random Verse: {random_verse.reference}** ({random_verse.translation})\n{random_verse.text}"
        return [types.TextContent(type="text", text=verse_text)]

    async def _handle_get_cross_references(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle get cross references tool."""
        reference = arguments["reference"]
        translation = arguments.get("translation", "BBE")
        limit = arguments.get("limit", 5)

        # First get the verse
        try:
            parts = reference.split()
            book_name = parts[0]
            ref_part = parts[1]
            chapter_str, verse_str = ref_part.split(":")
            chapter = int(chapter_str)
            verse_num = int(verse_str)

            verse = self.db_manager.get_verse(
                book_name, chapter, verse_num, translation
            )
            if not verse:
                return [
                    types.TextContent(type="text", text=f"Verse not found: {reference}")
                ]

            # Get cross-references using the search engine
            cross_refs = self.search_engine.get_cross_references(verse)[:limit]

            if not cross_refs:
                return [
                    types.TextContent(
                        type="text", text=f"No cross-references found for {reference}"
                    )
                ]

            results = []
            results.append(
                types.TextContent(
                    type="text", text=f"**Cross-references for {reference}:**\n"
                )
            )

            for ref_verse in cross_refs:
                verse_text = f"\n**{ref_verse.reference}** ({ref_verse.translation})\n{ref_verse.text}\n"
                results.append(types.TextContent(type="text", text=verse_text))

            return results

        except Exception as e:
            return [
                types.TextContent(
                    type="text", text=f"Error finding cross-references: {str(e)}"
                )
            ]

    # Resource implementation methods
    async def _get_books_resource(self) -> str:
        """Get list of Bible books as JSON resource."""
        books = self.db_manager.get_books()
        books_data = []

        for book in books:
            books_data.append(
                {
                    "id": book.id,
                    "name": book.name,
                    "abbreviation": book.abbreviation,
                    "testament": book.testament,
                    "order": book.order,
                    "chapters": book.chapters,
                }
            )

        return json.dumps(books_data, indent=2)

    async def _get_book_resource(self, book_name: str) -> str:
        """Get specific book information as JSON resource."""
        book = self.db_manager.get_book_by_name(book_name)
        if not book:
            raise ValueError(f"Book not found: {book_name}")

        book_data = {
            "id": book.id,
            "name": book.name,
            "abbreviation": book.abbreviation,
            "testament": book.testament,
            "order": book.order,
            "chapters": book.chapters,
            "description": f"The book of {book.name} is in the {book.testament} testament and contains {book.chapters} chapters.",
        }

        return json.dumps(book_data, indent=2)

    # Prompt implementation methods
    async def _generate_bible_study_prompt(
        self, arguments: dict[str, str]
    ) -> types.GetPromptResult:
        """Generate Bible study prompt."""
        passage = arguments.get("passage", "")
        study_type = arguments.get("study_type", "personal")
        focus = arguments.get("focus", "practical")

        if not passage:
            raise ValueError("Passage argument is required")

        prompt_text = f"""Generate a comprehensive Bible study for the passage: {passage}

Study Type: {study_type}
Focus: {focus}

Please provide:
1. Context and background of the passage
2. Key themes and theological insights
3. Practical applications for daily life
4. Discussion questions for reflection
5. Cross-references to related passages
6. Prayer points based on the passage

Make the study suitable for {study_type} use with a {focus} focus."""

        return types.GetPromptResult(
            description=f"Bible study for {passage}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text),
                )
            ],
        )

    async def _generate_verse_explanation_prompt(
        self, arguments: dict[str, str]
    ) -> types.GetPromptResult:
        """Generate verse explanation prompt."""
        verse = arguments.get("verse", "")
        context_level = arguments.get("context_level", "detailed")

        if not verse:
            raise ValueError("Verse argument is required")

        prompt_text = f"""Provide a {context_level} explanation of the Bible verse: {verse}

Please include:
1. The verse text in context
2. Historical and cultural background
3. Literary and grammatical analysis
4. Theological significance
5. Practical application
6. Cross-references to related verses
7. How this verse fits within the broader biblical narrative

Adjust the depth of explanation to be {context_level} level."""

        return types.GetPromptResult(
            description=f"Explanation of {verse}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text),
                )
            ],
        )

    async def _generate_devotional_prompt(
        self, arguments: dict[str, str]
    ) -> types.GetPromptResult:
        """Generate devotional prompt."""
        passage = arguments.get("passage", "")
        theme = arguments.get("theme", "")
        length = arguments.get("length", "medium")

        if not passage:
            raise ValueError("Passage argument is required")

        theme_text = f" focusing on the theme of {theme}" if theme else ""

        prompt_text = f"""Create a {length} devotional reflection based on the Bible passage: {passage}{theme_text}

Structure the devotional with:
1. Opening thought or question
2. Scripture passage with brief context
3. Key insight or meditation point
4. Personal application
5. Closing prayer or reflection

Make it suitable for personal quiet time and spiritual growth. The tone should be encouraging, thoughtful, and practical."""

        return types.GetPromptResult(
            description=f"Devotional for {passage}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text),
                )
            ],
        )

    async def _generate_sermon_outline_prompt(
        self, arguments: dict[str, str]
    ) -> types.GetPromptResult:
        """Generate sermon outline prompt."""
        text = arguments.get("text", "")
        audience = arguments.get("audience", "general")
        sermon_type = arguments.get("sermon_type", "expository")

        if not text:
            raise ValueError("Text argument is required")

        prompt_text = f"""Create a {sermon_type} sermon outline based on the Bible text: {text}

Target Audience: {audience}
Sermon Type: {sermon_type}

Please provide:
1. Sermon title
2. Main theme/big idea
3. Introduction (hook, context, preview)
4. Main points (3-4 points with sub-points)
5. Illustrations and application suggestions
6. Conclusion and call to action
7. Suggested supporting scriptures

Tailor the content and language to be appropriate for a {audience} audience. Make it practical, engaging, and biblically faithful."""

        return types.GetPromptResult(
            description=f"Sermon outline for {text}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text),
                )
            ],
        )

    async def run(self, host: str = "localhost", port: int = 8000):
        """Run the MCP server using stdio transport."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="bible-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


def create_mcp_server(database_url: str | None = None) -> BibleMCPServer:
    """Create and configure the Bible MCP server."""
    if database_url is None:
        # Use the same config system as CLI
        config = Config()
        db_path = config.get_database_path()
        database_url = f"sqlite:///{db_path}"
        print(f"Using database: {db_path}")

    db_manager = DatabaseManager(database_url)

    # Initialize database if needed (same as CLI)
    try:
        initialize_database(db_manager)
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

    return BibleMCPServer(db_manager)


async def run_mcp_server(database_url: str | None = None):
    """Run the Bible MCP server."""
    server = create_mcp_server(database_url)
    await server.run()


if __name__ == "__main__":
    asyncio.run(run_mcp_server())
