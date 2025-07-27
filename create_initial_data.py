from django.core.management.base import BaseCommand
from complaints.models import ComplaintCategory

class Command(BaseCommand):
    help = 'Creates initial complaint categories'

    def handle(self, *args, **kwargs):
        categories = [
            {
                'name': 'Academic Issues',
                'description': 'Issues related to courses, professors, grading, etc.'
            },
            {
                'name': 'Administrative Issues',
                'description': 'Issues related to university administration, registration, etc.'
            },
            {
                'name': 'Facilities',
                'description': 'Issues related to campus facilities, buildings, classrooms, etc.'
            },
            {
                'name': 'Harassment',
                'description': 'Reports of harassment, discrimination, or bullying'
            },
            {
                'name': 'Technology',
                'description': 'Issues related to university technology, wifi, computers, etc.'
            },
            {
                'name': 'Other',
                'description': 'Other issues not covered by the above categories'
            },
        ]

        for category_data in categories:
            ComplaintCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully created initial complaint categories')) 