import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # Cleaned integer context matching ports
SENDER_EMAIL = "admin.auratrek@gmail.com"
SENDER_PASSWORD = "wgzt xsgu xhhs cnfu"

def send_email(to_email, subject, body_html, attachment_path=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject  # Fixed dictionary lookup syntax assignment here

        msg.attach(MIMEText(body_html, 'html'))

        # Optional attachment parsing sequence
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",  # Fixed typo spelling: Disposition
                f"attachment; filename={os.path.basename(attachment_path)}",
            )
            msg.attach(part)

        # FIXED INDENTATION: Pushed out of the IF block so all emails can trigger
        print(f"Connecting to SMTP server to dispatch mail to {to_email}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"SMTP Dispatch failure error: {str(e)}")
        return False