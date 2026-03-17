import os
import jinja2
from datetime import datetime
from typing import Dict, Any

from app.models.newsletter import Newsletter

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')

def get_template_env() -> jinja2.Environment:
    """Initialize Jinja2 environment for email templates."""
    loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    env = jinja2.Environment(loader=loader, autoescape=jinja2.select_autoescape(['html', 'xml']))
    return env

def render_newsletter_html(newsletter: Newsletter, base_url: str = "http://localhost:3000") -> str:
    """
    Render a final HTML newsletter using the master template.
    Usually we inject the `newsletter.html_body` into a larger master template.
    """
    env = get_template_env()
    try:
        template = env.get_template('newsletter_master.html')
    except jinja2.exceptions.TemplateNotFound:
        # Fallback if file doesn't exist yet
        return newsletter.html_body or "<h1>Empty Newsletter</h1>"

    context: Dict[str, Any] = {
        "title": newsletter.title,
        "content_body": newsletter.html_body,
        "date": datetime.utcnow().strftime("%B %d, %Y"),
        "base_url": base_url,
        "unsubscribe_link": f"{base_url}/unsubscribe"
    }

    return template.render(**context)

def render_confirmation_email(token: str, base_url: str = "http://localhost:3000") -> str:
    """Render the double opt-in confirmation email."""
    env = get_template_env()
    try:
        template = env.get_template('confirm_email.html')
    except jinja2.exceptions.TemplateNotFound:
        # Fallback
        confirm_url = f"{base_url}/api/v1/public/confirm-subscription?token={token}"
        return f"<h1>Confirm your subscription</h1><p>Click <a href='{confirm_url}'>here</a> to confirm.</p>"

    confirm_url = f"{base_url}/api/v1/public/confirm-subscription?token={token}"
    context: Dict[str, Any] = {
        "confirm_url": confirm_url,
        "base_url": base_url
    }

    return template.render(**context)
