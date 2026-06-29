# email-MCP-Server
MCP server connecting Claude to Gmail
readme_content = """# Email MCP Server

A Model Context Protocol (MCP) server that connects Claude Desktop to Gmail.

## Features

- Read recent emails with full body content
- Reply to emails in the SAME thread (no duplicate emails)
- Send new emails
- Search emails using Gmail search syntax

## Setup

1. Install dependencies:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

2. Get Gmail API credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a project
   - Enable Gmail API
   - Create OAuth 2.0 Client ID (Desktop App)
   - Download as `credentials.json` and place in this folder

3. Add yourself as a test user in OAuth consent screen

4. Run the notebook to authenticate (opens browser first time)

## Connect to Claude Desktop

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": ["path/to/index.py"]
    }
  }
}
```

## Tools Available

- `read_emails` - Read recent emails with body content
- `reply_in_thread` - Reply to an email in same thread
- `send_email` - Send a new email
- `search_emails` - Search using Gmail syntax

## Note

`credentials.json` and `token.json` are NOT included - you must get your own from Google Cloud Console.
"""

with open('README.md', 'w') as f:
    f.write(readme_content)

print(" README.md created!")
