import textwrap
import tomllib
from pathlib import Path
from typing import Optional, Dict, Any

marker_files = {"setup.py", "setup.cfg", "pyproject.toml", "requirements.txt"}


def validate_path(path: Path):
    """Validate that the given path contains a valid Python package.

    Args:
        path: The path to validate

    Raises:
        ValueError: If the path does not contain a valid Python package
    """
    if not (path / "__init__.py").exists():
        raise ValueError(f"Path '{path}' does not contain a valid Python package")


def find_project_root(path: Path) -> Path:
    """Find the root directory of the project containing the given path.

    The root directory is identified by the presence of marker files like
    setup.py, pyproject.toml, etc., or by the absence of __init__.py in
    the parent directory.

    Args:
        path: The path to start the search from

    Returns:
        The root directory of the project
    """
    while 1:
        for marker in marker_files:
            if (path.parent / marker).exists():
                return path

        if not (path.parent / "__init__.py").exists():
            return path

        path = path.parent


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from a TOML file.

    If no config path is provided, looks for di.toml in the current directory
    or in the parent directory of the project root.

    Args:
        config_path: Path to the configuration file, or None to use default locations

    Returns:
        Dictionary containing the configuration, or an empty dictionary if no
        configuration file was found or if an error occurred while loading it
    """
    if config_path is None:
        config_path = Path.cwd() / "di.toml"

        if not config_path.exists():
            project_root = find_project_root(config_path)
            config_path = project_root.parent / "di.toml"

    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            print(f"Error loading config from {config_path}: {e}")

    return {}


def frame_text_with_centered_title(text: str, title: str = "", padding: int = 1, width: int = 100) -> str:
    wrapped_lines = []

    for line in text.strip().splitlines():
        wrapped = textwrap.wrap(line, width=width)
        wrapped_lines.extend(wrapped or [""])

    if not wrapped_lines:
        return ""

    max_len = max(len(line) for line in wrapped_lines)
    content_width = max_len + padding * 2

    # We form the upper frame with the heading aligned in the center.
    if title:
        title_str = f" {title} "
        left_len = (content_width - len(title_str)) // 2
        right_len = content_width - len(title_str) - left_len
        top = f"┌{'─' * left_len}{title_str}{'─' * right_len}┐"
    else:
        top = f"┌{'─' * content_width}┐"

    bottom = f"└{'─' * content_width}┘"

    result = [top]

    for line in wrapped_lines:
        padded = f"{' ' * padding}{line.ljust(max_len)}{' ' * padding}"
        result.append(f"│{padded}│")

    result.append(bottom)

    return "\n".join(result)
