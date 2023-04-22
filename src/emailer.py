import yagmail
from dotenv import load_dotenv
import os

load_dotenv()
gmail_username = os.getenv('gmail_username')
gmail_password = os.getenv('gmail_app_password')

def send_email(content, recipient):
    yag = yagmail.SMTP(gmail_username, gmail_password)
    yag.send(recipient, 'AI Tweets', content)

def send_email_with_attachment(content, recipient, attachment):
    yag = yagmail.SMTP(gmail_username, gmail_password)
    yag.send(to=recipient, subject='AI Tweets', contents=content, attachments=[attachment])