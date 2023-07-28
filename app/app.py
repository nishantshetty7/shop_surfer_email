import os
import time
import boto3
from dotenv import load_dotenv
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')
SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL')
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

# Initialize the SQS client using environment variables
sqs = boto3.client('sqs', aws_access_key_id=AWS_ACCESS_KEY_ID,
                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                   region_name=AWS_REGION)

def send_mail(data):
    # Set up the SMTP server
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    message = MIMEMultipart()
    recipient_email = data.get("recipient_email")

    message['From'] = SENDER_EMAIL
    message['To'] = data.get("recipient_email")
    message['Subject'] = 'Activate Your Account'
    html_content = data.get("html_content")
    message.attach(MIMEText(html_content, 'html'))

    try:
        # Establish a secure connection with the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        # Log in to the sender's email account
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # Send the email
        server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())

        # Close the connection
        server.quit()
        print("Verification email sent successfully!")
        return True
    except smtplib.SMTPException as e:
        print("Error: Unable to send email.")
        print(e)
        return False

def listen_for_emails():
    print("EMAIL CONSUMER LISTENING...")
    try:
        while True:
            response = sqs.receive_message(
                QueueUrl=SQS_QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20
            )

            for message in response.get('Messages', []):

                email_data = json.loads(message['Body'])
                email_body = json.loads(email_data["Message"])
                print("EMAIL BODY: ", email_body)
                result = send_mail(email_body)

                if result:
                    sqs.delete_message(
                        QueueUrl=SQS_QUEUE_URL,
                        ReceiptHandle=message['ReceiptHandle']
                    )

            time.sleep(1)
    except Exception as e:
        print(str(e))
        return str(e), 500

if __name__ == '__main__':
    listen_for_emails()