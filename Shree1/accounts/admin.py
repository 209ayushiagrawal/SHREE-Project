from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UniversityID, Worker, Warden, Supplier, Attendance, Inventory, LeaveRequest

# Register Custom User model
admin.site.register(User, UserAdmin)

# Register University ID verification table
admin.site.register(UniversityID)

admin.site.register(Worker)
admin.site.register(Warden)
admin.site.register(Supplier)


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('worker_master', 'date', 'status', 'warden') # Columns to show
    list_filter = ('date', 'status', 'warden') # Sidebar filters
    search_fields = ('worker_master__full_name', 'worker_master__university_id') # Search bar

admin.site.register(Attendance, AttendanceAdmin)

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    # Admin panel par jo columns aap dekhna chahte hain
    list_display = ('item_id', 'item_name', 'current_stock', 'required_stock', 'unit')
    # Search karne ke liye fields
    search_fields = ('item_id', 'item_name')



@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    # Admin panel ki table mein kaunse columns dikhen
    list_display = ('worker', 'leave_type', 'start_date', 'end_date', 'status', 'warden')
    
    # Side mein filter lagane ke liye
    list_filter = ('status', 'leave_type', 'start_date')
    
    # Search bar ke liye
    search_fields = ('worker__name', 'warden__name')

    # Status badalne ke liye custom actions
    actions = ['approve_leave', 'reject_leave']

    def approve_leave(self, request, queryset):
        queryset.update(status='Approved')
    approve_leave.short_description = "Mark selected requests as Approved"

    def reject_leave(self, request, queryset):
        queryset.update(status='Rejected')
    reject_leave.short_description = "Mark selected requests as Rejected"