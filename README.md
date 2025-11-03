# DatahubMCP - Data Management MCP Server

> A unified MCP (Model Context Protocol) server that provides seamless access to MySQL databases and Google Workspace APIs through Claude Desktop.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# DatahubMCP - Education Data Integration Server

> MCP server enabling Claude to query MySQL databases and Google Workspace for education program management.

## What It Does

Connects Claude Desktop to:
- **MySQL Database**: Attendance, lesson plans, DRDP assessments, support reports
- **Google Workspace**: Sheets, Forms, Drive integration
- **Built-in Templates**: Data analysis and report generation prompts

## Tech Stack

**Backend**: Python 3.13, FastMCP, SQLAlchemy  
**APIs**: MySQL, Google OAuth 2.0, Google Sheets/Forms/Drive  
**Config**: Environment variables, credential management  
**Architecture**: Service layer pattern, connection pooling, context managers

## Quick Start

```bash
# Install dependencies
uv sync

# Configure credentials
cp .env.example .env
# Edit .env with your DB and Google credentials

# Add to Claude Desktop config
{
  "mcpServers": {
    "datahub": {
      "command": "uv",
      "args": ["--directory", "/path/to/DatahubMCP", "run", "kmmcp.py"]
    }
  }
}
```

## Key Features

**Database Tools**
- Query attendance logs, lesson plans, DRDP records
- Filter by date range, site, classroom, child ID
- Hierarchical site/classroom listing

**Google Workspace Tools**
- List/read spreadsheets, create forms
- Sheet data as MCP resources
- OAuth authentication flow

**Prompts**
- `analyze_sheet_data`: Comprehensive analysis template
- `create_report_template`: Professional reports
- `form_to_sheet`: Form-to-spreadsheet workflow

## Project Structure

```
kmmcp.py           # FastMCP server with tool definitions
database.py        # MySQL session management
google_service.py  # Google OAuth & API builders
models.py          # SQLAlchemy ORM models
.env.example       # Configuration template
```

## Example Usage

Via Claude Desktop natural language:

```
"Show attendance for site S001 last week"
"Query DRDP records for child C456"
"List my recent spreadsheets"
"Create a feedback form"
```

## Technical Highlights

- **Session Management**: Context managers for safe DB/API access
- **Type Safety**: Full type hints throughout codebase
- **Security**: Environment-based config, `.gitignore` for credentials
- **Error Handling**: Comprehensive validation and user-friendly messages
- **Separation of Concerns**: Modular architecture (DB/API/MCP layers)

## Documentation

- `SETUP.md` - Step-by-step installation guide
- `HOW_TO_CONFIGURE.md` - Environment configuration reference
- `README.md` - Full documentation (this file)

## Skills Demonstrated

✅ API Integration (Google OAuth, MySQL)  
✅ Database ORM with SQLAlchemy  
✅ MCP Protocol Implementation  
✅ Environment-based Configuration  
✅ Clean Architecture & Separation of Concerns  
✅ Type-safe Python Development  

---

**Built for**: Kai Ming Head Start education program management  
**License**: MIT  
**Contact**: yucheng.contact@gmail.com