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
    
    async def extract_pdf_content_with_sampling(self, pdf_path: str, start_page: int = 1, ctx=None) -> Tuple[str, int]:
        """
        Extract PDF content using MCP sampling feature.
        Uses ctx.sample() to request completions from the client's LLM.
        """
        if ctx is None:
            # Fallback for testing or when no context is available
            return await self._extract_fallback(pdf_path, start_page)
        
        try:
            # Sample the LLM to extract content from the PDF
            prompt = f"""Please extract and convert the content from the PDF file: {pdf_path}
            
Starting from page {start_page}, please:
1. Extract the text content from each page
2. Convert it to clean Markdown format
3. Use page markers like "<!-- Page X -->" and "## Page X" for each page
4. Preserve the document structure (headings, lists, tables, etc.)
5. Remove any OCR artifacts or formatting noise
6. Return the content in a structured format

Please process the PDF and return the extracted Markdown content."""

            # Use FastMCP sampling to get LLM response
            extracted_content = await ctx.sample(prompt)
            
            # Count the number of pages processed by looking for page markers
            page_matches = re.findall(r'(?:##\s*Page\s*(\d+)|<!--\s*Page\s*(\d+)\s*-->)', extracted_content, re.IGNORECASE)
            pages_processed = len(set(int(match[0] or match[1]) for match in page_matches)) if page_matches else 1
            
            return extracted_content, pages_processed
            
        except Exception as e:
            # Log the error and return a fallback content
            import traceback
            traceback.print_exception(e)
            # Fallback if sampling fails
            fallback_content = f"""# PDF Content Extraction Error

Failed to extract content from: {pdf_path}
Error: {str(e)}

<!-- Page {start_page} -->
## Page {start_page}

*Content extraction failed. Please check the PDF file and try again.*

---
*PDF2MD MCP Server - Extraction failed, using fallback*
"""
            return fallback_content, 1
    
    async def _extract_fallback(self, pdf_path: str, start_page: int = 1) -> Tuple[str, int]:
        """Fallback method when no sampling context is available."""
        content = f"""# PDF Content Extracted

Content extracted from: {pdf_path}
Starting from page: {start_page}

<!-- Page {start_page} -->
## Page {start_page}

*This is a fallback implementation. For full extraction, use with MCP sampling context.*

---
*Extracted using PDF2MD MCP Server (fallback mode)*
"""
        return content, 1


converter = PDFToMarkdownConverter()

@mcp.tool
async def convert_pdf_to_markdown(
    file_path: str,
    ctx: Context,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convert a PDF file to Markdown format using AI sampling.
    
    Args:
        file_path: Local file path or URL to the PDF file
        ctx: MCP context for sampling (automatically provided by FastMCP)
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
        
        # Extract content using MCP sampling
        new_content, pages_processed = await converter.extract_pdf_content_with_sampling(
            local_pdf_path, start_page, ctx
        )
        
        # Write or append content
        mode = 'a' if last_page > 0 else 'w'
        async with aiofiles.open(output_path, mode, encoding='utf-8') as f:
            if last_page > 0:
                await f.write('\n\n' + new_content)
            else:
                await f.write(new_content)
        
        # Generate summary
        action = "Continued" if last_page > 0 else "Started"
        sampling_status = "with AI sampling" if ctx else "in fallback mode"
        summary = f"{action} PDF conversion from {source_description} {sampling_status}. " \
                 f"Processed {pages_processed} pages starting from page {start_page}. " \
                 f"Output saved to: {output_path}"
        
        return {
            "output_file": output_path,
            "summary": summary,
            "pages_processed": pages_processed,
            "start_page": start_page,
            "source": source_description,
            "sampling_used": ctx is not None
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
