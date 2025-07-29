"""
Main MCP server implementation for PDF to Markdown conversion.
"""

import asyncio
import os
import re
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlparse

import aiofiles
import httpx
from fastmcp import FastMCP, Context
import pymupdf4llm

# Initialize the MCP server
mcp = FastMCP("PDF2MD MCP Server")


class PDFToMarkdownConverter:
    """Handles PDF to Markdown conversion using MCP sampling."""
    
    def __init__(self):
        self.session_cache: Dict[str, Any] = {}
    
    async def download_pdf(self, url: str, output_dir: str) -> str:
        """Download PDF from URL to local file."""
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path) or "downloaded.pdf"
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        local_path = os.path.join(output_dir, filename)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            async with aiofiles.open(local_path, 'wb') as f:
                await f.write(response.content)
        
        return local_path
    
    def get_output_path(self, input_path: str, output_dir: Optional[str] = None) -> str:
        """Generate output markdown file path."""
        input_path_obj = Path(input_path)
        base_name = input_path_obj.stem
        
        if output_dir:
            output_directory = Path(output_dir)
        else:
            output_directory = input_path_obj.parent
        
        output_directory.mkdir(parents=True, exist_ok=True)
        return str(output_directory / f"{base_name}.md")
    
    async def check_existing_content(self, output_path: str) -> int:
        """Check existing markdown content and determine last processed page."""
        if not os.path.exists(output_path):
            return 0
        
        try:
            async with aiofiles.open(output_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Look for page markers like "## Page X" or "<!-- Page X -->"
            page_matches = re.findall(r'(?:##\s*Page\s*(\d+)|<!--\s*Page\s*(\d+)\s*-->)', content, re.IGNORECASE)
            if page_matches:
                # Get the highest page number
                pages = [int(match[0] or match[1]) for match in page_matches]
                return max(pages)
            
            return 0
        except Exception:
            return 0
    
    async def extract_pdf_content(self, pdf_path: str, start_page: int = 1) -> Tuple[str, int]:
        """
        Extract PDF content using pymupdf4llm (Python package) instead of MCP sampling.
        """
        try:
            # Use pymupdf4llm to extract markdown from the PDF
            # Note: pages are 0-indexed in pymupdf4llm
            # If start_page > 1, extract only the remaining pages
            import asyncio
            loop = asyncio.get_event_loop()
            def extract_md():
                if start_page > 1:
                    # Extract only the remaining pages
                    total_pages = pymupdf4llm.get_page_count(pdf_path)
                    pages = list(range(start_page - 1, total_pages))
                    md = pymupdf4llm.to_markdown(pdf_path, pages=pages)
                else:
                    md = pymupdf4llm.to_markdown(pdf_path)
                return md
            extracted_content = await loop.run_in_executor(None, extract_md)

            # Count the number of pages processed by looking for page markers
            page_matches = re.findall(r'(?:##\s*Page\s*(\d+)|<!--\s*Page\s*(\d+)\s*-->)', extracted_content, re.IGNORECASE)
            if page_matches:
                pages_processed = len(set(int(match[0] or match[1]) for match in page_matches))
            else:
                # Fallback: count number of '## Page' headers or estimate from start_page
                pages_processed = extracted_content.count('## Page') or 1

            return extracted_content, pages_processed
        except Exception as e:
            import traceback
            traceback.print_exception(e)
            fallback_content = f"""# PDF Content Extraction Error\n\nFailed to extract content from: {pdf_path}\nError: {str(e)}\n\n<!-- Page {start_page} -->\n## Page {start_page}\n\n*Content extraction failed. Please check the PDF file and try again.*\n\n---\n*PDF2MD MCP Server - Extraction failed, using fallback*\n"""
            return fallback_content, 1


converter = PDFToMarkdownConverter()

@mcp.tool
async def convert_pdf_to_markdown(
    file_path: str,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convert a PDF file to Markdown format using AI sampling.
    
    Args:
        file_path: Local file path or URL to the PDF file
        output_dir: Optional output directory. Defaults to same directory as input file
                   (for local files) or current working directory (for URLs)
    Returns:
        Dictionary containing:
        - output_file: Path to the generated markdown file
        - summary: Summary of the conversion task
        - pages_processed: Number of pages processed
    """
    try:
        # Determine if input is URL or local path
        is_url = file_path.startswith(('http://', 'https://'))
        
        if is_url:
            # Download the PDF first
            download_dir = output_dir or os.getcwd()
            os.makedirs(download_dir, exist_ok=True)
            local_pdf_path = await converter.download_pdf(file_path, download_dir)
            source_description = f"URL: {file_path}"
        else:
            # Check if local file exists
            if not os.path.exists(file_path):
                return {
                    "error": f"File not found: {file_path}",
                    "output_file": None,
                    "summary": "Failed - file not found",
                    "pages_processed": 0
                }
            local_pdf_path = file_path
            source_description = f"Local file: {file_path}"
        
        # Generate output path
        output_path = converter.get_output_path(local_pdf_path, output_dir)
        
        # Check for existing content
        last_page = await converter.check_existing_content(output_path)
        start_page = last_page + 1 if last_page > 0 else 1
        
        # Extract content using pymupdf4llm
        extracted_content, pages_processed = await converter.extract_pdf_content(
            local_pdf_path, start_page
        )
        
        # Write or append content
        mode = 'a' if last_page > 0 else 'w'
        async with aiofiles.open(output_path, mode, encoding='utf-8') as f:
            if last_page > 0:
                await f.write('\n\n' + extracted_content)
            else:
                await f.write(extracted_content)
        
        # Generate summary
        action = "Continued" if last_page > 0 else "Started"
        summary = f"{action} PDF conversion from {source_description}. " \
                 f"Processed {pages_processed} pages starting from page {start_page}. " \
                 f"Output saved to: {output_path}"
        
        return {
            "output_file": output_path,
            "summary": summary,
            "pages_processed": pages_processed,
            "start_page": start_page,
            "source": source_description,
        }
        
    except Exception as e:
        return {
            "error": f"Conversion failed: {str(e)}",
            "output_file": None,
            "summary": f"Failed to convert PDF: {str(e)}",
            "pages_processed": 0
        }

def main():
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
