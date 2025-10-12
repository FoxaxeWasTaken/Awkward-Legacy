"""
page_serializer.py

GeneWeb extended page serializer.

Design goals:
- Convert a pages dictionary into GeneWeb-compatible page-ext blocks
- Preserve keys and values for page metadata and content
- Ensure clean formatting compatible with GeneWeb `.gw` files

Functions:
    - serialize_pages: Serializes extended pages dictionary into GeneWeb format
"""

from typing import Dict


def serialize_pages(pages: Dict[str, Dict[str, str]]) -> str:
    """
    Serialize extended pages into GeneWeb `.gw` page-ext blocks.

    Args:
        pages (Dict[str, Dict[str, str]]): Dictionary where keys are page names
            and values are dictionaries of page content.

    Returns:
        str: GeneWeb-formatted extended pages as a single string.
    """
    all_blocks = []

    for page_name, content in pages.items():
        block_lines = []
        block_lines.append(f'# extended page "{page_name}" used by:')
        block_lines.append(f"page-ext {page_name}")
        for k, v in content.items():
            block_lines.append(f"{k}={v}")
        block_lines.append("end page-ext")
        all_blocks.append("\n".join(block_lines))

    return "\n\n".join(all_blocks)
