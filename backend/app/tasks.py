from app.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.qualify_lead_async")
def qualify_lead_async(lead_id: str, org_id: str):
    logger.info(f"Qualifying lead {lead_id} for org {org_id}")

@celery_app.task(name="app.tasks.check_overdue_tasks")
def check_overdue_tasks():
    logger.info("Checking overdue tasks...")

@celery_app.task(name="app.tasks.send_notification_email")
def send_notification_email(user_email: str, subject: str, body: str):
    logger.info(f"Sending email to {user_email}: {subject}")
