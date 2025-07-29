#!/usr/bin/env python3
"""
Huoshui PDF Converter - DXT Extension MCP Server (FastMCP)
Provides bidirectional conversion between PDF and Markdown
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Add the lib directory to Python path for DXT environment
script_dir = Path(__file__).parent
lib_dir = script_dir / "lib"
if lib_dir.exists():
    sys.path.insert(0, str(lib_dir))

from fastmcp import FastMCP
from fastmcp.prompts import Prompt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('huoshui_pdf_converter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import converters with multiple fallbacks for compatibility
import_errors = []
PDFToMarkdownConverter = None
MarkdownToPDFConverter = None

try:
    # First try relative import (package structure)
    from .pdf_converter import PDFToMarkdownConverter
    from .markdown_converter import MarkdownToPDFConverter
    logger.info("Successfully imported converters using relative imports")
except ImportError as e:
    import_errors.append(f"Relative import failed: {e}")
    try:
        # Try absolute import from package
        from huoshui_pdf_converter.pdf_converter import PDFToMarkdownConverter
        from huoshui_pdf_converter.markdown_converter import MarkdownToPDFConverter
        logger.info("Successfully imported converters using absolute imports")
    except ImportError as e2:
        import_errors.append(f"Absolute import failed: {e2}")
        try:
            # Finally try direct import (for DXT with lib in path)
            from pdf_converter import PDFToMarkdownConverter
            from markdown_converter import MarkdownToPDFConverter
            logger.info("Successfully imported converters using direct imports")
        except ImportError as e3:
            import_errors.append(f"Direct import failed: {e3}")
            logger.error(f"All import attempts failed:\n" + "\n".join(import_errors))
            logger.error(f"Current sys.path: {sys.path}")
            logger.error(f"Current working directory: {os.getcwd()}")
            logger.error(f"Script directory: {script_dir}")
            raise ImportError(f"Could not import converters. Errors: {import_errors}")

# Create FastMCP server
mcp = FastMCP(
    name="huoshui-pdf-converter"
)

@mcp.tool
async def pdf_to_markdown(
    pdf_path: str,
    output_path: Optional[str] = None,
    extract_images: bool = True,
    preserve_formatting: bool = True
) -> str:
    """Convert PDF file to Markdown format."""
    try:
        # Always use absolute import for maximum compatibility
        from huoshui_pdf_converter.pdf_converter import PDFToMarkdownConverter
        converter_class = PDFToMarkdownConverter
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF file")
        
        converter = converter_class()
        
        # Generate output path if not provided
        if output_path is None:
            output_path = pdf_path.replace('.pdf', '.md')
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert PDF to Markdown
        result = await converter.convert(
            pdf_path=pdf_path,
            output_path=output_path,
            extract_images=extract_images,
            preserve_formatting=preserve_formatting
        )
        
        logger.info(f"PDF to Markdown conversion completed: {pdf_path} -> {output_path}")
        if result.get("success"):
            return f"Successfully converted PDF to Markdown: {output_path}"
        else:
            raise Exception(result.get("message", "Unknown error"))
        
    except Exception as e:
        error_msg = f"PDF to Markdown conversion failed: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

@mcp.tool
async def markdown_to_pdf(
    markdown_path: str,
    output_path: Optional[str] = None,
    page_size: str = "A4",
    margin: str = "1cm",
    font_size: int = 12
) -> str:
    """Convert Markdown file to PDF format."""
    try:
        # Always use absolute import for maximum compatibility
        from huoshui_pdf_converter.markdown_converter import MarkdownToPDFConverter
        converter_class = MarkdownToPDFConverter
        
        if not os.path.exists(markdown_path):
            raise FileNotFoundError(f"Markdown file not found: {markdown_path}")
        
        if not markdown_path.lower().endswith(('.md', '.markdown')):
            raise ValueError("File must be a Markdown file")
        
        converter = converter_class()
        
        # Generate output path if not provided
        if output_path is None:
            output_path = markdown_path.replace('.md', '.pdf').replace('.markdown', '.pdf')
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert Markdown to PDF
        result = await converter.convert(
            markdown_path=markdown_path,
            output_path=output_path,
            page_size=page_size,
            margin=margin,
            font_size=font_size
        )
        
        logger.info(f"Markdown to PDF conversion completed: {markdown_path} -> {output_path}")
        if result.get("success"):
            return f"Successfully converted Markdown to PDF: {output_path}"
        else:
            raise Exception(result.get("message", "Unknown error"))
        
    except Exception as e:
        import traceback
        error_msg = f"Markdown to PDF conversion failed: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise Exception(error_msg)

@mcp.tool
async def list_supported_formats() -> str:
    """List supported file formats and conversion options."""
    try:
        formats_info = {
            "supported_formats": {
                "input": {
                    "pdf": {
                        "description": "Portable Document Format",
                        "extensions": [".pdf"],
                        "can_convert_to": ["markdown"]
                    },
                    "markdown": {
                        "description": "Markdown markup language",
                        "extensions": [".md", ".markdown"],
                        "can_convert_to": ["pdf"]
                    }
                },
                "output": {
                    "pdf": {
                        "description": "Portable Document Format",
                        "page_sizes": ["A4", "A3", "Letter", "Legal"],
                        "supported_margins": "CSS-style margins (e.g., '1cm', '0.5in')",
                        "font_sizes": "8-72 points"
                    },
                    "markdown": {
                        "description": "Markdown markup language",
                        "features": [
                            "Image extraction",
                            "Format preservation",
                            "Table support",
                            "Link preservation"
                        ]
                    }
                }
            },
            "conversion_options": {
                "pdf_to_markdown": {
                    "extract_images": "Extract images from PDF (default: true)",
                    "preserve_formatting": "Preserve original formatting (default: true)"
                },
                "markdown_to_pdf": {
                    "page_size": "PDF page size (default: A4)",
                    "margin": "Page margin (default: 1cm)",
                    "font_size": "Font size in points (default: 12)"
                }
            }
        }
        
        return json.dumps(formats_info, indent=2)
        
    except Exception as e:
        error_msg = f"Failed to list supported formats: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

@mcp.tool
async def validate_file(file_path: str) -> str:
    """Validate file format and convertibility."""
    try:
        if not os.path.exists(file_path):
            return json.dumps({
                "valid": False,
                "error": "File not found",
                "file_path": file_path
            })
        
        file_ext = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        
        validation_result = {
            "valid": False,
            "file_path": file_path,
            "file_size": file_size,
            "file_extension": file_ext,
            "convertible_to": [],
            "validation_details": {}
        }
        
        if file_ext == '.pdf':
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                page_count = len(doc)
                doc.close()
                
                validation_result.update({
                    "valid": True,
                    "file_type": "PDF",
                    "convertible_to": ["markdown"],
                    "validation_details": {
                        "page_count": page_count,
                        "readable": True
                    }
                })
            except Exception as e:
                validation_result["validation_details"]["error"] = str(e)
                
        elif file_ext in ['.md', '.markdown']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    word_count = len(content.split())
                    
                validation_result.update({
                    "valid": True,
                    "file_type": "Markdown",
                    "convertible_to": ["pdf"],
                    "validation_details": {
                        "word_count": word_count,
                        "readable": True
                    }
                })
            except Exception as e:
                validation_result["validation_details"]["error"] = str(e)
        else:
            validation_result["validation_details"]["error"] = "Unsupported file format"
        
        return json.dumps(validation_result, indent=2)
        
    except Exception as e:
        error_msg = f"File validation failed: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

# Define prompts
@mcp.prompt
async def convert_pdf_to_markdown(pdf_file: str) -> str:
    """Complete workflow guide for converting PDF to Markdown."""
    return f"""我将帮助您将PDF文件转换为Markdown格式。

步骤：
1. 首先验证PDF文件：{pdf_file}
2. 使用pdf_to_markdown工具进行转换
3. 可选参数：
   - extract_images: 是否提取图片（默认：true）
   - preserve_formatting: 是否保留格式（默认：true）
   - output_path: 输出路径（可选）

让我开始转换过程..."""

@mcp.prompt  
async def convert_markdown_to_pdf(markdown_file: str) -> str:
    """Complete workflow guide for converting Markdown to PDF."""
    return f"""我将帮助您将Markdown文件转换为PDF格式。

步骤：
1. 首先验证Markdown文件：{markdown_file}
2. 使用markdown_to_pdf工具进行转换
3. 可选参数：
   - page_size: 页面大小（默认：A4）
   - margin: 页边距（默认：1cm）
   - font_size: 字体大小（默认：12）
   - output_path: 输出路径（可选）

让我开始转换过程..."""

@mcp.prompt
async def batch_convert(source_directory: str, target_format: str) -> str:
    """Batch file conversion guide."""
    return f"""我将帮助您批量转换文件。

目录：{source_directory}
目标格式：{target_format}

步骤：
1. 扫描目录中的所有支持文件
2. 逐个验证文件格式
3. 根据目标格式选择转换工具
4. 执行批量转换

支持的转换：
- PDF → Markdown
- Markdown → PDF

让我开始批量转换过程..."""

def main():
    """Run the FastMCP server."""
    try:
        logger.info("Starting Huoshui PDF Converter FastMCP server...")
        mcp.run()
    except Exception as e:
        logger.error(f"Server startup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
