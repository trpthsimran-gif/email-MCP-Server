import sys
import json
import os

sys.path.insert(0, r"C:\Users\thema\email-mcp-server")
os.chdir(r"C:\Users\thema\email-mcp-server")

from gmail import read_emails, send_email, search_emails, reply_in_thread

def handle_request(request):
    method = request.get("method", "")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "email", "version": "3.0.0"}
            }
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "read_emails",
                        "description": "Read recent emails from Gmail with full body content. Always use this first to get email IDs before replying.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "count": {
                                    "type": "number",
                                    "description": "Number of emails to fetch"
                                }
                            }
                        }
                    },
                    {
                        "name": "reply_in_thread",
                        "description": "Reply to an existing email INSIDE the same conversation thread. No new email is created. ALWAYS use this when user wants to reply to a received email. Never use send_email for replies.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "email_id": {
                                    "type": "string",
                                    "description": "The ID of the email to reply to. Get this from read_emails first."
                                },
                                "reply_body": {
                                    "type": "string",
                                    "description": "The reply message text"
                                }
                            },
                            "required": ["email_id", "reply_body"]
                        }
                    },
                    {
                        "name": "send_email",
                        "description": "Send a BRAND NEW email. Only use this for new emails, never for replies.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "to":      {"type": "string", "description": "Recipient email address"},
                                "subject": {"type": "string", "description": "Email subject"},
                                "body":    {"type": "string", "description": "Email body"}
                            },
                            "required": ["to", "subject", "body"]
                        }
                    },
                    {
                        "name": "search_emails",
                        "description": "Search emails using Gmail search syntax",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Gmail search e.g. from:john, subject:invoice, is:unread"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                ]
            }
        }

    elif method == "tools/call":
        tool_name = request.get("params", {}).get("name", "")
        args      = request.get("params", {}).get("arguments", {})

        try:
            if tool_name == "read_emails":
                count  = int(args.get("count", 5))
                result = read_emails(count)
                text   = json.dumps(result, indent=2)

            elif tool_name == "reply_in_thread":
                text = reply_in_thread(
                    args["email_id"],
                    args["reply_body"]
                )

            elif tool_name == "send_email":
                text = send_email(
                    args["to"],
                    args["subject"],
                    args["body"]
                )

            elif tool_name == "search_emails":
                result = search_emails(args["query"])
                text   = json.dumps(result, indent=2)

            else:
                text = f"Unknown tool: {tool_name}"

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": text}]
                }
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Error: {str(e)}"}]
                }
            }

    elif method == "notifications/initialized":
        return None

    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }


def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            request  = json.loads(line)
            response = handle_request(request)
            if response is not None:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            continue
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
