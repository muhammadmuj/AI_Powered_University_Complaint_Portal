from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Creates user profiles for existing users that do not have one'

    def handle(self, *args, **kwargs):
        users_without_profile = []
        
        # Find users without profiles
        for user in User.objects.all():
            try:
                # Try to access the profile
                profile = user.profile
            except UserProfile.DoesNotExist:
                # If profile doesn't exist, add user to the list
                users_without_profile.append(user)
        
        # Create profiles for users without one
        for user in users_without_profile:
            UserProfile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created profile for user: {user.username}'))
        
        if not users_without_profile:
            self.stdout.write(self.style.SUCCESS('All users already have profiles'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created {len(users_without_profile)} user profiles')) 