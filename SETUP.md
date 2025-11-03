# Quick Setup Guide

This guide will walk you through setting up DatahubMCP from scratch.

## Step-by-Step Setup

### 1️⃣ Install uv (Python Package Manager)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2️⃣ Install Project Dependencies

```bash
cd DatahubMCP
uv sync
```

This will:
- Create a virtual environment
- Install all required Python packages
- Set up the project for development

### 3️⃣ Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit with your credentials
# macOS/Linux: nano .env
# Windows: notepad .env
```

**Required Configuration:**

```env
# Database Configuration
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database_name

# Google API Configuration (optional)
GOOGLE_CREDENTIALS_PATH=credentials.json
```

### 4️⃣ Set Up Google API Credentials (Optional)

**Skip this if you only need database features.**

1. **Create a Google Cloud Project:**
   - Visit https://console.cloud.google.com/
   - Click "Select a project" → "New Project"
   - Name it (e.g., "DatahubMCP")

2. **Enable Required APIs:**
   - Go to "APIs & Services" → "Library"
   - Search and enable:
     - Google Sheets API
     - Google Forms API
     - Google Drive API

3. **Create OAuth Credentials:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Name it (e.g., "DatahubMCP Desktop")
   - Click "Create"

4. **Download Credentials:**
   - Click the download button (⬇️) next to your new OAuth client
   - Save the file as `credentials.json` in the DatahubMCP directory

### 5️⃣ Configure Claude Desktop

**Find your config file:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Add this configuration:**

```json
{
  "mcpServers": {
    "datahub": {
      "command": "uv",
      "args": [
        "--directory",
        "/FULL/PATH/TO/DatahubMCP",
        "run",
        "kmmcp.py"
      ]
    }
  }
}
```

**Important:** Replace `/FULL/PATH/TO/DatahubMCP` with:
- macOS/Linux: Use `pwd` command in the project directory
- Windows: Right-click folder → Properties → Copy location

### 6️⃣ Test the Setup

**Restart Claude Desktop completely** (Quit and reopen)

When Claude starts, you should see the MCP tools available. Try asking:

```
"Can you list the available MCP tools?"
"Show me what database tools are available"
```

## Verification Checklist

- [ ] `uv` is installed and in PATH
- [ ] Dependencies installed with `uv sync`
- [ ] `.env` file created and configured
- [ ] Database connection works (test with MySQL client if available)
- [ ] `credentials.json` downloaded (if using Google features)
- [ ] Claude Desktop config updated with absolute path
- [ ] Claude Desktop restarted
- [ ] MCP tools appear in Claude

## Common Issues

### "uv: command not found"

**Solution:** Restart your terminal or add uv to PATH:
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

### "Database connection failed"

**Solutions:**
- Verify MySQL is running: `mysql -u username -p`
- Check credentials in `.env`
- Test connection: `mysql -u username -p -h hostname database_name`

### "Google authentication fails"

**Solutions:**
- Delete `token.pickle` and try again
- Verify `credentials.json` is in the project root
- Check that APIs are enabled in Google Cloud Console

### Claude Desktop doesn't show tools

**Solutions:**
- Use absolute path (not `~` or `./`) in config
- Verify path is correct: `ls /your/path/kmmcp.py`
- Check Claude Desktop logs for errors
- Restart Claude Desktop after config changes

## Getting Help

If you encounter issues:

1. Check the main [README.md](README.md) for detailed troubleshooting
2. Review error messages carefully
3. Open an issue on GitHub with:
   - Your operating system
   - Error messages
   - Steps you've tried

## Next Steps

Once setup is complete:

- Read [README.md](README.md) for usage examples
- Try the example queries
- Explore the available tools and prompts

Happy coding! 🚀

