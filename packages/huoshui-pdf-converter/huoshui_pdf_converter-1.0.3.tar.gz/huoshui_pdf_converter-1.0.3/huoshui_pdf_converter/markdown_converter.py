"""
Markdown to PDF converter
Multi-engine approach for maximum portability and quality
Priority: xhtml2pdf > ReportLab > fpdf2
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

# Import conversion libraries
try:
    import markdown
    from markdown.extensions import tables, codehilite, toc, fenced_code
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False
    raise RuntimeError("python-markdown not installed. Please install: pip install markdown")

# Test engines in order of preference (quality vs portability)

# Engine 1: xhtml2pdf (good quality, pure Python)
try:
    from xhtml2pdf import pisa
    HAS_XHTML2PDF = True
except ImportError:
    HAS_XHTML2PDF = False
    logger.info("xhtml2pdf not available")

# Engine 2: ReportLab (acceptable quality, excellent portability)
try:
    from reportlab.lib.pagesizes import letter, A4, A3, legal
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    logger.info("ReportLab not available")

# Engine 3: fpdf2 (basic quality, excellent portability)
try:
    from fpdf import FPDF
    HAS_FPDF2 = True
except ImportError:
    HAS_FPDF2 = False
    logger.info("fpdf2 not available")

# Engine 4: WeasyPrint (excellent quality, poor portability - requires system libs)
try:
    # Set library paths for macOS Homebrew
    import platform
    import glob
    if platform.system() == "Darwin":
        homebrew_lib_paths = [
            "/opt/homebrew/lib",
            "/usr/local/lib"
        ]
        # Find glib dynamically
        glib_paths = glob.glob("/opt/homebrew/Cellar/glib/*/lib")
        if glib_paths:
            homebrew_lib_paths.extend(glib_paths)
        
        current_path = os.environ.get("DYLD_LIBRARY_PATH", "")
        new_paths = [p for p in homebrew_lib_paths if os.path.exists(p)]
        if new_paths:
            os.environ["DYLD_LIBRARY_PATH"] = ":".join(new_paths + [current_path])
    
    import weasyprint
    HAS_WEASYPRINT = True
except (ImportError, OSError) as e:
    HAS_WEASYPRINT = False
    logger.info(f"WeasyPrint not available: {str(e)}")

class MarkdownToPDFConverter:
    """Markdown to PDF converter with multiple engine fallback for maximum portability"""
    
    def __init__(self):
        if not HAS_MARKDOWN:
            raise RuntimeError("python-markdown not installed. Please install: pip install markdown")
        
        # Select best available engine
        self._available_engines = []
        if HAS_XHTML2PDF:
            self._available_engines.append("xhtml2pdf")
        if HAS_WEASYPRINT:
            self._available_engines.append("weasyprint")
        if HAS_REPORTLAB:
            self._available_engines.append("reportlab")
        if HAS_FPDF2:
            self._available_engines.append("fpdf2")
            
        if not self._available_engines:
            raise RuntimeError("No PDF generation engine available. Please install one of: xhtml2pdf, reportlab, fpdf2, or weasyprint")
        
        # Default engine selection
        if HAS_XHTML2PDF:
            self.engine = "xhtml2pdf"
            logger.info("Default engine: xhtml2pdf (good quality, pure Python)")
        elif HAS_WEASYPRINT:
            self.engine = "weasyprint"
            logger.info("Default engine: WeasyPrint (excellent quality, requires system libs)")
        elif HAS_REPORTLAB:
            self.engine = "reportlab"
            logger.info("Default engine: ReportLab (acceptable quality, excellent portability)")
        else:
            self.engine = "fpdf2"
            logger.info("Default engine: fpdf2 (basic quality, excellent portability)")
    
    async def convert(
        self,
        markdown_path: str,
        output_path: str,
        page_size: str = "A4",
        margin: str = "1cm",
        font_size: int = 12
    ) -> Dict[str, Any]:
        """
        Convert Markdown to PDF
        
        Args:
            markdown_path: Markdown file path
            output_path: Output PDF file path
            page_size: Page size
            margin: Page margin
            font_size: Font size
            
        Returns:
            Conversion result information
        """
        start_time = datetime.now()
        
        try:
            # Create output directory
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Read Markdown file
            with open(markdown_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Detect if content has CJK characters and switch engine if needed
            if self._has_cjk_characters(markdown_content):
                if self.engine == "xhtml2pdf" and "reportlab" in self._available_engines:
                    logger.info("CJK characters detected, switching to ReportLab for better Unicode support")
                    self.engine = "reportlab"
            
            # Convert using selected engine
            if self.engine == "xhtml2pdf":
                result = await self._convert_with_xhtml2pdf(
                    markdown_content, output_path, page_size, margin, font_size
                )
            elif self.engine == "weasyprint":
                result = await self._convert_with_weasyprint(
                    markdown_content, output_path, page_size, margin, font_size, markdown_path
                )
            elif self.engine == "reportlab":
                result = await self._convert_with_reportlab(
                    markdown_content, output_path, page_size, margin, font_size
                )
            elif self.engine == "fpdf2":
                result = await self._convert_with_fpdf2(
                    markdown_content, output_path, page_size, margin, font_size
                )
            else:
                raise RuntimeError(f"Unsupported engine: {self.engine}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Statistics
            stats = {
                "source_file": markdown_path,
                "output_file": output_path,
                "engine": self.engine,
                "duration_seconds": duration,
                "page_size": page_size,
                "margin": margin,
                "font_size": font_size,
                "conversion_time": end_time.isoformat(),
                **result
            }
            
            logger.info(f"Markdown conversion completed: {markdown_path} -> {output_path}")
            return {
                "success": True,
                "message": "Markdown converted to PDF successfully",
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Markdown conversion failed: {str(e)}")
            return {
                "success": False,
                "message": f"Markdown conversion failed: {str(e)}",
                "error": str(e)
            }
    
    async def _convert_with_weasyprint(
        self,
        markdown_content: str,
        output_path: str,
        page_size: str,
        margin: str,
        font_size: int,
        base_url: str
    ) -> Dict[str, Any]:
        """Convert using WeasyPrint"""
        
        # Convert Markdown to HTML
        md = markdown.Markdown(
            extensions=['tables', 'codehilite', 'toc', 'fenced_code']
        )
        html_content = md.convert(markdown_content)
        
        # Create complete HTML document
        css_style = self._generate_css(page_size, margin, font_size)
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>{css_style}</style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Convert using WeasyPrint
        base_dir = Path(base_url).parent if base_url else None
        html = weasyprint.HTML(string=full_html, base_url=str(base_dir) if base_dir else None)
        
        # Generate PDF
        pdf_bytes = html.write_pdf()
        
        # Write to file
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Get page count
        document = html.render()
        page_count = len(document.pages)
        
        return {
            "output_size": len(pdf_bytes),
            "page_count": page_count,
            "html_size": len(full_html)
        }
    
    def _generate_css(self, page_size: str, margin: str, font_size: int) -> str:
        """Generate CSS styles"""
        return f"""
        @page {{
            size: {page_size};
            margin: {margin};
        }}
        body {{
            font-family: 'Arial', 'Microsoft YaHei', sans-serif;
            font-size: {font_size}pt;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: bold;
        }}
        h1 {{
            font-size: {font_size + 8}pt;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 0.3em;
        }}
        h2 {{
            font-size: {font_size + 6}pt;
            border-bottom: 1px solid #ddd;
            padding-bottom: 0.2em;
        }}
        h3 {{
            font-size: {font_size + 4}pt;
        }}
        p {{
            margin-bottom: 1em;
            text-align: justify;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: {font_size - 1}pt;
        }}
        pre {{
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 1em 0;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
            border-radius: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            font-size: {font_size - 1}pt;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            margin: 1em 0;
            padding-left: 1em;
            font-style: italic;
            color: #666;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
        }}
        ul, ol {{
            margin: 1em 0;
            padding-left: 2em;
        }}
        li {{
            margin-bottom: 0.5em;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 2em 0;
        }}
        """
    
    def _generate_enhanced_css_for_xhtml2pdf(self, page_size: str, margin: str, font_size: int) -> str:
        """Generate enhanced CSS specifically optimized for xhtml2pdf rendering"""
        return f"""
        /* Enhanced CSS for xhtml2pdf - optimized for PDF output */
        @page {{
            size: {page_size};
            margin: {margin};
            margin-top: 2cm;
            margin-bottom: 2cm;
        }}
        
        .container {{
            max-width: 100%;
            margin: 0 auto;
            font-family: "DejaVu Sans", "Liberation Sans", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: {font_size}pt;
        }}
        
        /* Typography - optimized for PDF */
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            font-weight: bold;
            margin-top: 1.5em;
            margin-bottom: 0.75em;
            page-break-after: avoid;
            line-height: 1.2;
        }}
        
        h1 {{
            font-size: {font_size + 8}pt;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 0.3em;
            margin-bottom: 1em;
        }}
        
        h2 {{
            font-size: {font_size + 6}pt;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 0.2em;
        }}
        
        h3 {{
            font-size: {font_size + 4}pt;
            color: #34495e;
        }}
        
        h4 {{
            font-size: {font_size + 2}pt;
            color: #34495e;
        }}
        
        h5, h6 {{
            font-size: {font_size + 1}pt;
            color: #7f8c8d;
        }}
        
        /* Paragraphs and text */
        p {{
            margin: 0 0 1em 0;
            text-align: justify;
            orphans: 3;
            widows: 3;
        }}
        
        strong, b {{
            font-weight: bold;
            color: #2c3e50;
        }}
        
        em, i {{
            font-style: italic;
            color: #34495e;
        }}
        
        /* Code - simplified for xhtml2pdf */
        code {{
            background-color: #f8f9fa;
            padding: 2px 4px;
            font-family: "DejaVu Sans Mono", "Liberation Mono", "Courier New", monospace;
            font-size: {font_size - 1}pt;
            color: #e74c3c;
            border: 1px solid #e1e8ed;
        }}
        
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #d1d5da;
            padding: 12pt;
            margin: 1em 0;
            page-break-inside: avoid;
            font-family: "DejaVu Sans Mono", "Liberation Mono", "Courier New", monospace;
            font-size: {font_size - 1}pt;
            line-height: 1.4;
            overflow: visible;
            white-space: pre-wrap;
        }}
        
        pre code {{
            background: none;
            padding: 0;
            border: none;
            color: #333;
        }}
        
        /* Code highlighting - simplified for xhtml2pdf */
        .highlight {{
            background-color: #f8f9fa;
            border: 1px solid #d1d5da;
            padding: 12pt;
            margin: 1em 0;
            page-break-inside: avoid;
        }}
        
        /* Tables - optimized for xhtml2pdf */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1.5em 0;
            font-size: {font_size - 1}pt;
            page-break-inside: avoid;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8pt 10pt;
            text-align: left;
            vertical-align: top;
        }}
        
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        tbody tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        /* Lists */
        ul, ol {{
            margin: 1em 0;
            padding-left: 1.5em;
        }}
        
        li {{
            margin-bottom: 0.5em;
        }}
        
        ul ul, ol ol {{
            margin: 0.5em 0;
        }}
        
        /* Blockquotes */
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 1.5em 0;
            padding: 0.5em 1em;
            background-color: #f8f9fa;
            color: #555;
            font-style: italic;
            page-break-inside: avoid;
        }}
        
        blockquote p {{
            margin: 0 0 0.5em 0;
        }}
        
        /* Horizontal rules */
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 2em 0;
            height: 0;
        }}
        
        /* Links - PDF friendly */
        a {{
            color: #3498db;
            text-decoration: underline;
        }}
        
        /* Images */
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
        }}
        
        /* Special elements */
        .admonition {{
            border: 1px solid #ddd;
            border-left: 4px solid #3498db;
            padding: 1em;
            margin: 1.5em 0;
            background-color: #f8f9fa;
            page-break-inside: avoid;
        }}
        
        .admonition-title {{
            font-weight: bold;
            margin-bottom: 0.5em;
            color: #2c3e50;
        }}
        
        /* Page breaks */
        .page-break {{
            page-break-before: always;
        }}
        
        .no-break {{
            page-break-inside: avoid;
        }}
        
        /* Ensure proper spacing */
        .container > *:first-child {{
            margin-top: 0;
        }}
        
        .container > *:last-child {{
            margin-bottom: 0;
        }}
        """
    
    async def _convert_with_xhtml2pdf(
        self,
        markdown_content: str,
        output_path: str,
        page_size: str,
        margin: str,
        font_size: int
    ) -> Dict[str, Any]:
        """Convert using xhtml2pdf (pure Python, good quality) with enhanced HTML pipeline and Unicode support"""
        
        # Use shared HTML conversion method
        html_content, extensions = self._convert_markdown_to_html(markdown_content)
        
        # Enhanced CSS with Unicode font support
        enhanced_css = self._generate_enhanced_css_for_xhtml2pdf(page_size, margin, font_size)
        
        # Create complete HTML document with better structure and language support
        full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Converted Document</title>
    <style>{enhanced_css}</style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>"""
        
        # Configure xhtml2pdf with Unicode font support
        unicode_fonts = self._get_unicode_fonts()
        
        # Update CSS in HTML to include proper font stack
        if unicode_fonts:
            enhanced_css = self._generate_enhanced_css_for_xhtml2pdf_with_unicode(
                page_size, margin, font_size, unicode_fonts
            )
            # Replace CSS in HTML
            full_html = full_html.replace(
                f"<style>{self._generate_enhanced_css_for_xhtml2pdf(page_size, margin, font_size)}</style>",
                f"<style>{enhanced_css}</style>"
            )
        
        # Generate PDF using xhtml2pdf
        with open(output_path, "wb") as result_file:
            pisa_status = pisa.CreatePDF(
                full_html, 
                dest=result_file,
                encoding='utf-8'
            )
        
        if pisa_status.err:
            logger.warning(f"xhtml2pdf conversion completed with {pisa_status.err} warnings")
        
        # Get file info
        file_size = Path(output_path).stat().st_size
        
        return {
            "output_size": file_size,
            "page_count": 1,  # xhtml2pdf doesn't provide easy page count
            "html_size": len(full_html),
            "extensions_used": extensions,
            "warnings": pisa_status.err if pisa_status.err else 0,
            "unicode_fonts": len(unicode_fonts)
        }
    
    async def _convert_with_reportlab(
        self,
        markdown_content: str,
        output_path: str,
        page_size: str,
        margin: str,
        font_size: int
    ) -> Dict[str, Any]:
        """Convert using ReportLab with enhanced Unicode support"""
        
        # Import additional ReportLab modules for Unicode
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.pdfbase.pdfmetrics import registerFontFamily
        except ImportError:
            logger.warning("ReportLab font modules not available")
        
        # Register Unicode fonts if available
        unicode_fonts = self._get_unicode_fonts()
        font_registered = False
        
        if unicode_fonts.get("chinese"):
            try:
                # Register the Chinese font
                font_path = unicode_fonts["chinese"]
                
                # Handle TTC (TrueType Collection) files differently
                if font_path.lower().endswith('.ttc'):
                    # For TTC files, try to use index 0 (first font in collection)
                    try:
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path, subfontIndex=0))
                        font_registered = True
                        logger.info(f"Registered Chinese font from TTC: {font_path} (index 0)")
                    except:
                        # If subfontIndex fails, try without it
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        font_registered = True
                        logger.info(f"Registered Chinese font: {font_path}")
                else:
                    # Regular TTF file
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    font_registered = True
                    logger.info(f"Registered Chinese font: {font_path}")
            except Exception as e:
                logger.warning(f"Failed to register Chinese font: {e}")
                # Try fallback font if available
                if unicode_fonts.get("fallback"):
                    try:
                        fallback_path = unicode_fonts["fallback"]
                        pdfmetrics.registerFont(TTFont('ChineseFont', fallback_path))
                        font_registered = True
                        logger.info(f"Registered fallback font: {fallback_path}")
                    except Exception as e2:
                        logger.warning(f"Failed to register fallback font: {e2}")
        
        # Convert page size
        page_sizes = {
            "A4": A4,
            "A3": A3,
            "Letter": letter,
            "Legal": legal
        }
        
        page_size_tuple = page_sizes.get(page_size, A4)
        
        # Parse margin
        margin_value = self._parse_margin(margin)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=page_size_tuple,
            leftMargin=margin_value,
            rightMargin=margin_value,
            topMargin=margin_value,
            bottomMargin=margin_value
        )
        
        # Enhanced styles with Unicode font support
        styles = getSampleStyleSheet()
        
        # Use registered font if available
        base_font = 'ChineseFont' if font_registered else 'Helvetica'
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=font_size + 6,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName=base_font
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=font_size + 2,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkred,
            fontName=base_font
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=font_size,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName=base_font
        )
        
        code_style = ParagraphStyle(
            'Code',
            parent=styles['Normal'],
            fontSize=font_size - 1,
            fontName='Courier',
            backgroundColor=colors.lightgrey,
            borderPadding=10,
            spaceAfter=12
        )
        
        elements = []
        
        # Parse and format content
        lines = markdown_content.split('\n')
        current_code_block = []
        in_code_block = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Handle code blocks
            if line.startswith('```'):
                if in_code_block:
                    # End code block
                    if current_code_block:
                        code_text = '\n'.join(current_code_block)
                        elements.append(Paragraph(code_text, code_style))
                        current_code_block = []
                    in_code_block = False
                else:
                    # Start code block
                    in_code_block = True
                continue
            
            if in_code_block:
                current_code_block.append(line)
                continue
            
            # Handle headings
            if line.startswith('# '):
                elements.append(Paragraph(line[2:], title_style))
            elif line.startswith('## '):
                elements.append(Paragraph(line[3:], heading_style))
            elif line.startswith('### '):
                elements.append(Paragraph(line[4:], heading_style))
            # Handle lists
            elif line.startswith('- ') or line.startswith('* '):
                elements.append(Paragraph(f"• {line[2:]}", normal_style))
            elif re.match(r'^\d+\. ', line):
                elements.append(Paragraph(line, normal_style))
            # Handle table rows (simplified)
            elif '|' in line and not line.startswith('|---'):
                # Simple table handling
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if cells:
                    elements.append(Paragraph(' | '.join(cells), normal_style))
            # Regular paragraphs
            elif line:
                # Clean up markdown formatting for better display
                # Handle bold+italic first (must close tags in correct order)
                clean_line = re.sub(r'\*\*\*(.*?)\*\*\*', r'<b><i>\1</i></b>', line)  # Bold+Italic
                clean_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_line)  # Bold
                clean_line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', clean_line)  # Italic
                clean_line = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', clean_line)  # Inline code
                elements.append(Paragraph(clean_line, normal_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get file size
        file_size = Path(output_path).stat().st_size
        
        return {
            "output_size": file_size,
            "page_count": max(1, len(elements) // 20),  # Estimate page count
            "elements_count": len(elements)
        }
    
    async def _convert_with_fpdf2(
        self,
        markdown_content: str,
        output_path: str,
        page_size: str,
        margin: str,
        font_size: int
    ) -> Dict[str, Any]:
        """Convert using fpdf2 (pure Python, basic quality)"""
        
        class PDF(FPDF):
            def header(self):
                self.set_font('helvetica', 'B', 15)
                self.cell(0, 10, 'PDF Document', 0, 1, 'C')
                self.ln(5)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('helvetica', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
        # Set page size
        page_format = page_size if page_size in ['A3', 'A4', 'Letter', 'Legal'] else 'A4'
        pdf = PDF(format=page_format)
        pdf.add_page()
        pdf.set_font('helvetica', '', font_size)
        
        # Simple text processing
        lines = markdown_content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('# '):
                pdf.set_font('helvetica', 'B', font_size + 4)
                pdf.cell(0, 10, line[2:], 0, 1)
                pdf.ln(5)
                pdf.set_font('helvetica', '', font_size)
            elif line.startswith('## '):
                pdf.set_font('helvetica', 'B', font_size + 2)
                pdf.cell(0, 8, line[3:], 0, 1)
                pdf.ln(3)
                pdf.set_font('helvetica', '', font_size)
            elif line.startswith('### '):
                pdf.set_font('helvetica', 'B', font_size + 1)
                pdf.cell(0, 8, line[4:], 0, 1)
                pdf.ln(2)
                pdf.set_font('helvetica', '', font_size)
            elif line and not line.startswith('```'):
                # Clean line of markdown
                clean_line = line.replace('**', '').replace('*', '').replace('`', '')
                try:
                    # Use multi_cell for better text wrapping
                    pdf.multi_cell(0, 6, clean_line)
                    pdf.ln(2)
                except:
                    # Handle unicode issues
                    safe_line = clean_line.encode('latin1', 'ignore').decode('latin1')
                    pdf.multi_cell(0, 6, safe_line)
                    pdf.ln(2)
        
        pdf.output(output_path)
        
        file_size = Path(output_path).stat().st_size
        
        return {
            "output_size": file_size,
            "page_count": pdf.page_no(),
            "text_processed": len(markdown_content)
        }
    
    def _parse_margin(self, margin: str) -> float:
        """Parse margin string for ReportLab"""
        if margin.endswith('cm'):
            return float(margin[:-2]) * cm
        elif margin.endswith('in'):
            return float(margin[:-2]) * inch
        elif margin.endswith('mm'):
            return float(margin[:-2]) * cm / 10
        else:
            # Default to centimeters
            try:
                return float(margin) * cm
            except ValueError:
                return 1 * cm
    
    def get_supported_engines(self) -> List[str]:
        """Get list of supported engines"""
        engines = []
        if HAS_XHTML2PDF:
            engines.append("xhtml2pdf")
        if HAS_WEASYPRINT:
            engines.append("weasyprint")
        if HAS_REPORTLAB:
            engines.append("reportlab")
        if HAS_FPDF2:
            engines.append("fpdf2")
        return engines
    
    def _convert_markdown_to_html(self, markdown_content: str) -> tuple[str, list]:
        """Convert markdown to HTML with enhanced extensions"""
        # Try to use advanced extensions
        try:
            from markdown.extensions import attr_list, admonition
            extensions = ['tables', 'codehilite', 'toc', 'fenced_code', 'attr_list', 'admonition', 'nl2br']
        except ImportError:
            # Fallback to basic extensions if advanced ones not available
            extensions = ['tables', 'codehilite', 'toc', 'fenced_code']
        
        md = markdown.Markdown(
            extensions=extensions,
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': False,  # Use simple highlighting for better PDF compatibility
                    'noclasses': True
                },
                'toc': {
                    'permalink': False  # Disable permalinks for PDF
                }
            }
        )
        
        html_content = md.convert(markdown_content)
        return html_content, extensions
    
    def _has_cjk_characters(self, text: str) -> bool:
        """Check if text contains CJK (Chinese, Japanese, Korean) characters"""
        import unicodedata
        
        for char in text:
            if any([
                # Chinese characters
                '\u4e00' <= char <= '\u9fff',  # CJK Unified Ideographs
                '\u3400' <= char <= '\u4dbf',  # CJK Extension A
                # Japanese characters
                '\u3040' <= char <= '\u309f',  # Hiragana
                '\u30a0' <= char <= '\u30ff',  # Katakana
                # Korean characters
                '\uac00' <= char <= '\ud7af',  # Hangul Syllables
                '\u1100' <= char <= '\u11ff',  # Hangul Jamo
            ]):
                return True
        return False
    
    def _get_unicode_fonts(self) -> dict:
        """Find available Unicode fonts on the system"""
        import platform
        import glob
        
        fonts = {}
        
        if platform.system() == "Darwin":  # macOS
            font_paths = [
                "/System/Library/Fonts/",
                "/Library/Fonts/",
                os.path.expanduser("~/Library/Fonts/")
            ]
            
            # Common Unicode fonts on macOS (prefer TTF over TTC for better ReportLab compatibility)
            font_candidates = {
                "chinese": [
                    "Arial Unicode.ttf",  # Prefer TTF format
                    "Arial Unicode MS.ttf",
                    "STHeiti Light.ttf",
                    "STHeiti Medium.ttc",
                    "Hiragino Sans GB.ttc", 
                    "PingFang SC.ttc",
                    "Songti.ttc"
                ],
                "fallback": [
                    "Arial.ttf",
                    "Helvetica.ttf",
                    "Times.ttf",
                    "Helvetica.ttc",
                    "Times.ttc"
                ]
            }
            
        elif platform.system() == "Windows":  # Windows
            font_paths = [
                "C:/Windows/Fonts/",
                os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts/")
            ]
            
            font_candidates = {
                "chinese": [
                    "arialuni.ttf",  # Arial Unicode MS - prefer TTF
                    "simhei.ttf",  # SimHei - TTF format
                    "simsun.ttf",  # SimSun TTF variant
                    "msyh.ttf",  # Microsoft YaHei TTF variant
                    "msyh.ttc",  # Microsoft YaHei TTC fallback
                    "simsun.ttc"  # SimSun TTC fallback
                ],
                "fallback": [
                    "arial.ttf",
                    "times.ttf",
                    "calibri.ttf"
                ]
            }
            
        else:  # Linux
            font_paths = [
                "/usr/share/fonts/",
                "/usr/local/share/fonts/",
                os.path.expanduser("~/.fonts/"),
                os.path.expanduser("~/.local/share/fonts/")
            ]
            
            font_candidates = {
                "chinese": [
                    "**/NotoSansCJK*.ttf",
                    "**/NotoSerifCJK*.ttf", 
                    "**/SourceHanSans*.ttf",
                    "**/WenQuanYi*.ttf",
                    "**/DroidSansFallback*.ttf"
                ],
                "fallback": [
                    "**/DejaVuSans.ttf",
                    "**/LiberationSans*.ttf",
                    "**/Arial*.ttf"
                ]
            }
        
        # Find fonts
        for font_type, candidates in font_candidates.items():
            for candidate in candidates:
                for font_path in font_paths:
                    if "**" in candidate:
                        # Use glob for recursive search
                        full_path = os.path.join(font_path, candidate)
                        matches = glob.glob(full_path, recursive=True)
                        if matches:
                            fonts[font_type] = matches[0]
                            break
                    else:
                        # Direct file check
                        full_path = os.path.join(font_path, candidate)
                        if os.path.exists(full_path):
                            fonts[font_type] = full_path
                            break
                if font_type in fonts:
                    break
        
        return fonts
    
    def _get_unicode_css_with_fonts(self, unicode_fonts: dict, page_size: str, margin: str, font_size: int) -> str:
        """Generate CSS with Unicode font registration for xhtml2pdf"""
        
        css = f"""
        @page {{
            size: {page_size};
            margin: {margin};
        }}
        """
        
        # Register fonts if available
        if unicode_fonts.get("chinese"):
            css += f"""
        @font-face {{
            font-family: "ChineseFont";
            src: url("{unicode_fonts['chinese']}");
        }}
        """
        
        if unicode_fonts.get("fallback"):
            css += f"""
        @font-face {{
            font-family: "FallbackFont";
            src: url("{unicode_fonts['fallback']}");
        }}
        """
        
        # Define font stacks with Unicode support
        chinese_font = '"ChineseFont"' if unicode_fonts.get("chinese") else ""
        fallback_font = '"FallbackFont"' if unicode_fonts.get("fallback") else ""
        
        font_stack = ", ".join(filter(None, [
            chinese_font,
            fallback_font,
            '"STHeiti"',  # macOS fallback
            '"Microsoft YaHei"',  # Windows fallback
            '"Noto Sans CJK SC"',  # Linux fallback
            'sans-serif'
        ]))
        
        css += f"""
        body, .container {{
            font-family: {font_stack};
            font-size: {font_size}pt;
            line-height: 1.6;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            font-family: {font_stack};
        }}
        
        code, pre {{
            font-family: "Courier New", monospace;
        }}
        """
        
        return css
    
    def _generate_enhanced_css_for_xhtml2pdf_with_unicode(self, page_size: str, margin: str, font_size: int, unicode_fonts: dict) -> str:
        """Generate enhanced CSS with Unicode font support"""
        
        # Build font stack with available fonts
        font_stack_parts = []
        
        # Add found fonts
        if unicode_fonts.get("chinese"):
            font_stack_parts.append(f'"{os.path.basename(unicode_fonts["chinese"]).split(".")[0]}"')
        if unicode_fonts.get("fallback"):
            font_stack_parts.append(f'"{os.path.basename(unicode_fonts["fallback"]).split(".")[0]}"')
        
        # Add system fallbacks
        font_stack_parts.extend([
            '"STHeiti"',  # macOS Chinese
            '"Microsoft YaHei"',  # Windows Chinese  
            '"Noto Sans CJK SC"',  # Linux Chinese
            '"Arial Unicode MS"',  # Unicode fallback
            'sans-serif'  # Final fallback
        ])
        
        font_stack = ", ".join(font_stack_parts)
        
        return f"""
        /* Enhanced CSS for xhtml2pdf with Unicode support */
        @page {{
            size: {page_size};
            margin: {margin};
            margin-top: 2cm;
            margin-bottom: 2cm;
        }}
        
        .container {{
            max-width: 100%;
            margin: 0 auto;
            font-family: {font_stack};
            line-height: 1.6;
            color: #333;
            font-size: {font_size}pt;
        }}
        
        /* Typography with Unicode support */
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            font-weight: bold;
            margin-top: 1.5em;
            margin-bottom: 0.75em;
            page-break-after: avoid;
            line-height: 1.2;
            font-family: {font_stack};
        }}
        
        h1 {{
            font-size: {font_size + 8}pt;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 0.3em;
            margin-bottom: 1em;
        }}
        
        h2 {{
            font-size: {font_size + 6}pt;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 0.2em;
        }}
        
        h3 {{
            font-size: {font_size + 4}pt;
            color: #34495e;
        }}
        
        h4 {{
            font-size: {font_size + 2}pt;
            color: #34495e;
        }}
        
        h5, h6 {{
            font-size: {font_size + 1}pt;
            color: #7f8c8d;
        }}
        
        /* Text with Unicode support */
        p, li, td, th {{
            font-family: {font_stack};
            margin: 0 0 1em 0;
            text-align: justify;
            orphans: 3;
            widows: 3;
        }}
        
        strong, b {{
            font-weight: bold;
            color: #2c3e50;
        }}
        
        em, i {{
            font-style: italic;
            color: #34495e;
        }}
        
        /* Code with fallback fonts */
        code {{
            background-color: #f8f9fa;
            padding: 2px 4px;
            font-family: "Courier New", "Consolas", monospace;
            font-size: {font_size - 1}pt;
            color: #e74c3c;
            border: 1px solid #e1e8ed;
        }}
        
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #d1d5da;
            padding: 12pt;
            margin: 1em 0;
            page-break-inside: avoid;
            font-family: "Courier New", "Consolas", monospace;
            font-size: {font_size - 1}pt;
            line-height: 1.4;
            overflow: visible;
            white-space: pre-wrap;
        }}
        
        pre code {{
            background: none;
            padding: 0;
            border: none;
            color: #333;
        }}
        
        /* Tables with Unicode support */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1.5em 0;
            font-size: {font_size - 1}pt;
            page-break-inside: avoid;
            font-family: {font_stack};
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8pt 10pt;
            text-align: left;
            vertical-align: top;
        }}
        
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        tbody tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        /* Lists */
        ul, ol {{
            margin: 1em 0;
            padding-left: 1.5em;
        }}
        
        li {{
            margin-bottom: 0.5em;
        }}
        
        /* Blockquotes */
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 1.5em 0;
            padding: 0.5em 1em;
            background-color: #f8f9fa;
            color: #555;
            font-style: italic;
            page-break-inside: avoid;
            font-family: {font_stack};
        }}
        
        blockquote p {{
            margin: 0 0 0.5em 0;
        }}
        
        /* Links */
        a {{
            color: #3498db;
            text-decoration: underline;
        }}
        
        /* Images */
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
        }}
        
        /* Horizontal rules */
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 2em 0;
            height: 0;
        }}
        
        /* Ensure proper spacing */
        .container > *:first-child {{
            margin-top: 0;
        }}
        
        .container > *:last-child {{
            margin-bottom: 0;
        }}
        """
    
    def get_supported_page_sizes(self) -> List[str]:
        """Get supported page sizes"""
        return ["A4", "A3", "Letter", "Legal"]
    
    async def validate_markdown(self, markdown_path: str) -> Dict[str, Any]:
        """Validate Markdown file"""
        try:
            path = Path(markdown_path)
            
            if not path.exists():
                return {"valid": False, "error": "File does not exist"}
            
            if not path.is_file():
                return {"valid": False, "error": "Not a file"}
            
            if path.suffix.lower() not in ['.md', '.markdown']:
                return {"valid": False, "error": "Not a Markdown file"}
            
            # Read and validate content
            try:
                with open(markdown_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Statistics
                line_count = len(content.splitlines())
                word_count = len(content.split())
                
                # Check Markdown syntax
                md = markdown.Markdown()
                html = md.convert(content)
                
                return {
                    "valid": True,
                    "line_count": line_count,
                    "word_count": word_count,
                    "character_count": len(content),
                    "file_size": path.stat().st_size,
                    "has_tables": "| " in content,
                    "has_code_blocks": "```" in content,
                    "has_images": "![" in content,
                    "engine": self.engine
                }
                    
            except UnicodeDecodeError:
                return {"valid": False, "error": "File encoding error, please use UTF-8 encoding"}
                
        except Exception as e:
            return {"valid": False, "error": f"Validation failed: {str(e)}"}