import feedparser
import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.content_item import ContentItem
from app.schemas.content_item import ContentItemCreate

logger = logging.getLogger(__name__)

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse RSS date string to datetime object."""
    from email.utils import parsedate_to_datetime
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return datetime.utcnow()

def fetch_rss_feed(feed_url: str, source_name: str, db: Session) -> int:
    """
    Fetch an RSS feed, parse it, and save new items to the database.
    Returns the number of new items added.
    """
    logger.info(f"Fetching RSS feed: {feed_url}")
    
    feed = feedparser.parse(feed_url)
    if feed.bozo:
        logger.error(f"Error parsing feed {feed_url}: {feed.bozo_exception}")
        return 0
        
    items_added = 0
    
    for entry in feed.entries:
        # Extract fields
        title = getattr(entry, 'title', 'No Title')
        link = getattr(entry, 'link', '')
        if not link:
            continue
            
        summary = ''
        if hasattr(entry, 'summary'):
            summary = entry.summary
        elif hasattr(entry, 'description'):
            summary = entry.description
            
        # Strip HTML from summary if necessary (simplified for MVP)
        import re
        if summary:
            summary = re.sub(r'<[^>]+>', '', summary)
            # Truncate summary
            if len(summary) > 500:
                summary = summary[:497] + '...'
                
        tags = []
        if hasattr(entry, 'tags'):
            tags = [t.term for t in entry.tags]
            
        # Check if already exists
        existing = db.query(ContentItem).filter(ContentItem.url == link).first()
        if existing:
            continue
            
        new_item = ContentItem(
            type='rss',
            title=title,
            summary=summary,
            url=link,
            source=source_name,
            tags=tags
        )
        
        try:
            db.add(new_item)
            db.commit()
            items_added += 1
        except IntegrityError:
            db.rollback()
            logger.warning(f"Integrity error adding {link}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding item: {str(e)}")
            
    return items_added
