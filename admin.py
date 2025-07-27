from django.contrib import admin
from .models import (
    ComplaintCategory, Complaint, ComplaintResponse, Feedback, 
    Department, ComplaintAttachment, ComplaintStatusHistory, 
    FAQ, Notification, ComplaintAnalytics
)

class ComplaintResponseInline(admin.TabularInline):
    model = ComplaintResponse
    extra = 0
    readonly_fields = ('created_at',)

class ComplaintAttachmentInline(admin.TabularInline):
    model = ComplaintAttachment
    extra = 0
    readonly_fields = ('uploaded_at',)

class ComplaintStatusHistoryInline(admin.TabularInline):
    model = ComplaintStatusHistory
    extra = 0
    readonly_fields = ('changed_at',)

@admin.register(ComplaintCategory)
class ComplaintCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'description')
    search_fields = ('name', 'department')
    list_filter = ('department',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'head', 'staff_count')
    search_fields = ('name',)
    filter_horizontal = ('staff',)
    
    def staff_count(self, obj):
        return obj.staff.count()
    staff_count.short_description = 'Staff Count'

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'user', 'status', 'priority', 'assigned_to', 'department', 'created_at', 'is_anonymous', 'is_archived')
    list_filter = ('status', 'category', 'priority', 'department', 'is_anonymous', 'is_archived', 'created_at')
    search_fields = ('title', 'description', 'user__username', 'assigned_to__username')
    readonly_fields = ('created_at', 'updated_at', 'resolved_at', 'escalation_level')
    inlines = [ComplaintResponseInline, ComplaintAttachmentInline, ComplaintStatusHistoryInline]
    list_editable = ('status', 'priority', 'assigned_to')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'user', 'email', 'is_anonymous')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'is_special_case')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'department', 'escalation_level')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
        ('Archive', {
            'fields': ('is_archived',),
            'classes': ('collapse',)
        }),
    )

@admin.register(ComplaintResponse)
class ComplaintResponseAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'responder', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at', 'responder')
    search_fields = ('response_text', 'complaint__title', 'responder__username')
    readonly_fields = ('created_at',)

@admin.register(ComplaintAttachment)
class ComplaintAttachmentAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'filename', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('filename', 'complaint__title')
    readonly_fields = ('uploaded_at',)

@admin.register(ComplaintStatusHistory)
class ComplaintStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('old_status', 'new_status', 'changed_at', 'changed_by')
    search_fields = ('complaint__title', 'changed_by__username')
    readonly_fields = ('changed_at',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('complaint__title', 'user__username', 'comment')
    readonly_fields = ('created_at',)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('question', 'answer')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)

@admin.register(ComplaintAnalytics)
class ComplaintAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_complaints', 'resolved_complaints', 'pending_complaints', 'avg_resolution_time', 'avg_satisfaction_rating')
    list_filter = ('date',)
    readonly_fields = ('date', 'total_complaints', 'resolved_complaints', 'pending_complaints', 'avg_resolution_time', 'avg_satisfaction_rating')
    ordering = ('-date',)
