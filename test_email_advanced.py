import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_complaint_portal.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_configuration():
    """Test the current email configuration"""
    print("=" * 60)
    print("EMAIL NOTIFICATION SYSTEM DIAGNOSTIC")
    print("=" * 60)
    
    # Display current configuration
    print(f"\n📧 Current Email Configuration:")
    print(f"   Backend: {settings.EMAIL_BACKEND}")
    print(f"   Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"   Port: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"   TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    print(f"   User: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    print(f"   From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    # Test email sending
    print(f"\n🧪 Testing Email Sending...")
    try:
        result = send_mail(
            subject='🔧 Email System Test - University Complaint Portal',
            message='''
This is a test email to verify the email notification system is working properly.

✅ If you receive this email, the system is working correctly!
✅ Complaint notifications will be sent to users.
✅ Resolution emails will be sent when complaints are resolved.

Best regards,
University Complaint Portal Team
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],
            fail_silently=False,
        )
        
        if result == 1:
            print("✅ SUCCESS: Email sent successfully!")
            if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
                print("⚠️  NOTE: Using console backend - emails are printed to console only")
                print("   To send actual emails, configure SMTP settings in settings.py")
            else:
                print("✅ NOTE: Using SMTP backend - emails should be delivered to recipients")
        else:
            print("❌ FAILED: Email sending returned unexpected result")
            
    except Exception as e:
        print(f"❌ ERROR: Email sending failed")
        print(f"   Error: {e}")
        print(f"   Type: {type(e).__name__}")
        
        # Provide specific guidance based on error type
        if "Authentication" in str(e):
            print("\n🔧 SOLUTION: Authentication error detected")
            print("   - Check your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")
            print("   - For Gmail, use an App Password instead of regular password")
            print("   - Enable 2-Step Verification in your Google Account")
        elif "Connection" in str(e):
            print("\n🔧 SOLUTION: Connection error detected")
            print("   - Check your EMAIL_HOST and EMAIL_PORT settings")
            print("   - Verify your internet connection")
            print("   - Check if your email provider allows SMTP access")
    
    print("\n" + "=" * 60)

def show_configuration_options():
    """Show different configuration options"""
    print("\n📋 EMAIL CONFIGURATION OPTIONS:")
    print("=" * 60)
    
    print("\n1️⃣  Gmail SMTP (Recommended for development):")
    print("   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'")
    print("   EMAIL_HOST = 'smtp.gmail.com'")
    print("   EMAIL_PORT = 587")
    print("   EMAIL_USE_TLS = True")
    print("   EMAIL_HOST_USER = 'your-email@gmail.com'")
    print("   EMAIL_HOST_PASSWORD = 'your-app-password'")
    
    print("\n2️⃣  Outlook/Hotmail SMTP:")
    print("   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'")
    print("   EMAIL_HOST = 'smtp-mail.outlook.com'")
    print("   EMAIL_PORT = 587")
    print("   EMAIL_USE_TLS = True")
    print("   EMAIL_HOST_USER = 'your-email@outlook.com'")
    print("   EMAIL_HOST_PASSWORD = 'your-password'")
    
    print("\n3️⃣  Console Backend (Development only):")
    print("   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'")
    print("   # Emails are printed to console only")
    
    print("\n4️⃣  File Backend (Development only):")
    print("   EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'")
    print("   EMAIL_FILE_PATH = '/tmp/app-messages'")
    print("   # Emails are saved to files")

if __name__ == "__main__":
    test_email_configuration()
    show_configuration_options() 