from fastmcp import Client
from server import mcp

async def main():
    # Connect via stdio to a local script
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        # result = await client.call_tool("convert_pdf_to_markdown", {"file_path": "C:\\Users\\ghuang\\projects\\GenAI\\pdf2md-mcp\\examples\\Goolge_whitepaper_Prompt_Engineering_v4.pdf", "output_dir": "C:\\Users\\ghuang\\projects\\GenAI\\pdf2md-mcp\\examples\\"})
        # print(f"Result: {result}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())