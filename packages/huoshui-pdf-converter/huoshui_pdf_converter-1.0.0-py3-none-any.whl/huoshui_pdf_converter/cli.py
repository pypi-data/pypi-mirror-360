#!/usr/bin/env python3
"""
Command-line interface for Huoshui PDF Converter
"""

import asyncio
import sys
import argparse
from pathlib import Path

from .pdf_converter import PDFToMarkdownConverter
from .markdown_converter import MarkdownToPDFConverter


async def pdf_to_markdown(args):
    """Convert PDF to Markdown"""
    converter = PDFToMarkdownConverter()
    result = await converter.convert(
        pdf_path=args.input,
        output_path=args.output,
        extract_images=args.extract_images,
        preserve_formatting=args.preserve_formatting
    )
    
    if result['success']:
        print(f"✅ Successfully converted {args.input} to {args.output}")
        if 'stats' in result:
            stats = result['stats']
            print(f"   Pages: {stats.get('pages', 'N/A')}")
            print(f"   Images: {stats.get('images_extracted', 0)}")
    else:
        print(f"❌ Conversion failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


async def markdown_to_pdf(args):
    """Convert Markdown to PDF"""
    converter = MarkdownToPDFConverter()
    result = await converter.convert(
        markdown_path=args.input,
        output_path=args.output,
        page_size=args.page_size,
        margin=args.margin,
        font_size=args.font_size
    )
    
    if result['success']:
        print(f"✅ Successfully converted {args.input} to {args.output}")
        if 'stats' in result:
            stats = result['stats']
            print(f"   Engine: {stats.get('engine', 'N/A')}")
            print(f"   Size: {stats.get('output_size', 0):,} bytes")
    else:
        print(f"❌ Conversion failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Huoshui PDF Converter - High-quality PDF ↔ Markdown converter"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # PDF to Markdown command
    pdf_parser = subparsers.add_parser('pdf-to-md', help='Convert PDF to Markdown')
    pdf_parser.add_argument('input', help='Input PDF file')
    pdf_parser.add_argument('output', help='Output Markdown file')
    pdf_parser.add_argument('--no-images', dest='extract_images', 
                           action='store_false', default=True,
                           help='Do not extract images')
    pdf_parser.add_argument('--no-formatting', dest='preserve_formatting',
                           action='store_false', default=True,
                           help='Do not preserve formatting')
    
    # Markdown to PDF command
    md_parser = subparsers.add_parser('md-to-pdf', help='Convert Markdown to PDF')
    md_parser.add_argument('input', help='Input Markdown file')
    md_parser.add_argument('output', help='Output PDF file')
    md_parser.add_argument('--page-size', default='A4',
                          choices=['A4', 'A3', 'Letter', 'Legal'],
                          help='Page size (default: A4)')
    md_parser.add_argument('--margin', default='2cm',
                          help='Page margin (default: 2cm)')
    md_parser.add_argument('--font-size', type=int, default=12,
                          help='Font size in points (default: 12)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Run the appropriate command
    if args.command == 'pdf-to-md':
        asyncio.run(pdf_to_markdown(args))
    elif args.command == 'md-to-pdf':
        asyncio.run(markdown_to_pdf(args))


if __name__ == "__main__":
    main()