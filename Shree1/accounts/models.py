from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# -------------------------
# CUSTOM USER MODEL (The central Authentication table)
# -------------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('warden', 'Warden'),
        ('worker', 'Worker'),
        ('supplier', 'Supplier'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=10)
    university_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


# -------------------------
# PRE-STORED UNIVERSITY IDS (Validation Layer)
# -------------------------
class UniversityID(models.Model):
    university_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.university_id} - {self.full_name} ({self.role})"


# -------------------------
# PROFILE TABLES (Matches your ER Diagram & DB Specs)
# -------------------------

class Warden(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    warden_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=20)
    admin_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_wardens')
    def __str__(self):
        return f"{self.name} ({self.warden_id})"

class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    worker_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=20)
    # The Admin field stays nullable so they can signup themselves
    admin_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_workers')
    # Use this to 'assign' them to the system
    is_approved = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name} ({self.worker_id})"

class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    supplier_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=20)
    contact = models.CharField(max_length=150)
    address = models.CharField(max_length=100, null=True)
    def __str__(self):
        return f"{self.name} ({self.supplier_id})"




class Attendance(models.Model):
    STATUS_CHOICES = [('Present', 'Present'),
                      ('Absent', 'Absent'),
                      ('Leave', 'Leave') ]
    
    # ForeignKey ab 'UniversityID' table se connect hogi (Master List)
    # Taaki bina signup kiye bhi attendance lag sake
    worker_master = models.ForeignKey(UniversityID, on_delete=models.CASCADE)
    warden = models.ForeignKey(Warden, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        # Ek University ID ki ek din mein ek hi attendance
        unique_together = ('worker_master', 'date') 

    def __str__(self):
        
        return f"{self.worker_master.full_name} - {self.date} - {self.status}"
    
class Inventory(models.Model):
    item_id = models.CharField(max_length=20, unique=True, primary_key=True) # Unique ID
    item_name = models.CharField(max_length=100)
    current_stock = models.FloatField(default=0.0)
    required_stock = models.FloatField(default=0.0)
    unit = models.CharField(max_length=10, default='kg') # kg, L, pcs
    
    # Supplier tracking ke liye (AI ke bina manual logic)
    is_delivered = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.item_id} - {self.item_name}"
    
class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    warden = models.ForeignKey(Warden, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.worker.name} - {self.status}"