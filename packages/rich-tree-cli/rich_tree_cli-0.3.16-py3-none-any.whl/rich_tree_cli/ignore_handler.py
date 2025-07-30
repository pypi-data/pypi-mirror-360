"""Python module to handle ignore patterns for file paths in a directory tree."""

from pathlib import Path

from pathspec import PathSpec

IGNORE_PATTERNS: list[str] = [
    "__pycache__",
    ".git",
    ".venv",
    ".env",
    ".vscode",
    ".idea",
    "*.DS_Store*",
    "__pypackages__",
    ".pytest_cache",
    ".coverage",
    ".*.swp",
    ".*.swo",
    "*.lock",
    "**/.nox",
    "dist",
    "**/.ruff_cache",
    "**/.github",
]


class IgnoreHandler:
    """Class to handle ignore patterns for file paths."""

    def __init__(self, gitignore_file: Path | None = None) -> None:
        """Initialize the IgnoreHandler with default and optional gitignore patterns."""
        self.patterns = IGNORE_PATTERNS.copy()
        if gitignore_file and gitignore_file.exists():
            git_lines = [
                line.strip()
                for line in gitignore_file.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            self.patterns.extend(git_lines)
        self.spec: PathSpec = self._create_spec(self.patterns)

    @staticmethod
    def _create_spec(patterns: list[str]) -> PathSpec:
        """Create a pathspec from the given patterns.

        Args:
            patterns: List of ignore patterns

        Returns:
            A pathspec object
        """
        return PathSpec.from_lines("gitwildmatch", patterns)

    def should_ignore(self, path: Path | str) -> bool:
        """Check if a given path should be ignored based on the ignore patterns.

        Args:
            path (Path): The path to check
        Returns:
            bool: True if the path should be ignored, False otherwise
        """
        if isinstance(path, str):
            path = path.replace("\\", "/")

        path_obj = Path(path).expanduser()
        path_str = path_obj.as_posix()

        if path_obj.is_dir() and not path_str.endswith("/"):
            path_str += "/"

        return self.spec.match_file(path_str)

    def add_patterns(self, patterns: list[str]) -> None:
        """Add a new pattern to the ignore list.

        Args:
            pattern (str): The pattern to add
        """
        for pattern in patterns:
            if pattern not in self.spec.patterns:
                self.patterns.append(pattern)
        self.spec = self._create_spec(self.patterns)
