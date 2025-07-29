# metool-mcp

MCP (Model Context Protocol) server for [metool](https://github.com/mbailey/metool) - a shell environment incubator.

## Features

This MCP server provides AI assistants with tools to manage metool repository manifests and synchronization:

### Tools
- **install_or_update_metool** - Install or update metool on your system
- **setup_project_standards** - Set up standard conventions and AI docs for a project
- **add_repo_entry** - Add repository entries to .repos.txt files
- **sync_directory** - Run `mt sync` to clone/update repositories and create symlinks
- **list_repos** - List repositories from .repos.txt files

### Prompts
- **setup_metool** - Guide for setting up metool on a new system
- **project_setup** - Guide for setting up a new project with standards
- **conventions_add** - Guide for adding conventions repositories
- **manage_repos** - Comprehensive guide for repository management

### Resources
- **repos-file** - Access contents of repos.txt files

## Installation

### Via uvx (recommended)
```bash
uvx install metool-mcp
```

### Via pip
```bash
pip install metool-mcp
```

### From source
```bash
git clone https://github.com/mbailey/metool.git
cd metool/mcp
pip install -e .
```

## Usage

### With Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "metool": {
      "command": "uvx",
      "args": ["metool-mcp"]
    }
  }
}
```

### Slash Commands

After configuring, you can use these commands in Claude:

- `/metool:setup-metool` - Install or update metool on your system
- `/metool:project-setup` - Set up a new project with conventions and AI docs
- `/metool:conventions-add mbailey/conventions` - Add conventions to your project
- `/metool:manage-repos` - Get help managing repository files

## Example Workflow

1. **Set up a new project with standards:**
   ```
   /metool:project-setup
   ```
   This will automatically:
   - Add mbailey/conventions and mbailey/ai_docs to .repos.txt
   - Run `mt sync` to clone and create symlinks
   - Set up docs/conventions/ and docs/ai_docs/ directories

2. **Add a specific conventions repository:**
   ```
   /metool:conventions-add mbailey/conventions
   ```
   This will:
   - Add "mbailey/conventions docs/conventions" to .repos.txt
   - Run `mt sync` to clone and symlink the repository

3. **Add custom repositories:**
   ```python
   # The MCP server can help you:
   - Add entries to .repos.txt
   - Sync to clone/update repositories
   - List current repository configuration
   ```

## Requirements

- Python 3.10+
- Git for repository operations
- [metool](https://github.com/mbailey/metool) - Can be installed via the MCP server's `install_or_update_metool` tool

## Development

```bash
# Install in development mode
cd metool/mcp
pip install -e .

# Run tests
pytest

# Run the server directly
python -m metool_mcp.server
```

## License

Same as metool - see main repository for license information.