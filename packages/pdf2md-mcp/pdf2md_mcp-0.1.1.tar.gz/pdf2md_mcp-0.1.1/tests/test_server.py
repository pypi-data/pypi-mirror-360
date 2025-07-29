"""
Tests for the PDF to Markdown conversion functionality.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from pdf2md_mcp.server import PDFToMarkdownConverter, convert_pdf_to_markdown


class TestPDFToMarkdownConverter:
    """Test the PDFToMarkdownConverter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.converter = PDFToMarkdownConverter()
    
    def test_get_output_path_with_output_dir(self):
        """Test output path generation with specified output directory."""
        input_path = "/path/to/document.pdf"
        output_dir = "/output/directory"
        
        result = self.converter.get_output_path(input_path, output_dir)
        expected = str(Path(output_dir) / "document.md")
        
        assert result == expected
    
    def test_get_output_path_without_output_dir(self):
        """Test output path generation without specified output directory."""
        input_path = "/path/to/document.pdf"
        
        result = self.converter.get_output_path(input_path)
        expected = str(Path("/path/to") / "document.md")
        
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_check_existing_content_no_file(self):
        """Test checking existing content when file doesn't exist."""
        non_existent_path = "/path/that/does/not/exist.md"
        
        result = await self.converter.check_existing_content(non_existent_path)
        
        assert result == 0
    
    @pytest.mark.asyncio
    async def test_check_existing_content_with_pages(self):
        """Test checking existing content with page markers."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Document
            
## Page 1
Content from page 1

<!-- Page 2 -->
## Page 2
Content from page 2

## Page 5
Content from page 5
""")
            temp_path = f.name
        
        try:
            result = await self.converter.check_existing_content(temp_path)
            assert result == 5  # Should return the highest page number
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_extract_pdf_content_with_sampling_no_context(self):
        """Test PDF content extraction without sampling context (fallback mode)."""
        pdf_path = "/path/to/test.pdf"
        start_page = 3
        
        content, pages_processed = await self.converter.extract_pdf_content_with_sampling(
            pdf_path, start_page, ctx=None
        )
        
        assert isinstance(content, str)
        assert isinstance(pages_processed, int)
        assert "PDF Content Extracted" in content
        assert f"Starting from page: {start_page}" in content
        assert pages_processed == 1  # Fallback mode returns 1 page
    
    @pytest.mark.asyncio
    async def test_extract_pdf_content_with_sampling_with_context(self):
        """Test PDF content extraction with mocked sampling context."""
        pdf_path = "/path/to/test.pdf"
        start_page = 1
        
        # Mock the sampling context
        mock_ctx = AsyncMock()
        mock_ctx.sample.return_value = """# Extracted Content

<!-- Page 1 -->
## Page 1
Sample content from page 1

<!-- Page 2 -->
## Page 2
Sample content from page 2"""
        
        content, pages_processed = await self.converter.extract_pdf_content_with_sampling(
            pdf_path, start_page, ctx=mock_ctx
        )
        
        assert isinstance(content, str)
        assert isinstance(pages_processed, int)
        assert "Extracted Content" in content
        assert pages_processed == 2  # Should detect 2 pages from markers
        mock_ctx.sample.assert_called_once()


class TestConvertPDFToMarkdownTool:
    """Test the convert_pdf_to_markdown MCP tool."""
    
    @pytest.mark.asyncio
    async def test_convert_nonexistent_local_file(self):
        """Test conversion of non-existent local file."""
        result = await convert_pdf_to_markdown("/path/that/does/not/exist.pdf")
        
        assert "error" in result
        assert "File not found" in result["error"]
        assert result["output_file"] is None
        assert result["pages_processed"] == 0
    
    @pytest.mark.asyncio
    async def test_convert_with_mock_file_and_sampling(self):
        """Test conversion with a mocked local file and sampling context."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
            pdf_path = pdf_file.name
        
        try:
            # Mock the content extraction with sampling
            mock_ctx = AsyncMock()
            mock_ctx.sample.return_value = "# Mocked Content\n\n## Page 1\nTest content"
            
            with patch.object(PDFToMarkdownConverter, 'extract_pdf_content_with_sampling') as mock_extract:
                mock_extract.return_value = ("# Mocked Content\n\n## Page 1\nTest content", 1)
                
                result = await convert_pdf_to_markdown(pdf_path, ctx=mock_ctx)
                
                assert "error" not in result
                assert result["output_file"] is not None
                assert result["pages_processed"] == 1
                assert result["start_page"] == 1
                assert "Started PDF conversion" in result["summary"]
                assert result["sampling_used"] is True
                
                # Check that output file was created
                assert os.path.exists(result["output_file"])
                
                # Clean up output file
                if os.path.exists(result["output_file"]):
                    os.unlink(result["output_file"])
        finally:
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
    
    @pytest.mark.asyncio
    async def test_convert_url_with_mock_download(self):
        """Test conversion of URL with mocked download."""
        test_url = "https://example.com/test.pdf"
        
        with patch.object(PDFToMarkdownConverter, 'download_pdf') as mock_download, \
             patch.object(PDFToMarkdownConverter, 'extract_pdf_content_with_sampling') as mock_extract:
            
            # Setup mocks
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                mock_download.return_value = temp_pdf.name
                mock_extract.return_value = ("# URL Content\n\n## Page 1\nURL test content", 1)
                
                try:
                    result = await convert_pdf_to_markdown(test_url)
                    
                    assert "error" not in result
                    assert result["output_file"] is not None
                    assert result["pages_processed"] == 1
                    assert "URL:" in result["source"]
                    
                    # Clean up
                    if os.path.exists(result["output_file"]):
                        os.unlink(result["output_file"])
                finally:
                    if os.path.exists(temp_pdf.name):
                        os.unlink(temp_pdf.name)


if __name__ == "__main__":
    pytest.main([__file__])
