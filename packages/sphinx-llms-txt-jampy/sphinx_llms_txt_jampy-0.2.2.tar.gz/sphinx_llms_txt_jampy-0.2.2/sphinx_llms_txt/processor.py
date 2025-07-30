"""
Document processor module for sphinx-llms-txt.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sphinx.util import logging

logger = logging.getLogger(__name__)


def build_directive_pattern(directives):
    """Build a regex pattern for directives.

    Args:
        directives: List of directive names to match

    Returns:
        A compiled regex pattern that matches the specified directives
    """
    directives_pattern = "|".join(re.escape(d) for d in directives)
    return re.compile(
        r"^(\s*\.\.\s+(" + directives_pattern + r")::\s+)([^\s].+?)$", re.MULTILINE
    )


class DocumentProcessor:
    """Processes document content, handling includes and directives."""

    def __init__(self, config: Dict[str, Any], srcdir: Optional[str] = None):
        self.config = config
        self.srcdir = srcdir

    def process_content(self, content: str, source_path: Path) -> str:
        """Process directives in content that need path resolution.

        Args:
            content: The source content to process
            source_path: Path to the source file (to resolve relative paths)

        Returns:
            Processed content with directives properly resolved
        """
        # First process include directives
        content = self._process_includes(content, source_path)

        # Then process path directives (image, figure, etc.)
        content = self._process_path_directives(content, source_path)

        return content

    def _extract_relative_document_path(
        self, source_path: Path
    ) -> Tuple[Optional[str], Optional[str], Optional[List[str]]]:
        """Extract the relative document path from a source file in _sources or srcdir.

        Returns:
            Tuple of (rel_doc_path, rel_doc_dir, rel_doc_path_parts)
        """
        try:
            path_str = str(source_path)

            # Case 1: under _sources/ directory
            if "_sources/" in path_str:
                rel_doc_path = path_str.split("_sources/")[1]

            # Case 2: fallback to relative to source directory
            elif self.srcdir and Path(path_str).startswith(str(self.srcdir)):
                rel_doc_path = str(Path(source_path).relative_to(Path(self.srcdir)))

            else:
                return None, None, None

            # Remove .txt extension if present
            if rel_doc_path.endswith(".txt"):
                rel_doc_path = rel_doc_path[:-4]

            rel_doc_dir = os.path.dirname(rel_doc_path)
            rel_doc_path_parts = rel_doc_path.split("/")

            return rel_doc_path, rel_doc_dir, rel_doc_path_parts

        except Exception as e:
            logger.debug(f"✨sphinx-llms-txt: Error extracting relative path: {e}")

        return None, None, None

    def _add_base_url(self, path: str, base_url: str) -> str:
        """Add base URL to a path if needed.

        Args:
            path: The path to add the base URL to
            base_url: The base URL to add

        Returns:
            Path with base URL added if applicable
        """
        if not base_url:
            return path

        if not base_url.endswith("/"):
            base_url += "/"
        return f"{base_url}{path}"

    def _is_absolute_or_url(self, path: str) -> bool:
        """Check if a path is absolute or a URL.

        Args:
            path: The path to check

        Returns:
            True if the path is absolute or a URL, False otherwise
        """
        return path.startswith(("http://", "https://", "/", "data:"))
    def _is_absolute_or_url(self, path: str) -> bool:
        """Check if a path is a true system absolute path or external URL.

        Sphinx-root-relative paths like '/admin/_images/...' are allowed.
        """
        if path.startswith(("/_images/", "/_static/")):
            return False  # Allow these to be rewritten
        if re.match(r"^/[a-zA-Z0-9_\-]+/_images/", path):
            return False  # Allow subdir paths like '/admin/_images/foo.png'
        return path.startswith(("http://", "https://", "/", "data:"))

    def _process_path_directives(self, content: str, source_path: Path) -> str:
        """Process directives with paths that need to be resolved.

        Args:
            content: The source content to process
            source_path: Path to the source file (to resolve relative paths)

        Returns:
            Processed content with directive paths properly resolved
        """
        # Get the configured path directives to process
        default_path_directives = ["image", "figure"]
        custom_path_directives = self.config.get("llms_txt_directives")
        path_directives = set(default_path_directives + custom_path_directives)

        # Build the regex pattern to match all configured directives
        directive_pattern = build_directive_pattern(path_directives)

        # Get the base URL from Sphinx's html_baseurl if set
        base_url = self.config.get("html_baseurl", "")

        # Handle test case specially
        is_test = "pytest" in str(source_path) and "subdir" in str(source_path)

        def replace_directive_path(match, base_url=base_url, is_test=is_test):
            prefix = match.group(1)
            path = match.group(3).strip()

            # Get just the filename from any path like foo.png, _images/foo.png, admin/_images/foo.png
            filename = os.path.basename(path)

            # Normalize to _images/filename
            image_path = f"_images/{filename}"

            # Apply base URL if present
            if base_url:
                full_path = self._add_base_url(image_path, base_url)
            else:
                full_path = image_path

            return f"{prefix}{full_path}"

#            print(f"✨{prefix}{full_path}")
            return f"{prefix}{full_path}"

        # Replace directive paths in the content
        processed_content = directive_pattern.sub(replace_directive_path, content)
        return processed_content

    def _resolve_include_paths(
        self, include_path: str, source_path: Path
    ) -> List[Path]:
        """Resolve possible paths for an include directive.

        Args:
            include_path: The path from the include directive
            source_path: The path to the source file

        Returns:
            List of possible paths to try
        """
        possible_paths = []

        # If it's an absolute path, use it directly
        if os.path.isabs(include_path):
            possible_paths.append(Path(include_path))
        else:
            # Relative to the source file (in _sources directory)
            possible_paths.append((source_path.parent / include_path).resolve())

            # If we're in _sources directory, try relative to the original source
            # directory
            if "_sources" in str(source_path):
                # Extract the relative path portion from the source path
                rel_path, rel_dir, _ = self._extract_relative_document_path(source_path)

                # If we have the original source directory from Sphinx
                if self.srcdir:
                    # Try in the srcdir root
                    possible_paths.append((Path(self.srcdir) / include_path).resolve())

                    # If we have a relative path, try in the corresponding source
                    # subdirectory
                    if rel_path and rel_dir:
                        possible_paths.append(
                            (Path(self.srcdir) / rel_dir / include_path).resolve()
                        )
#        print(possible_paths)
        return possible_paths

    def _process_includes(self, content: str, source_path: Path) -> str:
        """Process include directives in content.

        Args:
            content: The source content to process
            source_path: Path to the source file (to resolve relative paths)

        Returns:
            Processed content with include directives replaced with included content
        """
        # Find all include directives using regex
        include_pattern = build_directive_pattern(["include"])

        # Function to replace each include with content
        def replace_include(match):
            include_path = match.group(3)

            # Get all possible paths to try
            possible_paths = self._resolve_include_paths(include_path, source_path)

            # Try each possible path
            for path_to_try in possible_paths:
                try:
                    if path_to_try.exists():
                        with open(path_to_try, "r", encoding="utf-8") as f:
                            included_content = f.read()
                        return included_content
                except Exception as e:
                    logger.error(
                        f"sphinx-llms-txt: Error reading include file {path_to_try}:"
                        f" {e}"
                    )
                    continue

            # If we get here, we couldn't find the file
            paths_tried = ", ".join(str(p) for p in possible_paths)
            logger.warning(f"sphinx-llms-txt: Include file not found: {include_path}")
            logger.debug(f"sphinx-llms-txt: Tried paths: {paths_tried}")
            return f"[Include file not found: {include_path}]"

        # Replace all includes with their content
        processed_content = include_pattern.sub(replace_include, content)
        return processed_content
