import os
import smtplib

# Load the .env file (if using python-dotenv)
from dotenv import load_dotenv
load_dotenv()  # Make sure to install python-dotenv first: pip install python-dotenv

# Retrieve email settings from environment variables
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))  # Use default port 587 if not specified
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')

# Print retrieved values for verification
print("Email settings:")
print("- Host:", EMAIL_HOST)
print("- Port:", EMAIL_PORT)
print("- User:", EMAIL_HOST_USER)
print("- Password:", EMAIL_HOST_PASSWORD)  # Avoid printing sensitive information in production
print("- Recipient:", RECIPIENT_EMAIL)

# Create a message to send
message = f"This is a test email from Python using environment variables.\nSent at: {datetime.datetime.now()}"

# Connect to the email server
try:
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()  # Enable secure connection
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.sendmail(EMAIL_HOST_USER, RECIPIENT_EMAIL, message)
        print("Email sent successfully!")
except smtplib.SMTPException as e:
    print("Error sending email:", e)