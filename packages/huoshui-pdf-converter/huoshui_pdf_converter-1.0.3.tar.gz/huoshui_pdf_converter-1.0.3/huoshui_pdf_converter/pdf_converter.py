"""
PDF to Markdown converter
Uses PyMuPDF as the primary conversion engine
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

# Import PyMuPDF
try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False
    raise RuntimeError("PyMuPDF not installed. Please install: pip install PyMuPDF")

logger = logging.getLogger(__name__)

class PDFToMarkdownConverter:
    """PDF to Markdown converter - based on PyMuPDF"""
    
    def __init__(self):
        if not HAS_FITZ:
            raise RuntimeError("PyMuPDF not installed. Please install: pip install PyMuPDF")
        self.engine = "pymupdf"
    
    async def convert(
        self,
        pdf_path: str,
        output_path: str,
        extract_images: bool = True,
        preserve_formatting: bool = True
    ) -> Dict[str, Any]:
        """
        Convert PDF to Markdown
        
        Args:
            pdf_path: PDF file path
            output_path: Output Markdown file path
            extract_images: Whether to extract images
            preserve_formatting: Whether to preserve formatting
            
        Returns:
            Conversion result information
        """
        start_time = datetime.now()
        
        try:
            # Create output directory
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert using PyMuPDF
            result = await self._convert_with_pymupdf(
                pdf_path, output_path, extract_images, preserve_formatting
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Statistics
            stats = {
                "source_file": pdf_path,
                "output_file": output_path,
                "engine": "pymupdf",
                "duration_seconds": duration,
                "extract_images": extract_images,
                "preserve_formatting": preserve_formatting,
                "conversion_time": end_time.isoformat(),
                **result
            }
            
            logger.info(f"PDF conversion completed: {pdf_path} -> {output_path}")
            return {
                "success": True,
                "message": "PDF converted to Markdown successfully",
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"PDF conversion failed: {str(e)}")
            return {
                "success": False,
                "message": f"PDF conversion failed: {str(e)}",
                "error": str(e)
            }
    
    async def _convert_with_pymupdf(
        self,
        pdf_path: str,
        output_path: str,
        extract_images: bool,
        preserve_formatting: bool
    ) -> Dict[str, Any]:
        """Convert using PyMuPDF"""
        
        doc = fitz.open(pdf_path)
        markdown_content = []
        image_count = 0
        images_dir = None
        
        if extract_images:
            images_dir = Path(output_path).parent / f"{Path(output_path).stem}_images"
            images_dir.mkdir(exist_ok=True)
        
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Add page separator (except for first page)
                if page_num > 0:
                    markdown_content.append("\n---\n")
                
                # Extract text
                if preserve_formatting:
                    # Format-preserving text extraction
                    blocks = page.get_text("dict")
                    page_md = await self._process_text_blocks(blocks)
                else:
                    # Simple text extraction
                    page_md = page.get_text()
                
                if page_md.strip():
                    markdown_content.append(page_md)
                
                # Extract images
                if extract_images:
                    image_list = page.get_images()
                    for img_index, img in enumerate(image_list):
                        try:
                            xref = img[0]
                            pix = fitz.Pixmap(doc, xref)
                            
                            if pix.n < 5:  # Only process RGB or grayscale images
                                img_name = f"image_page{page_num + 1}_{img_index + 1}.png"
                                img_path = images_dir / img_name
                                pix.save(str(img_path))
                                
                                # Insert image reference in Markdown
                                rel_path = f"{images_dir.name}/{img_name}"
                                markdown_content.append(f"\n![Image {page_num + 1}-{img_index + 1}]({rel_path})\n")
                                image_count += 1
                            
                            pix = None
                        except Exception as e:
                            logger.warning(f"Image extraction failed (page {page_num + 1}, image {img_index + 1}): {str(e)}")
            
            # Merge content and clean
            final_content = "\n".join(markdown_content)
            final_content = self._clean_markdown(final_content)
            
            # Write Markdown file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            return {
                "pages_processed": len(doc),
                "images_extracted": image_count,
                "output_size": len(final_content),
                "images_directory": str(images_dir) if images_dir and image_count > 0 else None
            }
            
        finally:
            doc.close()
    
    async def _process_text_blocks(self, blocks: Dict) -> str:
        """Process text blocks to preserve formatting"""
        markdown_lines = []
        
        for block in blocks.get("blocks", []):
            if block.get("type") == 0:  # Text block
                block_text = []
                
                for line in block.get("lines", []):
                    line_text = []
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        flags = span.get("flags", 0)
                        size = span.get("size", 12)
                        
                        # Determine heading level based on font size
                        if size > 16:
                            text = f"# {text}"
                        elif size > 14:
                            text = f"## {text}"
                        elif size > 12:
                            text = f"### {text}"
                        
                        # Add Markdown formatting based on font flags
                        if flags & 2**4:  # Bold
                            text = f"**{text}**"
                        if flags & 2**1:  # Italic
                            text = f"*{text}*"
                        
                        line_text.append(text)
                    
                    if line_text:
                        block_text.append("".join(line_text))
                
                if block_text:
                    markdown_lines.append("\n".join(block_text))
        
        return "\n\n".join(markdown_lines)
    
    def _clean_markdown(self, content: str) -> str:
        """Clean Markdown content"""
        # Remove excess empty lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Clean leading and trailing whitespace
        content = content.strip()
        
        # Ensure code block format is correct
        content = re.sub(r'```([^`]+)```', r'```\n\1\n```', content)
        
        return content
    
    def get_supported_engines(self) -> List[str]:
        """Get list of supported engines"""
        return ["pymupdf"]
    
    async def validate_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Validate PDF file"""
        try:
            path = Path(pdf_path)
            
            if not path.exists():
                return {"valid": False, "error": "File does not exist"}
            
            if not path.is_file():
                return {"valid": False, "error": "Not a file"}
            
            if path.suffix.lower() != '.pdf':
                return {"valid": False, "error": "Not a PDF file"}
            
            # Try to open PDF with PyMuPDF
            try:
                doc = fitz.open(pdf_path)
                page_count = len(doc)
                doc.close()
                return {
                    "valid": True,
                    "page_count": page_count,
                    "file_size": path.stat().st_size,
                    "engine": "pymupdf"
                }
            except Exception as e:
                return {"valid": False, "error": f"PDF file corrupted: {str(e)}"}
                
        except Exception as e:
            return {"valid": False, "error": f"Validation failed: {str(e)}"}