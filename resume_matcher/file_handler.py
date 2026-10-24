"""Safe file handling with validation and graceful error reporting."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .exceptions import (
    EmptyContentError,
    FileReadError,
    FileValidationError,
    UnsupportedFileTypeError,
)

SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".csv", ".log", ".rst"}
OPTIONAL_EXTENSIONS = {".pdf", ".docx"}
ALL_SUPPORTED = SUPPORTED_TEXT_EXTENSIONS | OPTIONAL_EXTENSIONS

ENCODING_CANDIDATES = ("utf-8", "utf-8-sig", "latin-1", "cp1252")


def validate_file_path(path: str | Path) -> Path:
    """Validate that a path points to a readable, non-empty file."""
    p = Path(path)
    if not p.exists():
        raise FileValidationError(f"File does not exist: {path}")
    if not p.is_file():
        raise FileValidationError(f"Path is not a file: {path}")
    if p.stat().st_size == 0:
        raise EmptyContentError(f"File is empty: {path}")
    ext = p.suffix.lower()
    if ext and ext not in ALL_SUPPORTED and ext != "":
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{ext}' for {path}. "
            f"Supported: {sorted(ALL_SUPPORTED)}"
        )
    return p


def _read_text_with_encodings(path: Path) -> str:
    for encoding in ENCODING_CANDIDATES:
        try:
            with path.open("r", encoding=encoding) as handle:
                content = handle.read()
            if content.strip() == "":
                raise EmptyContentError(f"File contains only whitespace: {path}")
            return content
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            raise FileReadError(f"Could not read file {path}: {exc}") from exc
    raise FileReadError(f"Could not decode file with any known encoding: {path}")


def _read_pdf(path: Path) -> str:
    try:
        import pypdf  # type: ignore
    except ImportError as exc:
        raise FileReadError(
            "Reading PDF requires the 'pypdf' package. Install with: pip install pypdf"
        ) from exc
    try:
        reader = pypdf.PdfReader(str(path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        content = "\n".join(pages)
        if content.strip() == "":
            raise EmptyContentError(f"PDF contains no extractable text: {path}")
        return content
    except Exception as exc:  # pragma: no cover - defensive
        raise FileReadError(f"Failed to read PDF {path}: {exc}") from exc


def _read_docx(path: Path) -> str:
    try:
        import docx  # type: ignore
    except ImportError as exc:
        raise FileReadError(
            "Reading DOCX requires the 'python-docx' package. "
            "Install with: pip install python-docx"
        ) from exc
    try:
        document = docx.Document(str(path))
        paragraphs = [p.text for p in document.paragraphs]
        content = "\n".join(paragraphs)
        if content.strip() == "":
            raise EmptyContentError(f"DOCX contains no text: {path}")
        return content
    except Exception as exc:  # pragma: no cover - defensive
        raise FileReadError(f"Failed to read DOCX {path}: {exc}") from exc


def read_file(path: str | Path) -> str:
    """Read a file and return its textual content."""
    p = validate_file_path(path)
    ext = p.suffix.lower()
    if ext in SUPPORTED_TEXT_EXTENSIONS or ext == "":
        return _read_text_with_encodings(p)
    if ext == ".pdf":
        return _read_pdf(p)
    if ext == ".docx":
        return _read_docx(p)
    raise UnsupportedFileTypeError(f"Unsupported file type: {ext}")


def read_files(paths: Iterable[str | Path]) -> dict[str, str]:
    """Read multiple files, returning a mapping path -> content."""
    result: dict[str, str] = {}
    for path in paths:
        result[str(path)] = read_file(path)
    return result


def collect_resume_files(directory: str | Path) -> list[Path]:
    """Collect supported resume files from a directory (non-recursive)."""
    directory = Path(directory)
    if not directory.exists() or not directory.is_dir():
        raise FileValidationError(f"Not a directory: {directory}")
    files = []
    for entry in sorted(directory.iterdir()):
        if entry.is_file() and entry.suffix.lower() in ALL_SUPPORTED:
            files.append(entry)
    return files


def is_readable(path: str | Path) -> bool:
    """Return True if the file can be read successfully."""
    try:
        read_file(path)
        return True
    except (FileValidationError, FileReadError, EmptyContentError, UnsupportedFileTypeError):
        return False
