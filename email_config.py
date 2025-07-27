# Email Configuration Settings
# Replace these values with your actual email credentials

# For Gmail SMTP
EMAIL_CONFIG = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'your-email@gmail.com',  # Replace with your Gmail
    'EMAIL_HOST_PASSWORD': 'your-app-password',  # Replace with your Gmail app password
    'DEFAULT_FROM_EMAIL': 'noreply@university-complaints.com',
}

# For Development/Testing (Console Backend)
EMAIL_CONFIG_DEV = {
    'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
    'DEFAULT_FROM_EMAIL': 'noreply@university-complaints.com',
}

# For Outlook/Hotmail SMTP
EMAIL_CONFIG_OUTLOOK = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp-mail.outlook.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'your-email@outlook.com',  # Replace with your Outlook
    'EMAIL_HOST_PASSWORD': 'your-password',  # Replace with your password
    'DEFAULT_FROM_EMAIL': 'noreply@university-complaints.com',
}

# Instructions for Gmail App Password:
# 1. Go to your Google Account settings
# 2. Enable 2-Step Verification if not already enabled
# 3. Go to Security > App passwords
# 4. Generate a new app password for "Mail"
# 5. Use that password in EMAIL_HOST_PASSWORD 