"""Bible data import functionality."""

import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from pathlib import Path
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import DatabaseManager, Book, Verse


class BibleDataImporter:
    """Import Bible data from various sources."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def import_from_json(self, file_path: Path) -> None:
        """Import Bible data from JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        with self.db_manager.get_session() as session:
            self._import_json_data(session, data)

    def import_from_xml(self, file_path: Path) -> None:
        """Import Bible data from XML file."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            # Try to fix common XML issues
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix common issues
            content = self._fix_xml_content(content)
            
            # Try parsing again
            root = ET.fromstring(content)

        with self.db_manager.get_session() as session:
            self._import_xml_data(session, root)

    def import_from_url(self, url: str) -> None:
        """Import Bible data from URL."""
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()

            if url.endswith(".json"):
                data = response.json()
                with self.db_manager.get_session() as session:
                    self._import_json_data(session, data)
            elif url.endswith(".xml"):
                # Use streaming parser for large/malformed XML
                with self.db_manager.get_session() as session:
                    self._import_usfx_streaming(session, response.text)
            else:
                raise ValueError(f"Unsupported file format for URL: {url}")

    def _import_json_data(self, session: Session, data: Dict[str, Any]) -> None:
        """Import data from JSON structure."""
        if "books" in data:
            for book_data in data["books"]:
                self._import_book_json(session, book_data)
        else:
            raise ValueError("Invalid JSON structure: missing 'books' key")

    def _import_book_json(self, session: Session, book_data: Dict[str, Any]) -> None:
        """Import a single book from JSON."""
        book = Book(
            name=book_data["name"],
            abbreviation=book_data.get("abbreviation", book_data["name"][:3].upper()),
            testament=book_data.get("testament", "old"),
            order=book_data.get("order", 1),
            chapters=len(book_data.get("chapters", [])),
        )

        existing_book = session.query(Book).filter_by(name=book.name).first()
        if existing_book:
            book = existing_book
        else:
            session.add(book)
            session.flush()

        for chapter_num, chapter_data in enumerate(book_data.get("chapters", []), 1):
            if isinstance(chapter_data, list):
                for verse_num, verse_text in enumerate(chapter_data, 1):
                    verse = Verse(
                        book_id=book.id,
                        chapter=chapter_num,
                        verse=verse_num,
                        text=verse_text.strip(),
                        translation=book_data.get("translation", "NIV"),
                    )
                    session.add(verse)
            elif isinstance(chapter_data, dict):
                for verse_num, verse_text in chapter_data.items():
                    verse = Verse(
                        book_id=book.id,
                        chapter=chapter_num,
                        verse=int(verse_num),
                        text=verse_text.strip(),
                        translation=book_data.get("translation", "NIV"),
                    )
                    session.add(verse)

        session.commit()

    def _import_xml_data(self, session: Session, root: ET.Element) -> None:
        """Import data from XML structure."""
        if root.tag == "bible":
            self._import_bible_xml(session, root)
        elif root.tag == "usfx":
            self._import_usfx_xml(session, root)
        else:
            raise ValueError(f"Unknown XML root element: {root.tag}")

    def _import_bible_xml(self, session: Session, root: ET.Element) -> None:
        """Import from standard Bible XML format."""
        for book_elem in root.findall("book"):
            book_name = book_elem.get("name", "Unknown")
            book_abbr = book_elem.get("abbreviation", book_name[:3].upper())
            testament = book_elem.get("testament", "old")

            book = Book(
                name=book_name,
                abbreviation=book_abbr,
                testament=testament,
                order=len(session.query(Book).all()) + 1,
                chapters=len(book_elem.findall("chapter")),
            )

            existing_book = session.query(Book).filter_by(name=book.name).first()
            if existing_book:
                book = existing_book
            else:
                session.add(book)
                session.flush()

            for chapter_elem in book_elem.findall("chapter"):
                chapter_num = int(chapter_elem.get("number", 1))

                for verse_elem in chapter_elem.findall("verse"):
                    verse_num = int(verse_elem.get("number", 1))
                    verse_text = verse_elem.text or ""

                    verse = Verse(
                        book_id=book.id,
                        chapter=chapter_num,
                        verse=verse_num,
                        text=verse_text.strip(),
                        translation=root.get("translation", "NIV"),
                    )
                    session.add(verse)

        session.commit()

    def _import_usfx_xml(self, session: Session, root: ET.Element) -> None:
        """Import from USFX XML format."""
        import re
        
        # Convert the entire XML to string for regex parsing (more reliable for this format)
        xml_content = ET.tostring(root, encoding='unicode')
        
        # Extract books using regex
        book_pattern = r'<book id="([^"]+)">(.*?)</book>'
        book_matches = re.findall(book_pattern, xml_content, re.DOTALL)
        
        for book_code, book_content in book_matches:
            # Get book name from <h> tag
            h_match = re.search(r'<h>([^<]+)</h>', book_content)
            if h_match:
                book_name = h_match.group(1).strip()
            else:
                book_name = self._get_book_name_from_code(book_code)
            
            if not book_name:
                continue
            
            # Create or get book
            existing_book = session.query(Book).filter_by(name=book_name).first()
            if existing_book:
                current_book = existing_book
            else:
                book = Book(
                    name=book_name,
                    abbreviation=book_code,
                    testament="old" if self._is_old_testament(book_code) else "new",
                    order=len(session.query(Book).all()) + 1,
                    chapters=0,
                )
                session.add(book)
                session.flush()
                current_book = book
            
            # Extract chapters and verses
            self._parse_book_content(session, current_book, book_content)

        # Update chapter counts
        for book in session.query(Book).all():
            max_chapter = session.query(func.max(Verse.chapter)).filter(Verse.book_id == book.id).scalar()
            if max_chapter:
                book.chapters = max_chapter

        session.commit()

    def _parse_book_content(self, session: Session, book: Book, content: str) -> None:
        """Parse book content to extract verses."""
        import re
        
        # Split content by chapters
        chapter_parts = re.split(r'<c id="(\d+)"/>', content)
        
        current_chapter = 1
        for i in range(1, len(chapter_parts), 2):  # Skip the first empty part
            if i + 1 < len(chapter_parts):
                current_chapter = int(chapter_parts[i])
                chapter_content = chapter_parts[i + 1]
                
                # Extract verses from chapter content
                verses = self._extract_verses_from_chapter(chapter_content)
                
                for verse_num, verse_text in verses.items():
                    if verse_text.strip():
                        verse = Verse(
                            book_id=book.id,
                            chapter=current_chapter,
                            verse=verse_num,
                            text=verse_text.strip(),
                            translation="BBE",
                        )
                        session.add(verse)

    def _extract_verses_from_chapter(self, content: str) -> Dict[int, str]:
        """Extract verses from chapter content."""
        import re
        verses = {}
        
        # Split by verse markers and extract text
        verse_parts = re.split(r'<v id="(\d+)"/>', content)
        
        for i in range(1, len(verse_parts), 2):  # Skip first empty part
            if i + 1 < len(verse_parts):
                verse_num = int(verse_parts[i])
                verse_content = verse_parts[i + 1]
                
                # Extract text until next verse or end
                text_end = verse_content.find('<ve/>')
                if text_end != -1:
                    verse_text = verse_content[:text_end]
                else:
                    # Find next verse or end of content
                    next_verse = re.search(r'<v id="\d+"', verse_content)
                    if next_verse:
                        verse_text = verse_content[:next_verse.start()]
                    else:
                        verse_text = verse_content
                
                # Clean up the text
                verse_text = re.sub(r'<[^>]*>', '', verse_text)  # Remove any remaining tags
                verse_text = verse_text.strip()
                
                if verse_text:
                    verses[verse_num] = verse_text
        
        return verses

    def _import_usfx_streaming(self, session: Session, content: str) -> None:
        """Import USFX data using streaming approach for malformed XML."""
        import re
        
        current_book = None
        current_chapter = 1
        current_verse = 1
        verse_text = ""
        
        # Process line by line to handle malformed XML
        lines = content.split('\n')
        
        for line_index, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for book start
            book_match = re.search(r'<book id="([^"]+)"', line)
            if book_match:
                book_code = book_match.group(1)
                current_book = None  # Reset current book
                
                # Look for book name in <h> tag on same or next few lines
                h_match = re.search(r'<h>([^<]+)</h>', line)
                if not h_match:
                    # Check next few lines for <h> tag
                    for next_line in lines[line_index+1:line_index+5]:
                        h_match = re.search(r'<h>([^<]+)</h>', next_line)
                        if h_match:
                            break
                
                if h_match:
                    book_name = h_match.group(1).strip()
                else:
                    book_name = self._get_book_name_from_code(book_code)
                
                if book_name:
                    # Create or get book
                    existing_book = session.query(Book).filter_by(name=book_name).first()
                    if existing_book:
                        current_book = existing_book
                    else:
                        book = Book(
                            name=book_name,
                            abbreviation=book_code,
                            testament="old" if self._is_old_testament(book_code) else "new",
                            order=len(session.query(Book).all()) + 1,
                            chapters=0,
                        )
                        session.add(book)
                        session.flush()
                        current_book = book
                continue
            
            # Check for chapter
            chapter_match = re.search(r'<c id="(\d+)"', line)
            if chapter_match and current_book:
                current_chapter = int(chapter_match.group(1))
                continue
            
            # Check for verse start
            verse_match = re.search(r'<v id="(\d+)"/>', line)
            if verse_match and current_book:
                # Save previous verse if exists
                if verse_text.strip():
                    verse = Verse(
                        book_id=current_book.id,
                        chapter=current_chapter,
                        verse=current_verse,
                        text=verse_text.strip(),
                        translation="BBE",
                    )
                    session.add(verse)
                
                # Start new verse
                current_verse = int(verse_match.group(1))
                # Extract text after the verse tag
                verse_text = line.split('<v id="{}"/>'.format(current_verse), 1)[-1]
                verse_text = re.sub(r'<[^>]*>', '', verse_text)  # Remove XML tags
                continue
            
            # Check for verse end
            if '<ve/>' in line and current_book and verse_text:
                # Clean up and save verse
                line_text = line.replace('<ve/>', '')
                line_text = re.sub(r'<[^>]*>', '', line_text)
                verse_text += ' ' + line_text
                
                if verse_text.strip():
                    verse = Verse(
                        book_id=current_book.id,
                        chapter=current_chapter,
                        verse=current_verse,
                        text=verse_text.strip(),
                        translation="BBE",
                    )
                    session.add(verse)
                
                verse_text = ""
                continue
            
            # Accumulate verse text
            if current_book and verse_text is not None:
                line_text = re.sub(r'<[^>]*>', '', line)  # Remove XML tags
                if line_text.strip():
                    verse_text += ' ' + line_text.strip()
        
        # Save any remaining verse
        if current_book and verse_text and verse_text.strip():
            verse = Verse(
                book_id=current_book.id,
                chapter=current_chapter,
                verse=current_verse,
                text=verse_text.strip(),
                translation="BBE",
            )
            session.add(verse)
        
        # Update chapter counts
        for book in session.query(Book).all():
            max_chapter = session.query(func.max(Verse.chapter)).filter(Verse.book_id == book.id).scalar()
            if max_chapter:
                book.chapters = max_chapter
        
        session.commit()

    def _fix_xml_content(self, content: str) -> str:
        """Fix common XML parsing issues."""
        import re
        
        # Remove any content after the last closing tag to fix truncation issues
        last_tag_match = None
        for match in re.finditer(r'</[^>]+>', content):
            last_tag_match = match
        
        if last_tag_match:
            content = content[:last_tag_match.end()]
        
        # Ensure the document ends with the root closing tag
        if not content.strip().endswith('</usfx>'):
            # Find the last complete tag and truncate there
            last_complete = content.rfind('</')
            if last_complete != -1:
                next_close = content.find('>', last_complete)
                if next_close != -1:
                    content = content[:next_close + 1]
            
            # Add closing usfx tag if missing
            if '<usfx' in content and not content.endswith('</usfx>'):
                content += '</usfx>'
        
        return content

    def _get_book_name_from_code(self, code: str) -> Optional[str]:
        """Get book name from USFX code."""
        book_codes = {
            "GEN": "Genesis",
            "EXO": "Exodus",
            "LEV": "Leviticus",
            "NUM": "Numbers",
            "DEU": "Deuteronomy",
            "JOS": "Joshua",
            "JDG": "Judges",
            "RUT": "Ruth",
            "1SA": "1 Samuel",
            "2SA": "2 Samuel",
            "1KI": "1 Kings",
            "2KI": "2 Kings",
            "1CH": "1 Chronicles",
            "2CH": "2 Chronicles",
            "EZR": "Ezra",
            "NEH": "Nehemiah",
            "EST": "Esther",
            "JOB": "Job",
            "PSA": "Psalms",
            "PRO": "Proverbs",
            "ECC": "Ecclesiastes",
            "SNG": "Song of Solomon",
            "ISA": "Isaiah",
            "JER": "Jeremiah",
            "LAM": "Lamentations",
            "EZK": "Ezekiel",
            "DAN": "Daniel",
            "HOS": "Hosea",
            "JOL": "Joel",
            "AMO": "Amos",
            "OBA": "Obadiah",
            "JON": "Jonah",
            "MIC": "Micah",
            "NAM": "Nahum",
            "HAB": "Habakkuk",
            "ZEP": "Zephaniah",
            "HAG": "Haggai",
            "ZEC": "Zechariah",
            "MAL": "Malachi",
            "MAT": "Matthew",
            "MRK": "Mark",
            "LUK": "Luke",
            "JHN": "John",
            "ACT": "Acts",
            "ROM": "Romans",
            "1CO": "1 Corinthians",
            "2CO": "2 Corinthians",
            "GAL": "Galatians",
            "EPH": "Ephesians",
            "PHP": "Philippians",
            "COL": "Colossians",
            "1TH": "1 Thessalonians",
            "2TH": "2 Thessalonians",
            "1TI": "1 Timothy",
            "2TI": "2 Timothy",
            "TIT": "Titus",
            "PHM": "Philemon",
            "HEB": "Hebrews",
            "JAS": "James",
            "1PE": "1 Peter",
            "2PE": "2 Peter",
            "1JN": "1 John",
            "2JN": "2 John",
            "3JN": "3 John",
            "JUD": "Jude",
            "REV": "Revelation",
        }
        return book_codes.get(code.upper())

    def _is_old_testament(self, code: str) -> bool:
        """Check if book code is from Old Testament."""
        old_testament_codes = {
            "GEN", "EXO", "LEV", "NUM", "DEU", "JOS", "JDG", "RUT",
            "1SA", "2SA", "1KI", "2KI", "1CH", "2CH", "EZR", "NEH",
            "EST", "JOB", "PSA", "PRO", "ECC", "SNG", "ISA", "JER",
            "LAM", "EZK", "DAN", "HOS", "JOL", "AMO", "OBA", "JON",
            "MIC", "NAM", "HAB", "ZEP", "HAG", "ZEC", "MAL"
        }
        return code.upper() in old_testament_codes

    def download_and_import_bible(self, url: str = None) -> None:
        """Download and import Bible data from default or custom URL."""
        if url is None:
            url = "https://raw.githubusercontent.com/seven1m/open-bibles/f5581d1719c8ad8218efb54edbd6efc49fa4cc0a/eng-bbe.usfx.xml"

        try:
            self.import_from_url(url)
            print(f"Successfully imported Bible data from {url}")
        except Exception as e:
            print(f"Error importing Bible data: {e}")
            raise


def initialize_database(db_manager: DatabaseManager) -> None:
    """Initialize database with Bible data."""
    db_manager.create_tables()
    
    # Check if data already exists
    with db_manager.get_session() as session:
        if session.query(Book).count() > 0:
            print("Bible data already exists in database")
            return

    # Import default Bible data
    importer = BibleDataImporter(db_manager)
    importer.download_and_import_bible()
    print("Database initialized with Bible data")