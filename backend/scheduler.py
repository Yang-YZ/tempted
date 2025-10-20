from apscheduler.schedulers.background import BackgroundScheduler
from email_service import check_new_emails, send_email
from ai_service import generate_response
from models import User, Message
from config import EMAIL_CHECK_INTERVAL_MINUTES


def process_emails():
    """Process new emails from registered users and send AI responses."""
    print("\n=== Starting email check ===")

    # Get all registered user emails
    registered_emails = User.get_all_emails()

    if not registered_emails:
        print("No registered users yet")
        return

    print(f"Checking emails for {len(registered_emails)} registered users")

    # Check for new emails
    new_emails = check_new_emails(registered_emails)

    if not new_emails:
        print("No new emails from registered users")
        return

    print(f"Found {len(new_emails)} new email(s)")

    # Process each email
    for email_data in new_emails:
        user_email = email_data['from']
        user_message = email_data['body']

        print(f"\nProcessing email from {user_email}")

        # Get user data
        user = User.get(user_email)
        if not user:
            print(f"User {user_email} not found in database")
            continue

        # Store user message
        Message.create(user_email, 'user', user_message)

        # Get conversation history for context
        history = Message.get_recent_for_context(user_email, limit=10)

        # Generate AI response
        ai_response = generate_response(
            user_name=user['name'],
            user_context=user['context'],
            conversation_history=history,
            user_message=user_message
        )

        # Store bot response
        Message.create(user_email, 'bot', ai_response)

        # Send email reply
        subject = f"Re: {email_data['subject']}" if email_data['subject'] else "Your Support Partner"
        send_email(user_email, subject, ai_response)

        print(f"Response sent to {user_email}")

    print("=== Email check completed ===\n")


def start_scheduler():
    """Start the background scheduler for email checking."""
    scheduler = BackgroundScheduler()

    # Schedule email checking at configured interval
    scheduler.add_job(
        func=process_emails,
        trigger='interval',
        minutes=EMAIL_CHECK_INTERVAL_MINUTES,
        id='email_check_job',
        name='Check and process emails',
        replace_existing=True
    )

    # Also run immediately on startup for testing
    scheduler.add_job(
        func=process_emails,
        trigger='date',
        id='startup_check',
        name='Initial email check'
    )

    scheduler.start()

    print(f"Scheduler started - checking emails every {EMAIL_CHECK_INTERVAL_MINUTES} minute(s)")

    return scheduler

