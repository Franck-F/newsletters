import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import logging

from app.config import get_settings
from app.models.newsletter import Newsletter
from app.services.template_engine import render_newsletter_html, render_confirmation_email

logger = logging.getLogger(__name__)
settings = get_settings()

def get_brevo_client():
    if not settings.brevo_api_key:
        logger.warning("Brevo API key not set")
        return None
        
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.brevo_api_key
    return sib_api_v3_sdk.ApiClient(configuration)

def send_confirmation_email(to_email: str, token: str) -> bool:
    """Send double opt-in confirmation email via Brevo."""
    api_client = get_brevo_client()
    if not api_client:
        return False
        
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(api_client)
    
    html_content = render_confirmation_email(token)
    
    sender = {"name": settings.brevo_sender_name, "email": settings.brevo_sender_email}
    to = [{"email": to_email}]
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=html_content,
        sender=sender,
        subject="Confirm your newsletter subscription"
    )
    
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"Confirmation email sent to {to_email}. Message ID: {api_response.message_id}")
        return True
    except ApiException as e:
        logger.error(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")
        return False

def send_newsletter_campaign(newsletter: Newsletter, list_ids: list[int] = [2]) -> bool:
    """
    Create and send a Brevo campaign for a newsletter.
    (Assumes list_id 2 is the main subscriber list for this MVP).
    """
    api_client = get_brevo_client()
    if not api_client:
        return False
        
    api_instance = sib_api_v3_sdk.EmailCampaignsApi(api_client)
    
    html_content = render_newsletter_html(newsletter)
    sender = {"name": settings.brevo_sender_name, "email": settings.brevo_sender_email}
    
    email_campaign = sib_api_v3_sdk.CreateEmailCampaign(
        name=newsletter.title,
        subject=newsletter.title,
        sender=sender,
        html_content=html_content,
        recipients={"listIds": list_ids},
        inline_image_activation=False,
        mirror_active=True,
    )
    
    try:
        # 1. Create campaign
        create_campaign_response = api_instance.create_email_campaign(email_campaign)
        campaign_id = create_campaign_response.id
        logger.info(f"Campaign created with ID: {campaign_id}")
        
        # 2. Send campaign immediately
        api_instance.send_email_campaign_now(campaign_id)
        logger.info(f"Campaign {campaign_id} sending initiated.")
        return True
    except ApiException as e:
        logger.error(f"Exception when calling EmailCampaignsApi for newsletter {newsletter.id}: {e}")
        return False
