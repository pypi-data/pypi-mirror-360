"""
Huoshui PDF Converter - High-quality PDF ↔ Markdown converter

A cross-platform converter with full Unicode/CJK support and MCP integration.
"""

__version__ = "1.0.3"
__author__ = "Huoshui Development Team"
__email__ = "dev@huoshui.ai"

__all__ = [
    "PDFToMarkdownConverter",
    "MarkdownToPDFConverter",
]

# Lazy imports to avoid import errors during package initialization
def __getattr__(name):
    if name == "PDFToMarkdownConverter":
        from .pdf_converter import PDFToMarkdownConverter
        return PDFToMarkdownConverter
    elif name == "MarkdownToPDFConverter":
        from .markdown_converter import MarkdownToPDFConverter
        return MarkdownToPDFConverter
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")