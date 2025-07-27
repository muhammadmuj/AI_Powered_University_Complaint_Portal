from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Complaint, ComplaintCategory, ComplaintResponse, Feedback, Department, FAQ, ComplaintAttachment, ComplaintStatusHistory, Notification
from .forms import ComplaintForm, ComplaintResponseForm, ComplaintStatusForm, FeedbackForm, ComplaintAttachmentForm, InternalResponseForm, ComplaintAssignmentForm, ComplaintSearchForm, ComplaintArchiveForm
import joblib
import os
from django.conf import settings
from django.core.mail import send_mail
from accounts.models import is_department_staff

# Load ML models and encoders once
CATEGORY_MODEL_PATH = os.path.join(settings.BASE_DIR, 'category_svm_model.joblib')
CATEGORY_ENCODER_PATH = os.path.join(settings.BASE_DIR, 'category_encoder.joblib')
PRIORITY_MODEL_PATH = os.path.join(settings.BASE_DIR, 'priority_lr_model.joblib')
PRIORITY_ENCODER_PATH = os.path.join(settings.BASE_DIR, 'priority_encoder.joblib')

category_clf = joblib.load(CATEGORY_MODEL_PATH)
category_encoder = joblib.load(CATEGORY_ENCODER_PATH)
priority_clf = joblib.load(PRIORITY_MODEL_PATH)
priority_encoder = joblib.load(PRIORITY_ENCODER_PATH)

# Helper function to check if user is admin
def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
def complaint_list(request):
    form = ComplaintSearchForm(request.GET or None)
    
    # Filter complaints based on user role
    if is_admin(request.user) or (hasattr(request.user, 'profile') and request.user.profile.user_type == 'teacher'):
        # Admins and teachers can see all complaints
        complaints = Complaint.objects.all().select_related('category', 'user')
    else:
        # Students see only their own complaints
        complaints = Complaint.objects.filter(user=request.user).select_related('category', 'user')

    if form.is_valid():
        # Keyword search
        search_query = form.cleaned_data.get('search_query')
        search_field = form.cleaned_data.get('search_field')
        if search_query:
            if search_field == 'title':
                complaints = complaints.filter(title__icontains=search_query)
            elif search_field == 'description':
                complaints = complaints.filter(description__icontains=search_query)
            elif search_field == 'user':
                complaints = complaints.filter(user__username__icontains=search_query)
            elif search_field == 'category':
                complaints = complaints.filter(category__name__icontains=search_query)
            else:
                complaints = complaints.filter(
                    Q(title__icontains=search_query) |
                    Q(description__icontains=search_query)
                )
        # Status filter
        status = form.cleaned_data.get('status')
        if status:
            complaints = complaints.filter(status=status)
        # Priority filter
        priority = form.cleaned_data.get('priority')
        if priority:
            complaints = complaints.filter(priority=priority)
        # Category filter
        category = form.cleaned_data.get('category')
        if category:
            complaints = complaints.filter(category=category)
        # Date range filter
        date_from = form.cleaned_data.get('date_from')
        if date_from:
            complaints = complaints.filter(created_at__date__gte=date_from)
        date_to = form.cleaned_data.get('date_to')
        if date_to:
            complaints = complaints.filter(created_at__date__lte=date_to)
        # Anonymous filter
        is_anonymous = form.cleaned_data.get('is_anonymous')
        if is_anonymous:
            complaints = complaints.filter(is_anonymous=True)
        # Archived filter
        is_archived = form.cleaned_data.get('is_archived')
        if is_archived:
            complaints = complaints.filter(is_archived=True)
        else:
            # By default, exclude archived complaints unless explicitly requested
            complaints = complaints.filter(is_archived=False)
    else:
        # By default, exclude archived complaints
        complaints = complaints.filter(is_archived=False)

    complaints = complaints.order_by('-created_at')
    return render(request, 'complaints/complaint_list.html', {
        'complaints': complaints,
        'form': form,
    })

@login_required
def complaint_create(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        attachment_form = ComplaintAttachmentForm(request.POST, request.FILES)
        
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            # Assign complaint to user's department
            complaint.department = request.user.profile.department

            # Handle anonymous complaints
            if complaint.is_anonymous:
                # For anonymous complaints, we still need to track the user internally
                # but we'll display "Anonymous" in the UI
                complaint.user = request.user  # Keep the user for internal tracking
                # Don't send email notifications for anonymous complaints
                send_email = False
            else:
                send_email = True

            # ML Model Prediction
            text = f"{complaint.title} {complaint.description}"
            # Predict category
            cat_pred = category_clf.predict([text])[0]
            cat_label = category_encoder.inverse_transform([cat_pred])[0]
            # Predict priority
            prio_pred = priority_clf.predict([text])[0]
            prio_label = priority_encoder.inverse_transform([prio_pred])[0]

            # Set predicted values
            # Find or create the category object
            category_obj, _ = ComplaintCategory.objects.get_or_create(name=cat_label)
            complaint.category = category_obj
            complaint.priority = prio_label.lower()

            # Special case logic
            if cat_label.lower() == 'harassment' or prio_label.lower() == 'urgent':
                complaint.is_special_case = True
            else:
                complaint.is_special_case = False

            complaint.save()

            # Handle file attachments
            if attachment_form.is_valid() and request.FILES:
                for uploaded_file in request.FILES.getlist('file'):
                    attachment = ComplaintAttachment(
                        complaint=complaint,
                        file=uploaded_file,
                        filename=uploaded_file.name
                    )
                    attachment.save()

            # Send confirmation email only for non-anonymous complaints
            if send_email and complaint.email:
                send_mail(
                    subject='Complaint Submitted - University Complaint Portal',
                    message=f'Thank you for submitting your complaint.\n\nTitle: {complaint.title}\nDescription: {complaint.description}\n\nWe will notify you when your complaint is resolved.',
                    from_email=None,
                    recipient_list=[complaint.email],
                    fail_silently=True,
                )

            messages.success(request, f'Your complaint has been submitted. (Predicted category: {cat_label}, priority: {prio_label})')
            return redirect('complaint_detail', pk=complaint.pk)
    else:
        form = ComplaintForm()
        attachment_form = ComplaintAttachmentForm()
    
    return render(request, 'complaints/complaint_form.html', {
        'form': form,
        'attachment_form': attachment_form,
        'title': 'Submit New Complaint'
    })

@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    
    # Check if user has permission to view this complaint
    if not is_admin(request.user) and request.user != complaint.user:
        messages.error(request, "You don't have permission to view this complaint.")
        return redirect('complaint_list')
    
    responses = complaint.responses.filter(is_internal=False).order_by('created_at')
    internal_notes = complaint.responses.filter(is_internal=True).order_by('created_at')
    
    # Check if feedback exists for this complaint
    feedback = None
    if hasattr(complaint, 'feedback'):
        feedback = complaint.feedback
    
    # Store old status for resolution email
    old_status = complaint.status
    
    # Handle form submissions
    if request.method == 'POST':
        response_form = ComplaintResponseForm(request.POST)
        internal_form = InternalResponseForm(request.POST)
        status_form = ComplaintStatusForm(request.POST, instance=complaint)
        feedback_form = FeedbackForm(request.POST)
        
        # Process public response form
        if 'submit_response' in request.POST and response_form.is_valid():
            response = response_form.save(commit=False)
            response.complaint = complaint
            response.responder = request.user
            response.is_internal = False
            response.save()
            
            # Create notification for new response (only if not the complainant)
            if request.user != complaint.user:
                create_notification(
                    user=complaint.user,
                    notification_type='response',
                    title='New Response to Your Complaint',
                    message=f'There is a new response to your complaint "{complaint.title}".',
                    complaint=complaint
                )
            
            messages.success(request, 'Your response has been added.')
            return redirect('complaint_detail', pk=pk)
            
        # Process internal notes form (staff only)
        if 'submit_internal' in request.POST and is_admin(request.user) and internal_form.is_valid():
            internal_note = internal_form.save(commit=False)
            internal_note.complaint = complaint
            internal_note.responder = request.user
            internal_note.is_internal = True
            internal_note.save()
            messages.success(request, 'Internal note has been added.')
            return redirect('complaint_detail', pk=pk)
            
        # Process status form (staff only)
        if 'update_status' in request.POST and is_admin(request.user) and status_form.is_valid():
            old_status = complaint.status
            new_status = status_form.cleaned_data['status']
            status_form.save()
            
            # Create status history entry if status changed
            if old_status != new_status:
                ComplaintStatusHistory.objects.create(
                    complaint=complaint,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=request.user,
                    notes=f"Status changed from {old_status} to {new_status}"
                )
                
                # Create notification for status change
                create_notification(
                    user=complaint.user,
                    notification_type='status_change',
                    title=f'Complaint Status Updated',
                    message=f'Your complaint "{complaint.title}" status has been changed from {complaint.get_status_display()} to {status_form.cleaned_data["status"]}.',
                    complaint=complaint
                )
            
            # Send resolution email if status changed to resolved
            if old_status != 'resolved' and status_form.cleaned_data['status'] == 'resolved' and complaint.email and not complaint.is_anonymous:
                send_mail(
                    subject='Your Complaint Has Been Resolved',
                    message=f'Your complaint titled "{complaint.title}" has been marked as resolved.\n\nThank you for using the University Complaint Portal.',
                    from_email=None,
                    recipient_list=[complaint.email],
                    fail_silently=True,
                )
                
                # Create feedback request notification
                create_notification(
                    user=complaint.user,
                    notification_type='feedback_request',
                    title='Feedback Request',
                    message=f'Your complaint "{complaint.title}" has been resolved. Please provide feedback on your experience.',
                    complaint=complaint
                )
            
            messages.success(request, 'Complaint status has been updated.')
            return redirect('complaint_detail', pk=pk)
            
        # Process feedback form (only for resolved complaints by the original user)
        if 'submit_feedback' in request.POST and complaint.status == 'resolved' and request.user == complaint.user and not feedback and feedback_form.is_valid():
            feedback = feedback_form.save(commit=False)
            feedback.complaint = complaint
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('complaint_detail', pk=pk)
    else:
        response_form = ComplaintResponseForm()
        internal_form = InternalResponseForm()
        status_form = ComplaintStatusForm(instance=complaint)
        feedback_form = FeedbackForm()
    
    return render(request, 'complaints/complaint_detail.html', {
        'complaint': complaint,
        'responses': responses,
        'internal_notes': internal_notes,
        'response_form': response_form,
        'internal_form': internal_form,
        'status_form': status_form,
        'feedback_form': feedback_form,
        'feedback': feedback,
    })

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """
    Admin dashboard - only accessible to staff and superusers
    """
    complaints = Complaint.objects.filter(is_archived=False).order_by('-is_special_case', '-created_at')
    pending_count = complaints.filter(status='pending').count()
    in_progress_count = complaints.filter(status='in_progress').count()
    resolved_count = complaints.filter(status='resolved').count()
    rejected_count = complaints.filter(status='rejected').count()
    
    # Feedback statistics
    resolved_complaints = complaints.filter(status='resolved')
    feedback_count = resolved_complaints.filter(feedback__isnull=False).count()
    feedback_pending_count = resolved_complaints.filter(feedback__isnull=True).count()
    
    recent_complaints = complaints[:5]  # Get 5 most recent complaints
    
    return render(request, 'complaints/dashboard.html', {
        'recent_complaints': recent_complaints,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'rejected_count': rejected_count,
        'feedback_count': feedback_count,
        'feedback_pending_count': feedback_pending_count,
    })

@login_required
def user_home(request):
    """
    Home page for regular users
    """
    # Get user's complaints (excluding archived)
    complaints = Complaint.objects.filter(user=request.user, is_archived=False).order_by('-created_at')
    pending_count = complaints.filter(status='pending').count()
    in_progress_count = complaints.filter(status='in_progress').count()
    resolved_count = complaints.filter(status='resolved').count()
    rejected_count = complaints.filter(status='rejected').count()
    
    # Feedback statistics for user's resolved complaints
    resolved_complaints = complaints.filter(status='resolved')
    feedback_count = resolved_complaints.filter(feedback__isnull=False).count()
    feedback_pending_count = resolved_complaints.filter(feedback__isnull=True).count()
    
    recent_complaints = complaints[:5]  # Get 5 most recent complaints
    
    return render(request, 'complaints/user_home.html', {
        'recent_complaints': recent_complaints,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'rejected_count': rejected_count,
        'feedback_count': feedback_count,
        'feedback_pending_count': feedback_pending_count,
    })

@login_required
@user_passes_test(is_department_staff)
def department_dashboard(request):
    department = request.user.profile.department
    complaints = Complaint.objects.filter(department__name=department, is_archived=False)
    return render(request, 'complaints/department_dashboard.html', {
        'complaints': complaints,
        'department': department,
    })

@login_required
@user_passes_test(is_admin)
def analytics_dashboard(request):
    """Analytics dashboard for admins with charts and statistics"""
    
    # Date range for analytics (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Basic statistics (excluding archived complaints)
    total_complaints = Complaint.objects.filter(is_archived=False).count()
    resolved_complaints = Complaint.objects.filter(status='resolved', is_archived=False).count()
    pending_complaints = Complaint.objects.filter(status__in=['pending', 'in_progress'], is_archived=False).count()
    urgent_complaints = Complaint.objects.filter(priority='urgent', is_archived=False).count()
    
    # Resolution rate
    resolution_rate = (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0
    
    # Average satisfaction rating
    avg_satisfaction = Feedback.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    # Complaints by category (for pie chart)
    category_stats = Complaint.objects.filter(is_archived=False).values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Complaints by status (for bar chart)
    status_stats = Complaint.objects.filter(is_archived=False).values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Daily complaints trend (for line chart)
    daily_complaints = []
    for i in range(30):
        date = end_date - timedelta(days=i)
        count = Complaint.objects.filter(
            created_at__date=date.date(),
            is_archived=False
        ).count()
        daily_complaints.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    daily_complaints.reverse()
    
    # Department performance
    department_stats = Department.objects.annotate(
        total_complaints=Count('complaints', filter=Q(complaints__is_archived=False)),
        resolved_complaints=Count('complaints', filter=Q(complaints__status='resolved', complaints__is_archived=False)),
        avg_resolution_time=Avg('complaints__resolved_at' - 'complaints__created_at', filter=Q(complaints__is_archived=False))
    )
    
    # Priority distribution
    priority_stats = Complaint.objects.filter(is_archived=False).values('priority').annotate(
        count=Count('id')
    ).order_by('priority')
    
    # Recent activity
    recent_complaints = Complaint.objects.filter(is_archived=False).order_by('-created_at')[:10]
    recent_responses = ComplaintResponse.objects.order_by('-created_at')[:10]
    
    context = {
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
        'urgent_complaints': urgent_complaints,
        'resolution_rate': round(resolution_rate, 1),
        'avg_satisfaction': round(avg_satisfaction, 1),
        'category_stats': list(category_stats),
        'status_stats': list(status_stats),
        'daily_complaints': daily_complaints,
        'department_stats': department_stats,
        'priority_stats': list(priority_stats),
        'recent_complaints': recent_complaints,
        'recent_responses': recent_responses,
    }
    
    return render(request, 'complaints/analytics_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def assign_complaint(request, pk):
    """Assign a complaint to a staff member or department"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        form = ComplaintAssignmentForm(request.POST, instance=complaint)
        if form.is_valid():
            complaint = form.save()
            
            # Create status history entry
            ComplaintStatusHistory.objects.create(
                complaint=complaint,
                old_status=complaint.status,
                new_status='assigned',
                changed_by=request.user,
                notes=f"Complaint assigned to {complaint.assigned_to.username if complaint.assigned_to else 'department'}"
            )
            
            # Update status to assigned
            complaint.status = 'assigned'
            complaint.save()
            
            messages.success(request, f'Complaint assigned successfully.')
            return redirect('complaint_detail', pk=pk)
    else:
        form = ComplaintAssignmentForm(instance=complaint)
    
    return render(request, 'complaints/assign_complaint.html', {
        'form': form,
        'complaint': complaint
    })

@login_required
@user_passes_test(is_admin)
def escalate_complaint(request, pk):
    """Escalate a complaint to higher priority"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        # Increase escalation level
        complaint.escalation_level += 1
        
        # Update priority based on escalation
        if complaint.escalation_level == 1:
            complaint.priority = 'high'
        elif complaint.escalation_level >= 2:
            complaint.priority = 'urgent'
        
        complaint.save()
        
        # Create status history entry
        ComplaintStatusHistory.objects.create(
            complaint=complaint,
            old_status=complaint.status,
            new_status=complaint.status,
            changed_by=request.user,
            notes=f"Complaint escalated to level {complaint.escalation_level} (Priority: {complaint.get_priority_display()})"
        )
        
        messages.success(request, f'Complaint escalated to level {complaint.escalation_level}.')
        return redirect('complaint_detail', pk=pk)
    
    return render(request, 'complaints/escalate_complaint.html', {
        'complaint': complaint
    })

@login_required
def faq_list(request):
    query = request.GET.get('q', '')
    faqs = FAQ.objects.filter(is_active=True)
    if query:
        faqs = faqs.filter(Q(question__icontains=query) | Q(answer__icontains=query))
    # Group by category
    categories = {}
    for faq in faqs.order_by('category', 'question'):
        categories.setdefault(faq.get_category_display(), []).append(faq)
    return render(request, 'complaints/faq_list.html', {
        'categories': categories,
        'query': query,
    })

@login_required
def notification_list(request):
    """Display all notifications for the current user"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'complaints/notification_list.html', {
        'notifications': notifications,
    })

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notification_list')

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notification_list')

def create_notification(user, notification_type, title, message, complaint=None):
    """Helper function to create notifications"""
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        complaint=complaint
    )

@login_required
@user_passes_test(is_admin)
def archive_complaint(request, pk):
    """Archive a resolved complaint"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        form = ComplaintArchiveForm(request.POST)
        if form.is_valid():
            complaint.is_archived = True
            complaint.save()
            
            # Create status history entry
            ComplaintStatusHistory.objects.create(
                complaint=complaint,
                old_status=complaint.status,
                new_status=complaint.status,
                changed_by=request.user,
                notes=f"Complaint archived. Reason: {form.cleaned_data.get('archive_reason', 'No reason provided')}"
            )
            
            messages.success(request, 'Complaint has been archived successfully.')
            return redirect('complaint_detail', pk=pk)
    else:
        form = ComplaintArchiveForm()
    
    return render(request, 'complaints/archive_complaint.html', {
        'form': form,
        'complaint': complaint
    })

@login_required
@user_passes_test(is_admin)
def archived_complaints(request):
    """View all archived complaints"""
    complaints = Complaint.objects.filter(is_archived=True).order_by('-created_at')
    return render(request, 'complaints/archived_complaints.html', {
        'complaints': complaints
    })

@login_required
@user_passes_test(is_admin)
def unarchive_complaint(request, pk):
    """Unarchive a complaint"""
    complaint = get_object_or_404(Complaint, pk=pk, is_archived=True)
    complaint.is_archived = False
    complaint.save()
    
    # Create status history entry
    ComplaintStatusHistory.objects.create(
        complaint=complaint,
        old_status=complaint.status,
        new_status=complaint.status,
        changed_by=request.user,
        notes="Complaint unarchived"
    )
    
    messages.success(request, 'Complaint has been unarchived successfully.')
    return redirect('archived_complaints')

@login_required
def complaint_history(request, pk):
    """View detailed history of a complaint"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    # Check if user has permission to view this complaint
    if not is_admin(request.user) and request.user != complaint.user:
        messages.error(request, "You don't have permission to view this complaint.")
        return redirect('complaint_list')
    
    # Get all status history entries
    status_history = complaint.status_history.all().order_by('-changed_at')
    
    return render(request, 'complaints/complaint_history.html', {
        'complaint': complaint,
        'status_history': status_history
    })
