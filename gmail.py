import os
import base64
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def get_email_body(payload):
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                if data:
                    body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                    break
    else:
        data = payload.get("body", {}).get("data", "")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    return body[:500]

def read_emails(count=5):
    service = get_gmail_service()
    results = service.users().messages().list(userId="me", maxResults=count).execute()
    messages = results.get("messages", [])
    emails = []
    for msg in messages:
        detail = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        headers = detail["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(no subject)")
        sender  = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        date    = next((h["value"] for h in headers if h["name"] == "Date"), "")
        body    = get_email_body(detail["payload"])
        emails.append({
            "id": msg["id"],
            "subject": subject,
            "from": sender,
            "date": date,
            "body": body
        })
    return emails

def send_email(to, subject, body):
    service = get_gmail_service()
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return f"New email sent to {to}! ID: {result['id']}"

def reply_in_thread(email_id, reply_body):
    """Reply inside SAME email thread - no new email created"""
    service = get_gmail_service()

    # Get original email
    original = service.users().messages().get(
        userId="me",
        id=email_id,
        format="full"
    ).execute()

    headers   = original["payload"]["headers"]
    thread_id = original["threadId"]

    # Extract headers
    original_from    = ""
    original_subject = ""
    message_id       = ""
    references       = ""

    for h in headers:
        name = h["name"].lower()
        if name == "from":
            original_from = h["value"]
        elif name == "subject":
            original_subject = h["value"]
        elif name == "message-id":
            message_id = h["value"]
        elif name == "references":
            references = h["value"]

    # Build subject
    if original_subject.lower().startswith("re:"):
        reply_subject = original_subject
    else:
        reply_subject = "Re: " + original_subject

    # Build references chain
    new_references = (references + " " + message_id).strip()

    # Build reply
    msg = MIMEMultipart()
    msg["To"]      = original_from
    msg["Subject"] = reply_subject
    if message_id:
        msg["In-Reply-To"] = message_id
        msg["References"]  = new_references
    msg.attach(MIMEText(reply_body, "plain"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

    # Send inside same thread
    result = service.users().messages().send(
        userId="me",
        body={
            "raw": raw,
            "threadId": thread_id
        }
    ).execute()

    if result["threadId"] == thread_id:
        return f"Reply sent in SAME thread! To: {original_from} | Subject: {reply_subject}"
    else:
        return f"Warning: Reply sent but in different thread!"

def search_emails(query, count=5):
    service = get_gmail_service()
    results = service.users().messages().list(userId="me", q=query, maxResults=count).execute()
    messages = results.get("messages", [])
    emails = []
    for msg in messages:
        detail = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = detail["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(no subject)")
        sender  = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        emails.append({"id": msg["id"], "subject": subject, "from": sender})
    return emails
