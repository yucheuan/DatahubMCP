# DatahubMCP - Data Management MCP Server

> A unified MCP (Model Context Protocol) server that provides seamless access to MySQL databases and Google Workspace APIs through Claude Desktop.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

DatahubMCP is a production-ready MCP server that enables AI assistants (like Claude) to:
- **Query MySQL Databases**: Execute complex database queries for attendance tracking, lesson plans, assessments, and reports
- **Manage Google Workspace**: Interact with Google Sheets, Forms, and Drive programmatically
- **Provide Structured Data**: Format and analyze data with built-in templates and prompts

This project demonstrates best practices in:
- API integration (Google OAuth, MySQL connections)
- Database ORM with SQLAlchemy
- MCP server development with FastMCP
- Environment-based configuration
- Clean architecture and separation of concerns

## Features

### Database Tools
- Query attendance logs with flexible date ranges
- Search center support reports by site, staff, or date
- Retrieve lesson plans (Preschool & Infant/Toddler)
- Access DRDP assessment records with human-readable level conversions
- List sites and classrooms in hierarchical structure

### Google Workspace Tools
- List and search Google Spreadsheets
- Read data from sheets with custom ranges
- Create new spreadsheets and forms
- Access sheet data as MCP resources

### Built-in Prompts
- `analyze_sheet_data`: Comprehensive sheet analysis template
- `create_report_template`: Professional report generation
- `form_to_sheet`: Complete form-to-spreadsheet workflow

## Architecture

```
DatahubMCP/
├── kmmcp.py              # Main MCP server with all tools
├── database.py           # MySQL connection pooling & session management
├── google_service.py     # Google OAuth & API service builders
├── models.py             # SQLAlchemy ORM models
├── .env.example          # Example environment configuration
└── README.md             # Documentation
```

## Prerequisites

- Python 3.13 or higher
- MySQL database (if using database features)
- Google Cloud account (if using Google Workspace features)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yucheuan/DatahubMCP.git
cd DatahubMCP
```

### 2. Install uv Package Manager

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```bash
# Database Configuration (required for database tools)
DB_USER=your_database_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database_name

# Google API Configuration (required for Google Workspace tools)
GOOGLE_CREDENTIALS_PATH=credentials.json
```

**⚠️ Security Note**: Never commit the `.env` file to version control. It's already in `.gitignore`.

### 5. Get Google API Credentials (Optional)

Only needed if you want to use Google Workspace features:

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project** or select an existing one
3. **Enable APIs**:
   - Navigate to "APIs & Services" → "Library"
   - Enable: Google Sheets API, Google Forms API, Google Drive API
4. **Create OAuth Credentials**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the credentials JSON file
5. **Save the file** as `credentials.json` in the project root directory

### 6. First Run Authentication

On first run, the server will authenticate with Google:
1. A browser window will open automatically
2. Sign in with your Google account
3. Grant the requested permissions
4. A `token.pickle` file will be created automatically for future use

**Note**: `token.pickle` is excluded from git for security.

## Usage

### Running with Claude Desktop

Add this configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "datahub": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/DatahubMCP",
        "run",
        "kmmcp.py"
      ]
    }
  }
}
```

**Replace** `/absolute/path/to/DatahubMCP` with the actual path where you cloned this repository.

After adding the configuration:
1. Restart Claude Desktop
2. The MCP server will start automatically when Claude launches
3. You can now use the database and Google Workspace tools through natural language

### Running Standalone

You can also run the server directly for testing:

```bash
uv run kmmcp.py
```

## Available Tools

### Database Operations

| Tool | Description |
|------|-------------|
| `get_sites_with_classrooms(site_name)` | List all sites with their classrooms |
| `query_attendance_logs(...)` | Query daily attendance logs with flexible filters |
| `query_center_support_reports(...)` | Retrieve center support reports by site/staff/date |
| `query_lesson_plans(...)` | Get lesson plans (preschool or infant/toddler) |
| `query_drdp_records(...)` | Access DRDP assessments with level descriptions |

### Google Workspace Operations

| Tool | Description |
|------|-------------|
| `list_spreadsheets(max_results)` | List user's Google Spreadsheets |
| `read_sheet(spreadsheet_id, range_name)` | Read data from a specific sheet range |
| `create_spreadsheet(title)` | Create a new Google Spreadsheet |
| `create_form(title, description)` | Create a new Google Form |

### Resources

- `sheet://{spreadsheet_id}/{range_name}` - Access Google Sheet data as an MCP resource

### Prompts

- `analyze_sheet_data` - Comprehensive data analysis workflow
- `create_report_template` - Professional report generation template
- `form_to_sheet` - Complete form-to-spreadsheet workflow guide

## Example Queries

Once configured with Claude Desktop, you can ask natural language questions:

### Database Queries
```
"Show me all sites with their classrooms"
"Get attendance logs for site S001 from last week"
"Query lesson plans for room R123 in October 2024"
"Show DRDP records for child ID C456 from the last month"
"Find center support reports by staff member John Doe"
```

### Google Workspace
```
"List my most recent spreadsheets"
"Read data from spreadsheet 1abc123xyz in range Sheet1!A1:C10"
"Create a new spreadsheet called Q1 Sales Report"
"Create a feedback form titled Customer Satisfaction Survey"
"Analyze the data in my Budget 2024 spreadsheet"
```

### Using Prompts
```
"Use the analyze_sheet_data prompt to analyze my survey results"
"Create a professional report template"
"Help me set up a form-to-sheet workflow for collecting feedback"
```

## Tips

- **Spreadsheet IDs**: Find them in the URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
- **Date Formats**: Use `YYYY-MM-DD` format for date parameters
- **Range Notation**: Use A1 notation like `Sheet1!A1:C10` for sheet ranges

## Troubleshooting

### Google Authentication Issues

**Problem**: Browser doesn't open or authentication fails

**Solutions**:
- Delete `token.pickle` and restart the server to re-authenticate
- Verify APIs are enabled in Google Cloud Console
- Check that `GOOGLE_CREDENTIALS_PATH` in `.env` points to valid `credentials.json`
- Ensure OAuth consent screen is configured in Google Cloud Console

### Database Connection Issues

**Problem**: Database connection errors

**Solutions**:
- Verify all database credentials in `.env` are correct
- Check that MySQL server is running and accessible
- Test connection using MySQL client: `mysql -u username -p -h hostname`
- Verify firewall rules allow connections to MySQL port
- Check if the database and tables exist

### Claude Desktop Not Detecting Server

**Problem**: MCP tools don't appear in Claude

**Solutions**:
- Verify the config path is correct in `claude_desktop_config.json`
- Use absolute paths (not relative paths like `~/` or `./`)
- Restart Claude Desktop completely after configuration changes
- Check Claude Desktop logs for error messages
- Ensure `uv` is installed and in system PATH

### Import or Dependency Errors

**Problem**: Module not found errors

**Solutions**:
- Run `uv sync` to ensure all dependencies are installed
- Check Python version is 3.13 or higher: `python --version`
- If using virtual environment, ensure it's activated

## Project Structure

```
DatahubMCP/
├── kmmcp.py              # Main MCP server (FastMCP application)
├── database.py           # MySQL connection pooling & session management
├── google_service.py     # Google OAuth flow & API service builders
├── models.py             # SQLAlchemy ORM models for database tables
├── .env.example          # Template for environment configuration
├── .gitignore            # Git ignore rules (excludes sensitive files)
├── pyproject.toml        # Project metadata & dependencies
├── README.md             # This file
└── uv.lock               # Dependency lock file (auto-generated)
```

## Development

This project demonstrates clean architecture principles:

- **Separation of Concerns**: Database, Google API, and MCP logic are separated
- **Session Management**: Context managers for safe resource handling
- **Environment-based Config**: No hardcoded credentials
- **Type Hints**: Full type annotations for better IDE support
- **Error Handling**: Comprehensive validation and error messages
- **Documentation**: Docstrings for all public functions and tools

### Key Design Patterns

- **Context Managers**: `get_db_session()` ensures database connections are properly closed
- **Service Builders**: Google service functions handle OAuth and credential refresh
- **ORM Models**: SQLAlchemy models provide type-safe database access
- **FastMCP Decorators**: Clean tool/resource/prompt registration

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](#) file for details.

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) by Marvin
- Uses [Anthropic's MCP](https://modelcontextprotocol.io/) for AI integration
- Database ORM powered by [SQLAlchemy](https://www.sqlalchemy.org/)
- Package management by [uv](https://github.com/astral-sh/uv)

## Contact

**Project Link**: [https://github.com/yucheuan/DatahubMCP](https://github.com/yucheuan/DatahubMCP)

---

Built with ❤️ for seamless AI-powered data management
