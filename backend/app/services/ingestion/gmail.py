import os
import base64
import logging
import re
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.content_item import ContentItem

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'token.json')
    creds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'client_secret_146491076494-bgb2t7vrjbihoaa7ftvt28f05kj49vof.apps.googleusercontent.com.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as error:
        logger.error(f'An error occurred: {error}')
        return None

def _get_body_from_payload(payload) -> str:
    """Helper to extract text or HTML body from Gmail message payload."""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            elif part['mimeType'] == 'text/html':
                data = part['body'].get('data')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            elif 'parts' in part:
                 return _get_body_from_payload(part)
    elif 'body' in payload and 'data' in payload['body']:
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    return ""

def _extract_links_and_text(html_content: str) -> tuple[str, str, str]:
    """Parse HTML email to extract pure text and the most likely main link."""
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text(separator=' ', strip=True)
    
    # Try to find the first/most prominent link
    primary_link = ""
    links = soup.find_all('a', href=True)
    if links:
        # Just grab the first real link for the MVP
        for a in links:
            href = a['href']
            if href.startswith('http') and 'unsubscribe' not in href.lower():
                primary_link = href
                break
                
    return text_content, primary_link

def fetch_from_gmail_label(label_name: str, db: Session) -> int:
    """Fetch emails from a specific label and ingest as content items."""
    service = get_gmail_service()
    if not service:
        logger.error("Failed to initialize Gmail service")
        return 0
        
    try:
        # 1. Find the label ID
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        target_label_id = None
        for label in labels:
            if label['name'].lower() == label_name.lower():
                target_label_id = label['id']
                break
                
        if not target_label_id:
            logger.warning(f"Label '{label_name}' not found")
            return 0
            
        # 2. Get messages with this label (that we haven't processed)
        # In a real app we'd track historyId, for MVP we just fetch recent and deduplicate by Message-ID
        results = service.users().messages().list(
            userId='me', 
            labelIds=[target_label_id],
            maxResults=20
        ).execute()
        
        messages = results.get('messages', [])
        if not messages:
            logger.info("No new messages found for label.")
            return 0
            
        items_added = 0
            
        # 3. Process each message
        for msg in messages:
            msg_id = msg['id']
            message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            
            headers = message['payload'].get('headers', [])
            subject = "No Subject"
            date_str = ""
            sender = ""
            
            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                elif header['name'] == 'Date':
                    date_str = header['value']
                elif header['name'] == 'From':
                    sender = header['value']
            
            # Use Gmail message ID as the URL if no primary link is found (acts as unique key)
            unique_url = f"gmail://{msg_id}"
            
            # Extract body
            body = _get_body_from_payload(message['payload'])
            text_content = body
            primary_link = ""
            
            if '<html' in body.lower():
                text_content, primary_link = _extract_links_and_text(body)
                
            if primary_link:
                unique_url = primary_link
                
            # Truncate summary
            summary = text_content[:497] + '...' if len(text_content) > 500 else text_content
            
            existing = db.query(ContentItem).filter(ContentItem.url == unique_url).first()
            if existing:
                continue
                
            new_item = ContentItem(
                type='email',
                title=subject,
                summary=summary,
                url=unique_url,
                source=f"Gmail ({sender})",
                tags=["gmail", label_name]
            )
            
            try:
                db.add(new_item)
                db.commit()
                items_added += 1
            except IntegrityError:
                db.rollback()
            except Exception as e:
                db.rollback()
                logger.error(f"Error adding email item: {str(e)}")
                
        return items_added

    except Exception as error:
        logger.error(f'An error occurred fetching Gmail: {error}')
        return 0
