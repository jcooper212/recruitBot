from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
#import smtplib
import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


# Define scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def create_message_with_attachment(sender, to, subject, message_text, file_path):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    # Attach the file
    attachment = MIMEBase('application', 'octet-stream')
    with open(file_path, 'rb') as file:
        attachment.set_payload(file.read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
    message.attach(attachment)

    raw_message = base64.urlsafe_b64encode(message.as_bytes())
    raw_message = raw_message.decode()
    return {'raw': raw_message}

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except Exception as e:
        print('An error occurred: %s' % e)
        return None

def send_email_with_attachment(sender_email, attachment_path, subject, body):
    # Authenticate using OAuth2 credentials
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Build the Gmail service
    service = build('gmail', 'v1', credentials=creds)

    # Create the message with attachment
    message = create_message_with_attachment(sender_email, sender_email, subject, body, attachment_path)

    # Send the email
    response = send_message(service, 'me', message)
    if response:
        return response['status']
    else:
        return 'Failed to send email'



# Example usage:
# sender_email = 'your_email@gmail.com'
# attachment_path = 'path/to/your/attachment.pdf'
# subject = 'Test Email with Attachment'
# body = 'This is a test email with an attachment.'
# status = send_email_with_attachment(sender_email, attachment_path, subject, body)
# print('Email sending status:', status)
