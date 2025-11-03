# 🔧 Configuration Quick Reference

This guide shows you exactly how to set up your environment variables.

## Step 1: Copy the Template

```bash
cp .env.example .env
```

## Step 2: Edit Your .env File

Open the `.env` file and replace the placeholder values:

### Database Configuration

```env
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database_name
```

**Where to get these values:**
- `DB_USER`: Your MySQL username (e.g., "root", "admin", or your custom user)
- `DB_PASSWORD`: Your MySQL password
- `DB_HOST`: Database server address (use "localhost" if running locally)
- `DB_PORT`: MySQL port (default is 3306)
- `DB_NAME`: Name of your database

**Example:**
```env
DB_USER=myapp_user
DB_PASSWORD=SecurePassword123!
DB_HOST=localhost
DB_PORT=3306
DB_NAME=education_data
```

### Google API Configuration (Optional)

```env
GOOGLE_CREDENTIALS_PATH=credentials.json
```

**Where to get this:**
1. Go to https://console.cloud.google.com/
2. Create a project or select existing one
3. Enable: Google Sheets API, Google Forms API, Google Drive API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the JSON file
6. Save it as `credentials.json` in your project folder

**Note:** If you only need database features, you can skip this step.

## Step 3: Test Your Configuration

### Test Database Connection

```bash
# Try connecting directly
mysql -u your_username -p -h localhost -P 3306 your_database_name
```

If this works, your database config is correct!

### Test the MCP Server

```bash
uv run kmmcp.py
```

If you see errors, check:
- Database credentials are correct
- MySQL server is running
- Database exists

## Claude Desktop Configuration

After setting up `.env`, configure Claude Desktop:

**macOS Config File Location:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Add This Configuration:**
```json
{
  "mcpServers": {
    "datahub": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/glennhuang/Desktop/YC Studio/DatahubMCP",
        "run",
        "kmmcp.py"
      ]
    }
  }
}
```

**Important:** Use the absolute path to your project (shown above).

## Security Checklist

- [ ] `.env` file is created (not `.env.example`)
- [ ] `.env` contains your actual credentials
- [ ] `.env` is listed in `.gitignore` (already done)
- [ ] Never commit `.env` to git
- [ ] Never share `.env` file or credentials
- [ ] `credentials.json` is also in `.gitignore` (already done)

## Quick Troubleshooting

### "Database connection failed"
- ✅ Check MySQL is running: `mysql.server status` (macOS)
- ✅ Verify username/password: Try connecting with mysql client
- ✅ Check database exists: `SHOW DATABASES;` in mysql
- ✅ Verify port is correct (default: 3306)

### "Google authentication failed"
- ✅ Check `credentials.json` exists in project folder
- ✅ Verify APIs are enabled in Google Cloud Console
- ✅ Delete `token.pickle` and try again
- ✅ Check `GOOGLE_CREDENTIALS_PATH` in `.env`

### "Module not found"
- ✅ Run `uv sync` to install dependencies
- ✅ Make sure you're in the project directory
- ✅ Check Python version: `python --version` (need 3.13+)

## Example .env File (Complete)

Here's what your complete `.env` file should look like:

```env
# Database Configuration
DB_USER=myapp_user
DB_PASSWORD=SecurePassword123!
DB_HOST=localhost
DB_PORT=3306
DB_NAME=education_data

# Google API Configuration
GOOGLE_CREDENTIALS_PATH=credentials.json
```

That's it! Your configuration is complete. 🎉

## Next Steps

1. ✅ Configure `.env` file (this guide)
2. 📋 Configure Claude Desktop
3. 🔄 Restart Claude Desktop
4. 🧪 Test by asking Claude: "What MCP tools are available?"

Need more help? Check:
- `SETUP.md` - Complete setup guide
- `README.md` - Full documentation
- `GITHUB_SETUP_SUMMARY.md` - Publishing guide
