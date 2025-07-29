"""FastMCP server for metool."""

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, List

from fastmcp import FastMCP

mcp = FastMCP("metool-mcp")


@mcp.tool()
async def add_repo_entry(
    directory: str,
    repo: str,
    target_name: Optional[str] = None,
    file_name: str = ".repos.txt"
) -> Dict[str, any]:
    """
    Add a repository entry to repos.txt file.
    
    Args:
        directory: Directory containing the repos.txt file
        repo: Repository specification (e.g., "mbailey/conventions")
        target_name: Optional target directory name (defaults to repo basename)
        file_name: Name of the repos file (default: ".repos.txt")
    
    Returns:
        Dict with status and message
    """
    try:
        repo_file = Path(directory) / file_name
        
        # Ensure directory exists
        repo_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Build the entry line
        if target_name:
            entry = f"{repo} {target_name}"
        else:
            entry = repo
            
        # Check if entry already exists
        if repo_file.exists():
            content = repo_file.read_text()
            if entry in content or repo in content:
                return {
                    "status": "exists",
                    "message": f"Repository {repo} already exists in {file_name}"
                }
        
        # Append the entry
        with open(repo_file, 'a') as f:
            if repo_file.exists() and repo_file.stat().st_size > 0:
                f.write('\n')
            f.write(entry + '\n')
            
        return {
            "status": "added",
            "message": f"Added {entry} to {repo_file}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to add repo entry: {str(e)}"
        }


async def _install_or_update_metool_impl(
    install_dir: Optional[str] = None,
    update_bashrc: bool = True
) -> Dict[str, any]:
    """Implementation of install_or_update_metool."""
    try:
        # Default installation directory
        if not install_dir:
            install_dir = str(Path.home() / "metool")
        
        install_path = Path(install_dir)
        mt_script = install_path / "shell" / "mt"
        
        # Check if metool is already installed
        if mt_script.exists():
            # Update existing installation
            bash_cmd = f'cd "{install_path}" && git pull'
            result = await asyncio.create_subprocess_exec(
                'bash', '-c', bash_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": f"Failed to update metool: {stderr.decode('utf-8')}"
                }
            
            return {
                "status": "updated",
                "message": f"Updated metool at {install_path}",
                "path": str(install_path),
                "git_output": stdout.decode('utf-8')
            }
        else:
            # Fresh installation
            # Ensure parent directory exists
            install_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Clone metool repository
            git_cmd = f'git clone https://github.com/mbailey/metool.git "{install_path}"'
            result = await asyncio.create_subprocess_exec(
                'bash', '-c', git_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": f"Failed to clone metool: {stderr.decode('utf-8')}"
                }
            
            # Update .bashrc if requested
            bashrc_updated = False
            if update_bashrc:
                bashrc_path = Path.home() / ".bashrc"
                source_line = f'source "{install_path}/shell/mt"'
                
                # Check if already in .bashrc
                if bashrc_path.exists():
                    content = bashrc_path.read_text()
                    if source_line not in content:
                        # Add to .bashrc
                        with open(bashrc_path, 'a') as f:
                            f.write(f'\n# Added by metool MCP server\n')
                            f.write(f'{source_line}\n')
                        bashrc_updated = True
            
            # Run mt install to set up symlinks
            install_cmd = f'source "{install_path}/shell/mt" && mt install'
            result = await asyncio.create_subprocess_exec(
                'bash', '-c', install_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, 'MT_ROOT': str(install_path)}
            )
            stdout, stderr = await result.communicate()
            
            return {
                "status": "installed",
                "message": f"Installed metool at {install_path}",
                "path": str(install_path),
                "bashrc_updated": bashrc_updated,
                "install_output": stdout.decode('utf-8'),
                "next_steps": "Restart your shell or run: source ~/.bashrc" if bashrc_updated else "Source the mt script to use metool"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to install/update metool: {str(e)}"
        }


@mcp.tool()
async def install_or_update_metool(
    install_dir: Optional[str] = None,
    update_bashrc: bool = True
) -> Dict[str, any]:
    """
    Install or update metool on the system.
    
    Args:
        install_dir: Directory to install metool (defaults to ~/metool)
        update_bashrc: Whether to update .bashrc to source metool (default: True)
        
    Returns:
        Dict with status, action taken, and installation path
    """
    return await _install_or_update_metool_impl(install_dir, update_bashrc)


@mcp.tool()
async def setup_project_standards(
    directory: str = ".",
    include_conventions: bool = True,
    include_ai_docs: bool = True,
    conventions_repo: str = "mbailey/conventions", 
    ai_docs_repo: str = "mbailey/ai_docs",
    repos_file: str = ".repos.txt"
) -> Dict[str, any]:
    """
    Set up standard project conventions and AI documentation.
    
    This tool adds the standard conventions and/or ai_docs repositories to your project's
    .repos.txt file and syncs them to create the appropriate symlinks.
    
    Args:
        directory: Project directory (defaults to current directory)
        include_conventions: Whether to include conventions repo (default: True)
        include_ai_docs: Whether to include ai_docs repo (default: True)
        conventions_repo: Conventions repository (default: mbailey/conventions)
        ai_docs_repo: AI docs repository (default: mbailey/ai_docs)
        repos_file: Name of repos file (default: .repos.txt)
        
    Returns:
        Dict with status and results of each operation
    """
    try:
        results = {
            "status": "success",
            "directory": directory,
            "operations": []
        }
        
        # Ensure directory exists
        dir_path = Path(directory)
        if not dir_path.exists():
            return {
                "status": "error",
                "message": f"Directory not found: {directory}"
            }
        
        # Check if any repos should be added
        if not include_conventions and not include_ai_docs:
            return {
                "status": "error",
                "message": "At least one repository must be included"
            }
        
        # Add conventions repository if requested
        if include_conventions:
            conventions_result = await add_repo_entry(
                directory=directory,
                repo=conventions_repo,
                target_name="docs/conventions",
                file_name=repos_file
            )
            results["operations"].append({
                "operation": "add_conventions",
                "result": conventions_result
            })
        
        # Add ai_docs repository if requested
        if include_ai_docs:
            ai_docs_result = await add_repo_entry(
                directory=directory,
                repo=ai_docs_repo,
                target_name="docs/ai_docs",
                file_name=repos_file
            )
            results["operations"].append({
                "operation": "add_ai_docs", 
                "result": ai_docs_result
            })
        
        # Run sync to clone and create symlinks
        sync_result = await sync_directory(directory)
        results["operations"].append({
            "operation": "sync",
            "result": sync_result
        })
        
        # Check if all operations succeeded
        all_success = all(
            op["result"].get("status") in ["success", "exists", "completed", "added"]
            for op in results["operations"]
        )
        
        if all_success:
            results["message"] = "Project standards set up successfully"
            results["next_steps"] = [
                "Review docs/conventions/CONVENTIONS.md for project conventions",
                "Browse docs/ai_docs/ for AI-optimized documentation",
                "Customize by adding overrides to your project"
            ]
        else:
            results["status"] = "partial"
            results["message"] = "Some operations failed - check individual results"
            
        return results
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to set up project standards: {str(e)}"
        }


@mcp.tool()
async def sync_directory(directory: str) -> Dict[str, any]:
    """
    Run mt sync on a directory to synchronize repositories.
    
    Args:
        directory: Directory to sync
        
    Returns:
        Dict with status, stdout, stderr, and return code
    """
    try:
        # Find metool installation
        # First check if MT_ROOT is set
        mt_root = os.environ.get('MT_ROOT')
        
        if not mt_root:
            # Try to find metool relative to this script
            # Go up from mcp/src/metool_mcp to find the root
            current_file = Path(__file__).resolve()
            potential_root = current_file.parent.parent.parent.parent
            if (potential_root / 'shell' / 'mt').exists():
                mt_root = str(potential_root)
            else:
                # Try common locations
                for location in [
                    Path.home() / 'metool',
                    Path.home() / '.metool',
                    Path('/usr/local/metool'),
                    Path('/opt/metool')
                ]:
                    if (location / 'shell' / 'mt').exists():
                        mt_root = str(location)
                        break
        
        if not mt_root:
            return {
                "status": "error",
                "message": "Cannot find metool installation. Set MT_ROOT environment variable."
            }
        
        # Create bash command that sources mt and runs sync
        bash_cmd = f'source "{mt_root}/shell/mt" && mt sync "{directory}"'
        
        # Run the command in bash
        result = await asyncio.create_subprocess_exec(
            'bash', '-c', bash_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=directory,
            env={**os.environ, 'MT_ROOT': mt_root}
        )
        
        stdout, stderr = await result.communicate()
        
        return {
            "status": "completed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": stdout.decode('utf-8'),
            "stderr": stderr.decode('utf-8')
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Failed to sync directory: {str(e)}"
        }


@mcp.tool()
async def list_repos(directory: str, file_name: str = ".repos.txt") -> Dict[str, any]:
    """
    List repositories from a repos.txt file.
    
    Args:
        directory: Directory containing the repos.txt file
        file_name: Name of the repos file (default: ".repos.txt")
        
    Returns:
        Dict with repos list or error message
    """
    try:
        repo_file = Path(directory) / file_name
        
        if not repo_file.exists():
            return {
                "status": "not_found",
                "message": f"No {file_name} found in {directory}",
                "repos": []
            }
            
        content = repo_file.read_text()
        repos = []
        
        for line in content.splitlines():
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                repos.append(line)
                
        return {
            "status": "success",
            "file": str(repo_file),
            "repos": repos
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list repos: {str(e)}"
        }


@mcp.prompt()
async def project_setup() -> str:
    """Guide for setting up a new project with standard conventions and documentation."""
    return """To set up a new project with standard conventions and AI documentation:

Use the setup_project_standards tool to automatically:
1. Add mbailey/conventions to .repos.txt (symlinked as docs/conventions/)
2. Add mbailey/ai_docs to .repos.txt (symlinked as docs/ai_docs/)
3. Run mt sync to clone and create the symlinks

Example usage:
- `setup_project_standards()` - Set up both conventions and ai_docs in current directory
- `setup_project_standards(directory="/path/to/project")` - Set up in specific directory
- `setup_project_standards(include_ai_docs=False)` - Only install conventions
- `setup_project_standards(include_conventions=False)` - Only install ai_docs
- `setup_project_standards(conventions_repo="myorg/conventions")` - Use custom repos

After setup:
- docs/conventions/CONVENTIONS.md - Engineering conventions and standards
- docs/ai_docs/ - AI-optimized documentation for tools and frameworks
- .repos.txt - Manifest file listing all external dependencies

The conventions and ai_docs directories are symlinks to shared repositories,
making it easy to keep standards consistent across multiple projects.
"""


@mcp.prompt()
async def setup_metool() -> str:
    """Guide for setting up metool on a new system."""
    return """To set up metool on your system:

1. Use the install_or_update_metool tool to install metool
2. The tool will:
   - Clone metool from GitHub (or update if already installed)
   - Optionally update your .bashrc to source metool
   - Run mt install to set up symlinks

Example usage:
- `install_or_update_metool()` - Install to ~/metool with .bashrc update
- `install_or_update_metool(install_dir="/opt/metool", update_bashrc=False)` - Custom location

After installation:
- Restart your shell or run: source ~/.bashrc
- Verify with: mt --help
- Install additional modules: mt install module-name
"""


@mcp.prompt()
async def conventions_add(repo: str = "mbailey/conventions", target: str = "docs/conventions") -> str:
    """Guide for adding conventions repository to a project."""
    return f"""To add the conventions repository '{repo}' to your project:

1. First, I'll check if .repos.txt exists in your project root
2. Then add the entry: "{repo} {target}"
3. Finally, run mt sync to clone/update and create the symlink

The slash command syntax is:
- `/metool:conventions-add {repo}` - Uses target name '{target}'
- `/metool:conventions-add owner/repo target-name` - Custom target

Steps I'll perform:
1. Call add_repo_entry(directory=".", repo="{repo}", target_name="{target}")
2. Call sync_directory(directory=".")

This will clone {repo} to the canonical location and create a symlink at {target}
"""


@mcp.prompt()
async def manage_repos() -> str:
    """Guide for managing repository manifest files."""
    return """Repository manifest files (.repos.txt or repos.txt) declare git repositories for your project.

Format:
```
# Comments start with #
repo-owner/repo-name                          # Default target name
repo-owner/repo-name custom-name              # Custom target directory
github.com_account:owner/repo target-name     # With SSH host identity
_account:owner/repo target                    # GitHub shorthand
repo@branch target                            # Specific branch/tag
```

Common operations:
1. Add a repository: Use add_repo_entry tool
2. Sync repositories: Use sync_directory tool  
3. List current repos: Use list_repos tool

The mt sync command will:
- Clone missing repositories
- Update existing repositories
- Create/update symlinks for shared repos
- Handle multi-account SSH configurations
"""


@mcp.resource("repos-file://{directory}")
async def get_repos_file(directory: str) -> str:
    """
    Get contents of a repos.txt file from a directory.
    
    Args:
        directory: Directory containing the repos.txt file
    """
    repo_file = Path(directory) / ".repos.txt"
    
    if not repo_file.exists():
        # Try repos.txt without dot
        repo_file = Path(directory) / "repos.txt"
        
    if not repo_file.exists():
        return f"# No repos.txt or .repos.txt found in {directory}\n"
        
    return repo_file.read_text()


def main():
    """Run the MCP server."""
    import sys
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()