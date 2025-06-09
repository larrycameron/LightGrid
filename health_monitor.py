import logging
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)

# Email alert configuration (customize as needed)
ALERT_EMAIL_FROM = 'alert@example.com'
ALERT_EMAIL_TO = 'admin@example.com'
ALERT_EMAIL_SUBJECT = 'RoadMesh System Alert'
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
SMTP_USER = 'alert@example.com'
SMTP_PASS = 'yourpassword'

class HealthMonitor:
    def __init__(self, battery, lighting, mesh, user_service):
        self.battery = battery
        self.lighting = lighting
        self.mesh = mesh
        self.user_service = user_service

    def check_and_alert(self):
        issues = []
        if not self.battery.health_check():
            issues.append('Battery subsystem')
        if not self.lighting.health_check():
            issues.append('Lighting subsystem')
        if not self.mesh.health_check():
            issues.append('Mesh network')
        if not self.user_service.health_check():
            issues.append('User service')
        if issues:
            msg = f"ALERT: The following subsystems have issues: {', '.join(issues)}"
            logger.error(msg)
            self.send_email_alert(msg)
        else:
            logger.info('All subsystems healthy')

    def send_email_alert(self, message):
        try:
            msg = EmailMessage()
            msg['Subject'] = ALERT_EMAIL_SUBJECT
            msg['From'] = ALERT_EMAIL_FROM
            msg['To'] = ALERT_EMAIL_TO
            msg.set_content(message)
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            logger.info('Alert email sent')
        except Exception as e:
            logger.error(f'Failed to send alert email: {e}') 