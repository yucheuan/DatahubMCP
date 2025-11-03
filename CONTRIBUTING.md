# Contributing to DatahubMCP

Thank you for your interest in contributing to DatahubMCP! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:

1. **Check existing issues** to see if it's already reported
2. **Create a new issue** with a clear title and description
3. **Include details**:
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Your environment (OS, Python version, etc.)
   - Error messages or logs

### Submitting Pull Requests

1. **Fork the repository** and create a new branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines below

3. **Test your changes** thoroughly
   - Ensure database connections work
   - Test Google API integrations (if modified)
   - Verify MCP tools function correctly

4. **Commit your changes** with clear messages
   ```bash
   git commit -m "Add: Brief description of changes"
   ```

5. **Push to your fork** and submit a pull request
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and under 50 lines when possible

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param2 is negative
    """
    pass
```

### Database Models

- Use descriptive column names
- Add comments for non-obvious fields
- Include relationships where appropriate
- Document any special constraints

### MCP Tools

When adding new MCP tools:

1. **Use the `@mcp.tool()` decorator**
2. **Include comprehensive docstrings**
3. **Add input validation**
4. **Return structured data** (JSON-serializable)
5. **Handle errors gracefully** with clear messages

Example:

```python
@mcp.tool()
def query_something(
    required_param: str,
    optional_param: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """Query something from the database.
    
    Args:
        required_param: Description of required parameter
        optional_param: Description of optional parameter
        limit: Maximum number of records to return (default: 100)
    
    Returns:
        Dictionary containing query results
    """
    # Implementation with error handling
    pass
```

## Development Setup

1. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/DatahubMCP.git
   cd DatahubMCP
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your test database credentials
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature
   ```

## Testing

Before submitting a PR:

- [ ] Test database connections
- [ ] Verify Google API functionality (if modified)
- [ ] Test with Claude Desktop
- [ ] Check for no regressions in existing features
- [ ] Ensure all new code has docstrings
- [ ] No hardcoded credentials or sensitive data

## Commit Message Guidelines

Use clear, descriptive commit messages:

- `Add: New feature or functionality`
- `Fix: Bug fix`
- `Update: Improvements to existing features`
- `Docs: Documentation updates`
- `Refactor: Code restructuring without behavior change`
- `Test: Adding or updating tests`

Examples:
```
Add: DRDP record query tool with level conversion
Fix: Database connection timeout in get_db_session
Update: Improve Google OAuth error messages
Docs: Add examples for query_lesson_plans
```

## What to Contribute

### Priority Areas

- **Additional database tools** for new table types
- **Google Workspace integrations** (Docs, Calendar, etc.)
- **Error handling improvements**
- **Documentation and examples**
- **Performance optimizations**
- **Tests and test coverage**

### New Features

If you're planning a major new feature:

1. **Open an issue first** to discuss the approach
2. **Get feedback** from maintainers
3. **Implement incrementally** with multiple small PRs if possible

## Code Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged
4. You'll be credited in the release notes!

## Questions?

If you have questions:

- Open an issue with the `question` label
- Check existing documentation
- Review closed issues for similar questions

## Code of Conduct

- Be respectful and professional
- Welcome newcomers
- Focus on constructive feedback
- Keep discussions on-topic

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to DatahubMCP! 🎉

