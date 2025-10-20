import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from typing import List, Dict
from config import (
    EMAIL_ADDRESS, EMAIL_PASSWORD,
    IMAP_SERVER, SMTP_SERVER, SMTP_PORT
)


def decode_email_subject(subject):
    """Decode email subject."""
    decoded = decode_header(subject)
    subject_parts = []
    for content, encoding in decoded:
        if isinstance(content, bytes):
            subject_parts.append(content.decode(encoding or 'utf-8'))
        else:
            subject_parts.append(content)
    return ''.join(subject_parts)


def get_email_body(msg):
    """Extract email body from message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    body = part.get_payload(decode=True).decode()
                    break
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode()
        except:
            pass
    
    return body.strip()


def check_new_emails(registered_emails: List[str]) -> List[Dict]:
    """
    Check for new emails from registered users.
    
    Args:
        registered_emails: List of registered user email addresses
    
    Returns:
        List of dicts with 'from', 'subject', 'body'
    """
    new_emails = []
    
    try:
        print(f"[DEBUG] Registered emails: {registered_emails}")

        # Connect to Gmail IMAP
        print(f"[DEBUG] Connecting to {IMAP_SERVER} as {EMAIL_ADDRESS}")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select('inbox')
        print("[DEBUG] Successfully connected to inbox")

        # Search for unread emails
        status, messages = mail.search(None, 'UNSEEN')

        if status != 'OK':
            print("[DEBUG] Search status not OK")
            return new_emails

        email_ids = messages[0].split()
        print(f"[DEBUG] Found {len(email_ids)} unread email(s)")

        for email_id in email_ids:
            try:
                # Fetch email
                status, msg_data = mail.fetch(email_id, '(RFC822)')

                if status != 'OK':
                    print(f"[DEBUG] Failed to fetch email {email_id}")
                    continue

                # Parse email
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Get sender
                from_header = msg.get('From')
                print(f"[DEBUG] Email {email_id} - From header: {from_header}")

                # Extract email address from "Name <email@domain.com>" format
                if '<' in from_header and '>' in from_header:
                    sender_email = from_header.split('<')[1].split('>')[0].strip()
                else:
                    sender_email = from_header.strip()

                print(f"[DEBUG] Extracted sender email: {sender_email}")

                # Check if sender is registered
                is_registered = sender_email.lower() in [e.lower() for e in registered_emails]
                print(f"[DEBUG] Is registered? {is_registered}")

                if is_registered:
                    subject = decode_email_subject(msg.get('Subject', ''))
                    body = get_email_body(msg)

                    print(f"[DEBUG] Subject: {subject}")
                    print(f"[DEBUG] Body length: {len(body) if body else 0}")

                    if body:  # Only process if we got a body
                        new_emails.append({
                            'from': sender_email.lower(),
                            'subject': subject,
                            'body': body
                        })
                        print(f"✓ New email from {sender_email}: {subject}")
                    else:
                        print(f"[DEBUG] Email has no body, skipping")
                else:
                    print(f"[DEBUG] Sender {sender_email} not in registered list")

                # Mark as read (optional - you can remove this to keep emails unread)
                # mail.store(email_id, '+FLAGS', '\\Seen')

            except Exception as e:
                print(f"[ERROR] Error processing email {email_id}: {e}")
                import traceback
                traceback.print_exc()
                continue

        mail.close()
        mail.logout()

    except Exception as e:
        print(f"Error checking emails: {e}")

    return new_emails


def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send email reply.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
        server.quit()

        print(f"Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
        return False

