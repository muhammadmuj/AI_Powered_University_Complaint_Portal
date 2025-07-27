from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from complaints.models import Department, FAQ, ComplaintCategory
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Set up initial data for enhanced complaint portal features'

    def handle(self, *args, **options):
        self.stdout.write('Setting up enhanced complaint portal data...')
        
        # Create departments
        departments_data = [
            {
                'name': 'Information Technology',
                'description': 'Handles IT-related complaints and issues'
            },
            {
                'name': 'Facilities Management',
                'description': 'Handles infrastructure and maintenance issues'
            },
            {
                'name': 'Academic Affairs',
                'description': 'Handles academic and course-related complaints'
            },
            {
                'name': 'Student Services',
                'description': 'Handles student life and support issues'
            },
            {
                'name': 'Health & Safety',
                'description': 'Handles health, safety, and security concerns'
            },
        ]
        
        for dept_data in departments_data:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'name': dept_data['name']}
            )
            if created:
                self.stdout.write(f'Created department: {department.name}')
        
        # Update complaint categories with departments
        category_department_mapping = {
            'IT Services': 'Information Technology',
            'Infrastructure': 'Facilities Management',
            'Academic': 'Academic Affairs',
            'Library': 'Student Services',
            'Transportation': 'Facilities Management',
            'Health/Safety': 'Health & Safety',
            'Harassment': 'Student Services',
            'Accessibility': 'Student Services',
        }
        
        for category_name, department_name in category_department_mapping.items():
            try:
                category = ComplaintCategory.objects.get(name=category_name)
                department = Department.objects.get(name=department_name)
                category.department = department_name
                category.save()
                self.stdout.write(f'Updated category {category_name} with department {department_name}')
            except (ComplaintCategory.DoesNotExist, Department.DoesNotExist):
                self.stdout.write(f'Warning: Could not update category {category_name}')
        
        # Create FAQs
        faqs_data = [
            {
                'question': 'How do I submit a complaint?',
                'answer': 'You can submit a complaint by logging into your account and clicking on "Submit New Complaint". Fill out the form with details about your issue and submit.',
                'category': 'general'
            },
            {
                'question': 'How long does it take to resolve a complaint?',
                'answer': 'Resolution time varies depending on the complexity and priority of the issue. Urgent complaints are typically addressed within 24-48 hours, while standard complaints may take 3-5 business days.',
                'category': 'general'
            },
            {
                'question': 'Can I submit an anonymous complaint?',
                'answer': 'Yes, you can submit anonymous complaints by checking the "Submit Anonymously" option. However, anonymous complaints may have limited follow-up capabilities.',
                'category': 'general'
            },
            {
                'question': 'What should I do if my Wi-Fi is not working?',
                'answer': 'First, try restarting your device and router. If the issue persists, check if other devices are affected. If the problem continues, submit a complaint under the IT Services category.',
                'category': 'it_services'
            },
            {
                'question': 'How do I report a maintenance issue?',
                'answer': 'Submit a complaint under the Infrastructure category. Include the location, description of the issue, and any relevant photos if possible.',
                'category': 'infrastructure'
            },
            {
                'question': 'What if I have a grade-related concern?',
                'answer': 'Submit a complaint under the Academic category. Include course details, instructor name, and specific concerns about your grade.',
                'category': 'academic'
            },
            {
                'question': 'How do I report harassment or bullying?',
                'answer': 'Submit a complaint under the Harassment category. These complaints are treated with high priority and confidentiality. You can also submit anonymously if needed.',
                'category': 'health_safety'
            },
            {
                'question': 'Can I attach files to my complaint?',
                'answer': 'Yes, you can attach supporting documents, photos, or other relevant files when submitting a complaint. Supported formats include PDF, DOC, DOCX, JPG, PNG, and GIF.',
                'category': 'general'
            },
            {
                'question': 'How do I check the status of my complaint?',
                'answer': 'Log into your account and go to "My Complaints" to view the status of all your submitted complaints. You will also receive email notifications when the status changes.',
                'category': 'general'
            },
            {
                'question': 'What if I\'m not satisfied with the resolution?',
                'answer': 'You can provide feedback on resolved complaints. If you\'re still not satisfied, you can submit a follow-up complaint or escalate the issue through the appropriate department.',
                'category': 'general'
            },
        ]
        
        for faq_data in faqs_data:
            faq, created = FAQ.objects.get_or_create(
                question=faq_data['question'],
                defaults={
                    'answer': faq_data['answer'],
                    'category': faq_data['category'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created FAQ: {faq.question[:50]}...')
        
        self.stdout.write(self.style.SUCCESS('Successfully set up enhanced complaint portal data!')) 