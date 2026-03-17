import json
import logging
from typing import List, Optional
from datetime import datetime

from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.config import get_settings
from app.models.content_item import ContentItem
from app.models.newsletter import Newsletter, NewsletterContentItem

logger = logging.getLogger(__name__)
settings = get_settings()

def get_genai_client():
    """Initialize the Google GenAI client."""
    if not settings.openai_api_key:
        logger.warning("Google Gemini API key not found in settings!")
        return None
    
    # We repurpose the openai_api_key setting for the Gemini API key
    try:
        return genai.Client(api_key=settings.openai_api_key)
    except Exception as e:
        logger.error(f"Failed to initialize GenAI client: {e}")
        return None

def select_content_items(db: Session, max_items: int = 5, tags: Optional[List[str]] = None, from_date: Optional[datetime] = None) -> List[ContentItem]:
    """Select appropriate content items for the newsletter."""
    
    query = db.query(ContentItem)
    
    if from_date:
        query = query.filter(ContentItem.collected_at >= from_date)
        
    if tags and len(tags) > 0:
        # Simple ilike filter for tags assuming JSONB array as string
        conditions = [ContentItem.tags.cast(str).ilike(f"%{tag}%") for tag in tags]
        query = query.filter(or_(*conditions))
        
    # Get the latest items, prioritizing newer ones
    items = query.order_by(ContentItem.collected_at.desc()).limit(max_items).all()
    return items

def generate_newsletter_draft(db: Session, max_items: int = 5, tags: Optional[List[str]] = None, from_date: Optional[datetime] = None) -> Newsletter:
    """Generate a newsletter draft using selected content and GenAI."""
    
    client = get_genai_client()
    if not client:
        raise ValueError("Google Gemini API client not configured")
        
    items = select_content_items(db, max_items, tags, from_date)
    if not items:
        # Create an empty test newsletter if we have no content
        logger.warning("No content items found for newsletter generation")
        newsletter = Newsletter(
            title=f"Weekly Roundup - {datetime.utcnow().strftime('%B %d, %Y')}",
            status="draft",
            html_body="<p>No new content this week!</p>"
        )
        db.add(newsletter)
        db.commit()
        db.refresh(newsletter)
        return newsletter
        
    # 1. Prepare context for GenAI
    content_context = "Here are the content items collected this week:\\n\\n"
    for i, item in enumerate(items):
        content_context += f"Item {i+1}:\\n"
        content_context += f"Title: {item.title}\\n"
        content_context += f"Source: {item.source}\\n"
        content_context += f"URL: {item.url}\\n"
        content_context += f"Summary/Content: {item.summary}\\n\\n"
        
    prompt = f"""
    You are an expert newsletter editor. Draft a very brief, engaging email newsletter based off the following content.
    
    {content_context}
    
    Provide the output in JSON format exactly matching the schema below:
    {{
        "email_subject": "A catchy subject line",
        "intro_paragraph": "A friendly introductory paragraph summarizing the week's themes",
        "items": [
            {{
                "id": "The Item number you referenced (e.g. 1)",
                "catchy_title": "A rewritten, catchy title for the item",
                "brief_summary": "A 2-sentence max summary of why this is interesting"
            }}
        ],
        "conclusion": "A brief sign-off"
    }}
    """
    
    # 2. Call GenAI 2.5 Flash Lite
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        
        result_json = json.loads(response.text)
        
        # 3. Save the Newsletter to DB
        title = result_json.get("email_subject", "Weekly Newsletter")
        
        newsletter = Newsletter(
            title=title,
            status="draft",
        )
        db.add(newsletter)
        db.flush() # get ID
        
        # Map generated items back to DB items
        generated_items = result_json.get("items", [])
        
        # We will build the rough HTML body here. Later this should use a Jinja template engine `template_engine.py`
        html_body = f"<h2>{title}</h2>"
        html_body += f"<p>{result_json.get('intro_paragraph', '')}</p>"
        
        html_body += "<ul>"
        for i, item in enumerate(generated_items):
            try:
                # Parse "Item 1" or "1" to index 0
                idx_str = str(item.get("id", "")).replace("Item", "").strip()
                idx = int(idx_str) - 1
                db_item = items[idx]
                
                # Create association
                assoc = NewsletterContentItem(
                    newsletter_id=newsletter.id,
                    content_item_id=db_item.id,
                    position=i,
                    section="Main"
                )
                db.add(assoc)
                
                # Append to HTML
                catchy_title = item.get("catchy_title", db_item.title)
                brief_summary = item.get("brief_summary", db_item.summary[:100])
                html_body += f"<li><a href='{db_item.url}'><b>{catchy_title}</b></a> - {brief_summary}</li>"
                
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to map AI item to DB item: {e}")
                
        html_body += "</ul>"
        html_body += f"<p>{result_json.get('conclusion', '')}</p>"
        
        newsletter.html_body = html_body
        db.commit()
        db.refresh(newsletter)
        
        return newsletter
        
    except Exception as e:
        logger.error(f"GenAI generation failed: {e}")
        db.rollback()
        raise ValueError(f"Failed to generate newsletter: {str(e)}")
