import os
import re
import secrets
import string
from pathlib import Path
from typing import Literal


LATEX_FILE_EXTENSIONS = frozenset({".tex", ".tax"})
SourceFormat = Literal["markdown", "latex"]


def doc_to_markdown(doc_path: str) -> str:
    """Convert a non-LaTeX document to Markdown.

    LaTeX files are returned as raw source so their template is not rewritten
    before they reach the agents.
    """
    if get_file_extension(str(doc_path)) in LATEX_FILE_EXTENSIONS:
        return read_latex_source(doc_path)

    from markitdown import MarkItDown

    md = MarkItDown()
    return md.convert(doc_path).text_content


def get_file_extension(filename: str) -> str:
    """Return a normalized, lowercase file extension."""
    return Path(filename.strip()).suffix.lower()


def get_cv_source_format(filename: str) -> SourceFormat | None:
    """Return the explicitly recognized source format, or ``None``.

    Unknown extensions are left to MarkItDown for backward compatibility with
    the existing document-upload path.
    """
    extension = get_file_extension(filename)
    if extension in LATEX_FILE_EXTENSIONS:
        return "latex"
    if extension == ".docx":
        return "markdown"
    return None


def read_latex_source(file_path: str | os.PathLike[str]) -> str:
    """Read a LaTeX source file without converting or formatting it."""
    path = Path(file_path)
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            return source.read()
    except UnicodeDecodeError:
        # Older LaTeX files are often saved as Latin-1. Preserve the source
        # text rather than failing conversion; LaTeX itself can handle escaped
        # non-ASCII content when the document declares its input encoding.
        with path.open("r", encoding="latin-1", newline="") as source:
            return source.read()


def _normalize_latex_preamble(preamble: str) -> str:
    """Normalize insignificant whitespace when comparing LaTeX wrappers."""
    return re.sub(r"\s+", " ", preamble).strip()


def validate_latex_output(source_cv: str, optimized_cv: str) -> None:
    """Reject an optimizer result that is not the source LaTeX template.

    The optimizer is responsible for changing CV content, not replacing the
    document wrapper. A fragment without ``\\begin{document}`` cannot be
    compared as a complete document, so only its document-class marker is
    checked when present.
    """
    if not optimized_cv.strip():
        raise ValueError("The optimizer returned an empty LaTeX CV.")
    if "\\" in source_cv and "\\" not in optimized_cv:
        raise ValueError("The optimizer removed the source's LaTeX syntax.")

    document_begin = "\\begin{document}"
    document_end = "\\end{document}"
    source_has_document = document_begin in source_cv
    output_has_document = document_begin in optimized_cv

    if source_has_document:
        if not output_has_document:
            raise ValueError(
                "The optimized CV must retain the source's document environment."
            )
        if document_end in source_cv and document_end not in optimized_cv:
            raise ValueError(
                "The optimized CV must retain the source's document ending."
            )

        source_preamble = _normalize_latex_preamble(
            source_cv.split(document_begin, 1)[0]
        )
        output_preamble = _normalize_latex_preamble(
            optimized_cv.split(document_begin, 1)[0]
        )
        if source_preamble != output_preamble:
            raise ValueError(
                "The optimized CV changed the source's LaTeX template."
            )
    elif "\\documentclass" in source_cv and "\\documentclass" not in optimized_cv:
        raise ValueError(
            "The optimized CV must retain the source's LaTeX document class."
        )


def read_cv_text(file_path: str, original_filename: str) -> str:
    """Load an uploaded CV in the format expected by the agent workflow.

    ``.tex`` (and the commonly used ``.tax`` alias) is intentionally read as
    raw LaTeX. Other supported document types continue through MarkItDown.
    """
    if get_cv_source_format(original_filename) == "latex":
        return read_latex_source(file_path)
    return doc_to_markdown(file_path)


def generate_unique_filepath(original_name: str) -> str:
    random_key = generate_random_string()
    clean_filename = get_clean_filename(original_name)

    new_file_path = os.path.join(
        "files/",
        random_key + "_" + clean_filename,
    )
    os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

    while os.path.exists(new_file_path):
        random_key = generate_random_string()
        new_file_path = os.path.join(
            "files/",
            random_key + "_" + clean_filename,
        )

    return new_file_path


def get_clean_filename(orig_filename: str) -> str:
    clean_file_name = re.sub(r"[^\w.]", "", orig_filename.strip())
    cleaned_file_name = clean_file_name.replace(" ", "_")
    return cleaned_file_name


def generate_random_string() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(16))


async def save_file(file_path, file):
    import aiofiles

    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await file.read():
            await f.write(chunk)


def delete_file(file_path: str) -> bool:
    try:
        if not os.path.exists(file_path):
            return False

        os.remove(file_path)
        return True

    except Exception as e:
        print(f"Error deleting file: {e}")
        return False
