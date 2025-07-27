import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_complaint_portal.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("Testing email functionality...")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

try:
    # Test email sending
    result = send_mail(
        subject='Test Email - University Complaint Portal',
        message='This is a test email to verify the email notification system is working.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['test@example.com'],
        fail_silently=False,
    )
    print(f"Email sent successfully! Result: {result}")
except Exception as e:
    print(f"Email sending failed: {e}")
    print(f"Error type: {type(e).__name__}") 