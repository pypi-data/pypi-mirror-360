# Changelog

All notable changes to metool-mcp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3] - 2025-01-05

### Fixed
- Fixed 'FunctionTool' object is not callable error in `setup_project_standards`
- Refactored internal tool implementations to avoid circular dependencies
- Tools now call internal implementation functions instead of decorated tool functions

## [0.2.2] - 2024-12-21

### Fixed
- Fixed PyPI trusted publishing workflow configuration
- Added required release environment to GitHub Actions

## [0.2.0] - 2024-12-21

### Added
- New `install_or_update_metool` tool to install/update metool from GitHub
- New `setup_project_standards` tool to set up conventions and AI docs
- Support for selective installation with `include_conventions` and `include_ai_docs` parameters
- Comprehensive prompts for setup guidance

### Changed
- Default locations changed from root dotfiles to `docs/` subdirectory:
  - `.conventions` → `docs/conventions`
  - `.ai_docs` → `docs/ai_docs`
- Updated all documentation and prompts to reflect new paths

### Fixed
- Improved error handling in all tools
- Better status reporting from sync operations

## [0.0.1] - 2024-06-23

### Added
- Initial release of metool-mcp
- `add_repo_entry` tool for managing .repos.txt files
- `sync_directory` tool to run mt sync
- `list_repos` tool to list repository configurations
- Repository manifest file management via MCP
- Integration with metool's mt sync functionality