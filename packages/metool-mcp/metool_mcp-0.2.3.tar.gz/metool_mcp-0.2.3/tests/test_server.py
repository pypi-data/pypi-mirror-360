"""Tests for metool MCP server."""

import pytest
from pathlib import Path
import tempfile
import json


@pytest.mark.asyncio
async def test_add_repo_entry():
    """Test adding repository entries."""
    # Import the raw function for testing
    from metool_mcp.server import add_repo_entry
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Get the wrapped function
        add_repo_fn = add_repo_entry.fn
        
        # Test adding first entry
        result = await add_repo_fn(
            directory=tmpdir,
            repo="mbailey/test-repo",
            target_name="test"
        )
        assert result["status"] == "added"
        
        # Verify file contents
        repo_file = Path(tmpdir) / ".repos.txt"
        assert repo_file.exists()
        content = repo_file.read_text()
        assert "mbailey/test-repo test" in content
        
        # Test duplicate detection
        result = await add_repo_fn(
            directory=tmpdir,
            repo="mbailey/test-repo",
            target_name="test"
        )
        assert result["status"] == "exists"


@pytest.mark.asyncio
async def test_list_repos():
    """Test listing repositories."""
    from metool_mcp.server import list_repos
    list_repos_fn = list_repos.fn
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test empty directory
        result = await list_repos_fn(tmpdir)
        assert result["status"] == "not_found"
        assert result["repos"] == []
        
        # Create repos file
        repo_file = Path(tmpdir) / ".repos.txt"
        repo_file.write_text("""# Test repos
mbailey/repo1
mbailey/repo2 custom-name
# Comment
_work:company/repo3

mbailey/repo4
""")
        
        # Test listing
        result = await list_repos_fn(tmpdir)
        assert result["status"] == "success"
        assert len(result["repos"]) == 4
        assert "mbailey/repo1" in result["repos"]
        assert "mbailey/repo2 custom-name" in result["repos"]
        assert "_work:company/repo3" in result["repos"]
        assert "mbailey/repo4" in result["repos"]


@pytest.mark.asyncio
async def test_prompts():
    """Test prompt generation."""
    from metool_mcp.server import conventions_add, manage_repos
    
    # Test conventions_add prompt
    prompt_text = await conventions_add.fn()
    assert "conventions repository" in prompt_text
    assert "/metool:conventions-add" in prompt_text
    
    # Test manage_repos prompt
    prompt_text = await manage_repos.fn()
    assert "manifest files" in prompt_text
    assert "mt sync" in prompt_text


@pytest.mark.asyncio 
async def test_add_repo_without_target():
    """Test adding repo without explicit target name."""
    from metool_mcp.server import add_repo_entry
    add_repo_fn = add_repo_entry.fn
    
    with tempfile.TemporaryDirectory() as tmpdir:
        result = await add_repo_fn(
            directory=tmpdir,
            repo="owner/simple-repo"
        )
        assert result["status"] == "added"
        
        content = Path(tmpdir, ".repos.txt").read_text()
        assert "owner/simple-repo\n" in content