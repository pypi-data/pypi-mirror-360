# Background
VoiceBot is a project written in Python. Its purpose is to send Discord notifications whenever a user enters a Discord voice channel.

# Python
- Use uv to manage Python and all python packages.
- Use 'uv add [package_name]' instead of 'uv pip install [package_name]'.

# Testing
- Use pytest for Python testing.
- Ensure all code is formatted and linted with Ruff.

# Files
- Do not create binary files, such as Lambda zip files.
- Do not modify CHANGELOG.md. This is handled by CI.

# Commits
- Use conventional commits for all changes.
    - Prefix all commit messages with fix:; feat:; build:; chore:; ci:; docs:; style:; refactor:; perf:; or test: as appropriate.