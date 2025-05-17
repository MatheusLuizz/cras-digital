from django.contrib import admin
from .models import SupportTicket, SupportMessage


class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0
    readonly_fields = ('sender', 'created_at')
    fields = ('sender', 'message', 'created_at')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'description', 'user__username', 'user__email')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'subject', 'description')
        }),
        ('Status', {
            'fields': ('status', 'created_at')
        }),
    )
    inlines = [SupportMessageInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ('get_ticket_subject', 'sender', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('message', 'sender__username', 'ticket__subject')
    readonly_fields = ('created_at',)

    def get_ticket_subject(self, obj):
        return obj.ticket.subject
    get_ticket_subject.short_description = 'Ticket'
    get_ticket_subject.admin_order_field = 'ticket__subject'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'ticket')
