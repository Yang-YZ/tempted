import os
from dotenv import load_dotenv

load_dotenv()

# Email Configuration
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', '')  # Bot email address
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')  # Gmail App Password
IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Scheduler Configuration
# Set to minutes (60 = 1 hour)
EMAIL_CHECK_INTERVAL_MINUTES = int(os.getenv('EMAIL_CHECK_INTERVAL_MINUTES', '60'))  # Default: 1 hour

# Flask Configuration
FLASK_HOST = '0.0.0.0'
FLASK_PORT = int(os.getenv('PORT', 5000))  # Render uses PORT env var
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'  # Default False for production

