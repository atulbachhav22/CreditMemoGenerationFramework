"""
FileLoader - Utility for loading various file types into text format.

Supports: TXT, PDF, DOCX, JSON, and more.
"""

from pathlib import Path
from typing import Optional
from loguru import logger


class FileLoader:
    """
    Handles loading various file types and converting them to text.

    Supports:
    - Plain text files (.txt, .md, .json, .csv)
    - PDF files (.pdf) - requires PyPDF2
    - Word documents (.docx) - requires python-docx
    """

    @staticmethod
    def load_file(file_path: str, encoding: str = "utf-8") -> str:
        """
        Load a file and return its content as text.

        Args:
            file_path: Path to the file to load
            encoding: Text encoding (default: utf-8)

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is not supported
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = path.suffix.lower()

        # Plain text files
        if extension in [".txt", ".md", ".json", ".csv", ".xml", ".yaml", ".yml"]:
            return FileLoader._load_text_file(path, encoding)

        # PDF files
        elif extension == ".pdf":
            return FileLoader._load_pdf(path)

        # Word documents
        elif extension in [".docx", ".doc"]:
            return FileLoader._load_docx(path)

        else:
            # Try as plain text
            logger.warning(f"Unknown file type {extension}, attempting to read as text")
            return FileLoader._load_text_file(path, encoding)

    @staticmethod
    def _load_text_file(path: Path, encoding: str = "utf-8") -> str:
        """Load a plain text file."""
        try:
            with open(path, "r", encoding=encoding) as f:
                content = f.read()
            logger.info(f"Loaded text file: {path.name} ({len(content)} characters)")
            return content
        except UnicodeDecodeError:
            # Try with different encoding
            logger.warning(f"UTF-8 decode failed, trying latin-1 for {path.name}")
            with open(path, "r", encoding="latin-1") as f:
                content = f.read()
            return content

    @staticmethod
    def _load_pdf(path: Path) -> str:
        """Load a PDF file and extract text."""
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            raise ImportError(
                "PyPDF2 is required to load PDF files. "
                "Install it with: pip install pypdf2"
            )

        reader = PdfReader(str(path))
        text_parts = []

        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            text_parts.append(f"--- Page {i + 1} ---\n{text}")

        content = "\n\n".join(text_parts)
        logger.info(f"Loaded PDF: {path.name} ({len(reader.pages)} pages, {len(content)} characters)")
        return content

    @staticmethod
    def _load_docx(path: Path) -> str:
        """Load a Word document and extract text."""
        try:
            from docx import Document
        except ImportError:
            raise ImportError(
                "python-docx is required to load Word documents. "
                "Install it with: pip install python-docx"
            )

        doc = Document(str(path))
        paragraphs = [para.text for para in doc.paragraphs]
        content = "\n".join(paragraphs)

        logger.info(f"Loaded DOCX: {path.name} ({len(doc.paragraphs)} paragraphs, {len(content)} characters)")
        return content

    @staticmethod
    def is_supported_file(file_path: str) -> bool:
        """
        Check if a file type is supported.

        Args:
            file_path: Path to check

        Returns:
            True if file type is supported
        """
        extension = Path(file_path).suffix.lower()
        supported = [
            ".txt", ".md", ".json", ".csv", ".xml", ".yaml", ".yml",
            ".pdf", ".docx", ".doc"
        ]
        return extension in supported

    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """
        Get information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        return {
            "name": path.name,
            "extension": path.suffix,
            "size_bytes": path.stat().st_size,
            "is_supported": FileLoader.is_supported_file(file_path),
            "absolute_path": str(path.absolute())
        }
