"""
Allow running the package as a module: python -m huoshui_pdf_converter
"""

from .cli import main

if __name__ == "__main__":
    main()