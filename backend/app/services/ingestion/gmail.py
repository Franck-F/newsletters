import imaplib
import email
import logging
import re
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.content_item import ContentItem
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def _extract_links_and_text(html_content: str) -> tuple[str, str]:
    """Parse HTML email to extract pure text and the most likely main link."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    text_content = soup.get_text(separator=' ', strip=True)
    
    # Try to find the first/most prominent link
    primary_link = ""
    links = soup.find_all('a', href=True)
    if links:
        for a in links:
            href = a['href']
            # Basic heuristic: ignore common tracking/unsubscribe links
            if href.startswith('http') and 'unsubscribe' not in href.lower() and 'manage' not in href.lower():
                primary_link = href
                break
                
    return text_content, primary_link

def fetch_from_gmail_imap(db: Session) -> int:
    """Fetch emails using IMAP and an App Password."""
    if not settings.gmail_app_password:
        logger.warning("Gmail App Password not set")
        return 0

    try:
        # Connect to Gmail IMAP
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(settings.gmail_email, settings.gmail_app_password)
        
        # Select the folder/label
        # Gmail labels are presented as IMAP folders. 
        # For spaces in labels, they should be quoted or used as is.
        status, messages = mail.select(f'"{settings.gmail_label}"')
        if status != 'OK':
            logger.error(f"Could not select label '{settings.gmail_label}'")
            return 0

        # Search for all emails in this label
        status, search_data = mail.search(None, "ALL")
        if status != 'OK':
            return 0

        mail_ids = search_data[0].split()
        items_added = 0

        # Process the most recent 20 emails
        for mail_id in reversed(mail_ids[-20:]):
            status, data = mail.fetch(mail_id, "(RFC822)")
            if status != 'OK':
                continue

            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            subject = email.header.decode_header(msg.get("Subject", "No Subject"))[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            sender = msg.get("From", "Unknown")
            message_id = msg.get("Message-ID", f"imap-{mail_id.decode()}")
            
            # Extract body
            body = ""
            html_body = ""
            
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    try:
                        payload = part.get_payload(decode=True).decode()
                    except Exception:
                        continue
                        
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = payload
                    elif content_type == "text/html" and "attachment" not in content_disposition:
                        html_body = payload
            else:
                body = msg.get_payload(decode=True).decode()

            text_content = html_body if html_body else body
            primary_link = ""
            
            if html_body:
                text_content, primary_link = _extract_links_and_text(html_body)
            
            unique_url = primary_link if primary_link else f"gmail://{message_id}"
            
            # Deduplicate
            existing = db.query(ContentItem).filter(ContentItem.url == unique_url).first()
            if existing:
                continue
                
            summary = text_content[:497] + '...' if len(text_content) > 500 else text_content
            
            new_item = ContentItem(
                type='email',
                title=subject,
                summary=summary,
                url=unique_url,
                source=f"Gmail ({sender})",
                tags=["gmail", settings.gmail_label]
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

        mail.close()
        mail.logout()
        return items_added

    except Exception as e:
        logger.error(f"Errur fetching Gmail via IMAP: {e}")
        return 0

