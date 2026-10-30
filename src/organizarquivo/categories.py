"""Categorias padrao do organizarquivo e utilitarios associados."""

from __future__ import annotations


CATEGORIES: dict[str, set[str]] = {
    "Documents": {
        ".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".md", ".tex",
        ".pages",
    },
    "Spreadsheets": {
        ".xlsx", ".xls", ".csv", ".ods", ".tsv",
    },
    "Presentations": {
        ".pptx", ".ppt", ".key", ".odp",
    },
    "Images": {
        ".jpeg", ".jpg", ".png", ".gif", ".webp", ".svg", ".ico",
        ".bmp", ".tiff", ".tif", ".heic", ".avif", ".raw",
    },
    "Videos": {
        ".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv",
        ".m4v", ".mpg", ".mpeg", ".3gp",
    },
    "Audios": {
        ".wav", ".mp3", ".flac", ".aac", ".ogg", ".m4a", ".wma",
        ".opus", ".aiff",
    },
    "Archives": {
        ".zip", ".rar", ".7z", ".tar", ".gz", ".tar.gz", ".bz2",
        ".xz", ".tgz", ".tbz2", ".zst", ".lz4", ".cab",
    },
    "Code": {
        ".py", ".pyw", ".ipynb", ".js", ".mjs", ".cjs", ".ts",
        ".jsx", ".tsx", ".cs", ".rs", ".go", ".java", ".kt",
        ".rb", ".php", ".html", ".htm", ".css", ".scss", ".sass",
        ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd", ".sql",
        ".c", ".h", ".cpp", ".hpp", ".cc", ".hh", ".lua", ".swift",
        ".dart", ".ex", ".exs", ".erl", ".hs", ".ml", ".fs", ".clj",
    },
    "Books": {
        ".epub", ".mobi", ".azw", ".azw3", ".fb2", ".djvu", ".cbz",
        ".cbr",
    },
    "Fonts": {
        ".ttf", ".otf", ".woff", ".woff2", ".eot", ".fon",
    },
    "3D": {
        ".blend", ".obj", ".fbx", ".stl", ".gltf", ".glb", ".ply",
        ".3ds", ".dae",
    },
    "Design": {
        ".psd", ".ai", ".sketch", ".fig", ".xd", ".indd", ".eps",
        ".afdesign", ".afphoto", ".xcf",
    },
    "Executables": {
        ".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".appimage",
        ".apk", ".jar", ".snap",
    },
    "Databases": {
        ".sqlite", ".sqlite3", ".db", ".mdb", ".accdb",
    },
}

OTHER = "Others"

INFRASTRUCTURE_DIRS: frozenset[str] = frozenset({
    ".git", ".hg", ".svn", ".venv", "venv", "env",
    "__pycache__", "node_modules", ".idea", ".vscode",
    "target", "dist", "build", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".tox", ".gradle", ".cache",
})


def category_for(extension: str, categories: dict[str, set[str]] | None = None) -> str:
    """Mapeia uma extensao (com ponto) para uma categoria.

    Se nenhuma categoria casar, devolve OTHER.
    Extensoes compostas (.tar.gz) sao testadas antes das simples.
    """
    ext = extension.lower()
    table = categories if categories is not None else CATEGORIES

    for name, extensions in table.items():
        if ext in extensions:
            return name

    return OTHER


def all_category_names(categories: dict[str, set[str]] | None = None) -> set[str]:
    table = categories if categories is not None else CATEGORIES
    return set(table) | {OTHER}
