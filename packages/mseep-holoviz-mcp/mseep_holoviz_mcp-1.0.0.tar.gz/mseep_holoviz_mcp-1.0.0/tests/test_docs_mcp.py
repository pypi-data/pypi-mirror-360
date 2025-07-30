"""
Simple tests for the documentation MCP server.

Tests just the docs server functionality without the composed server.
"""

import pytest
from fastmcp import Client

from holoviz_mcp.docs_mcp.server import mcp


@pytest.mark.asyncio
async def test_best_practices_resource():
    """Test the best-practices resource."""
    client = Client(mcp)
    async with client:
        result = await client.call_tool("get_best_practices", {"package": "panel"})
        assert result.data


@pytest.mark.skip(reason="This test is very slow and not needed for CI")
@pytest.mark.asyncio
async def test_update_index():
    """Test the best-practices resource."""
    client = Client(mcp)
    async with client:
        result = await client.call_tool("update_index")
        assert result.data


@pytest.mark.asyncio
async def test_pages_semantic_search():
    """Test the pages tool with semantic search queries."""
    client = Client(mcp)
    async with client:
        # Test basic semantic search across all packages
        result = await client.call_tool("search", {"query": "dashboard layout best practices"})
        assert result.data
        assert isinstance(result.data, list)
        # Should return up to 5 results by default
        assert len(result.data) <= 5

        # Verify each result is a proper Page object
        for page in result.data:
            assert "title" in page
            assert "url" in page
            assert "package" in page
            assert "path" in page
            # Should include content by default
            assert "content" in page


@pytest.mark.asyncio
async def test_pages_with_package_filter():
    """Test the pages tool with package filtering."""
    client = Client(mcp)
    async with client:
        # Test search with specific package filter
        result = await client.call_tool("search", {"query": "interactive plotting with widgets", "package": "hvplot"})
        assert result.data
        assert isinstance(result.data, list)

        # All results should be from hvplot package
        for page in result.data:
            assert page["package"] == "hvplot"


@pytest.mark.asyncio
async def test_pages_with_custom_max_results():
    """Test the pages tool with custom max_results parameter."""
    client = Client(mcp)
    async with client:
        # Test search with limited results
        result = await client.call_tool("search", {"query": "custom widgets", "package": "panel", "max_results": 3})
        assert result.data
        assert isinstance(result.data, list)
        # Should return at most 3 results
        assert len(result.data) <= 3

        # All results should be from panel package
        for page in result.data:
            assert page["package"] == "panel"


@pytest.mark.asyncio
async def test_pages_without_content():
    """Test the pages tool with content=False for metadata only."""
    client = Client(mcp)
    async with client:
        # Test search without content for faster response
        result = await client.call_tool("search", {"query": "parameter handling", "content": False})
        assert result.data
        assert isinstance(result.data, list)

        # Verify each result has metadata but no content
        for page in result.data:
            assert "title" in page
            assert "url" in page
            assert "package" in page
            assert "path" in page
            # Should not include content when content=False
            assert page.get("content") is None


@pytest.mark.asyncio
async def test_pages_material_ui_specific():
    """Test the pages tool with Material UI specific query."""
    client = Client(mcp)
    async with client:
        # Test search for Material UI styling
        result = await client.call_tool("search", {"query": "How to style Material UI components?", "package": "panel_material_ui"})
        assert result.data
        assert isinstance(result.data, list)

        # Results should be from panel_material_ui package
        for page in result.data:
            assert page["package"] == "panel_material_ui"


@pytest.mark.asyncio
async def test_pages_empty_query():
    """Test the pages tool with edge cases."""
    client = Client(mcp)
    async with client:
        # Test with empty query
        result = await client.call_tool("search", {"query": ""})
        # Should handle gracefully and return empty or minimal results
        assert isinstance(result.data, list)


@pytest.mark.asyncio
async def test_pages_invalid_package():
    """Test the pages tool with invalid package name."""
    client = Client(mcp)
    async with client:
        # Test with non-existent package
        result = await client.call_tool("search", {"query": "test query", "package": "nonexistent_package"})
        # Should handle gracefully and return empty results
        assert isinstance(result.data, list)
        assert len(result.data) == 0


@pytest.mark.asyncio
async def test_page():
    """Test the page tool with package filtering."""
    client = Client(mcp)
    async with client:
        # Test search with specific package filter
        result = await client.call_tool("get_page", {"path": "doc/index.md", "package": "hvplot"})
        assert result.data
        assert result.data.title == "hvPlot"
