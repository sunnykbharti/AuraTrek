import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SENDER_EMAIL = "admin.auratrek@gmail.com"
SENDER_PASSWORD = "wgzt xsgu xhhs cnfu"

def send_email(to_email, subject, body_html, attachment_path=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['subject']

        msg.attach(MIMEText(body_html, 'html'))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Dispoistion",
                f"attachment; filename={os.path.basename(attachment_path)}",
            )
            msg.attach(part)

            # establishing connections

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
            server.quit()
            return True
        
    except Exception as e:
        print(f"SMTP Dispatch failure error: {str(e)}")
        return False
