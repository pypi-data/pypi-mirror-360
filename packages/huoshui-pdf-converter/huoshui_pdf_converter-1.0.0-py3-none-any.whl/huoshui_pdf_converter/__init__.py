"""
Huoshui PDF Converter - High-quality PDF ↔ Markdown converter

A cross-platform converter with full Unicode/CJK support and MCP integration.
"""

__version__ = "1.0.0"
__author__ = "Huoshui Development Team"
__email__ = "dev@huoshui.ai"

from .pdf_converter import PDFToMarkdownConverter
from .markdown_converter import MarkdownToPDFConverter

__all__ = [
    "PDFToMarkdownConverter",
    "MarkdownToPDFConverter",
]