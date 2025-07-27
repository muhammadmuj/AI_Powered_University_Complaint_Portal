from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import os

class ComplaintCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)  # For department assignment
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Complaint Categories"

class Department(models.Model):
    name = models.CharField(max_length=100)
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='department_head')
    staff = models.ManyToManyField(User, related_name='department_staff', blank=True)
    
    def __str__(self):
        return self.name

class Complaint(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    email = models.EmailField(null=True, blank=True)
    category = models.ForeignKey(ComplaintCategory, on_delete=models.CASCADE, related_name='complaints')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_special_case = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)  # Feature 4: Anonymous complaints
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_complaints')  # Feature 7: Assignment
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)  # Feature 7: Department assignment
    escalation_level = models.IntegerField(default=0)  # Feature 7: Escalation
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)  # Feature 15: Archiving
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-assign department based on category
        if not self.department and self.category.department:
            try:
                self.department = Department.objects.get(name=self.category.department)
            except Department.DoesNotExist:
                pass
        
        # Set resolved_at when status changes to resolved
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        
        super().save(*args, **kwargs)

class ComplaintAttachment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(
        upload_to='complaint_attachments/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif'])]
    )
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment for {self.complaint.title}"
    
    def save(self, *args, **kwargs):
        if not self.filename:
            self.filename = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

class ComplaintResponse(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    response_text = models.TextField()
    is_internal = models.BooleanField(default=False)  # Feature 6: Internal notes
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Response to {self.complaint.title}"

class ComplaintStatusHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, choices=Complaint.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Complaint.STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.complaint.title}: {self.old_status} → {self.new_status}"

class Feedback(models.Model):
    RATING_CHOICES = (
        (1, 'Very Dissatisfied'),
        (2, 'Dissatisfied'),
        (3, 'Neutral'),
        (4, 'Satisfied'),
        (5, 'Very Satisfied'),
    )
    
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback for {self.complaint.title} by {self.user.username}"
    
    class Meta:
        verbose_name_plural = "Feedback"

# Feature 10: FAQ & Knowledge Base
class FAQ(models.Model):
    CATEGORY_CHOICES = (
        ('general', 'General'),
        ('academic', 'Academic'),
        ('infrastructure', 'Infrastructure'),
        ('it_services', 'IT Services'),
        ('health_safety', 'Health & Safety'),
        ('other', 'Other'),
    )
    
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.question
    
    class Meta:
        verbose_name_plural = "FAQs"

# Feature 14: Notification Center
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('status_change', 'Status Change'),
        ('assignment', 'Assignment'),
        ('response', 'Response'),
        ('escalation', 'Escalation'),
        ('feedback_request', 'Feedback Request'),
        ('general', 'General'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"
    
    class Meta:
        ordering = ['-created_at']

# Feature 3: Analytics & Reporting
class ComplaintAnalytics(models.Model):
    date = models.DateField()
    total_complaints = models.IntegerField(default=0)
    resolved_complaints = models.IntegerField(default=0)
    pending_complaints = models.IntegerField(default=0)
    avg_resolution_time = models.FloatField(default=0)  # in hours
    avg_satisfaction_rating = models.FloatField(default=0)
    
    class Meta:
        verbose_name_plural = "Complaint Analytics"
        unique_together = ['date']
