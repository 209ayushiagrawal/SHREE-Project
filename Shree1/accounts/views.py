from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .models import User, UniversityID, Worker, Warden, Supplier, Attendance, Inventory, LeaveRequest
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from django.db.models import F
from datetime import datetime, date
from django.db import transaction
from django.contrib import messages
import re

     

def login_selection(request):
    return render(request, 'Shree1/login_role.html')


# -------------------------------
# 1. NAVIGATION PAGES
# -------------------------------
def welcome_role(request):
    return render(request, 'Shree1/home.html')

def login_selection(request):
    return render(request, 'Shree1/login_role.html')

def role_selection(request):
    return render(request, 'Shree1/signup_role.html')


# -------------------------------
# 2. PASSWORD CONSTRAINTS (HELPER)
# -------------------------------
def validate_password(password, confirm_password):
    if password != confirm_password:
        return "Passwords do not match."

    if len(password) < 5:
        return "Password must be at least 5 characters long."

    return None

# -------------------------------
# 3. SIGNUP LOGIC (UPDATED)
# -------------------------------

def worker_signup_view(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 1. Password Validation
        error = validate_password(password, confirm_password)
        if error:
            messages.error(request, error)
            return render(request, 'Shree1/signupWorker.html')

        # 2. UniversityID Check (Check if authorized and unused)
        record = UniversityID.objects.filter(
            university_id=user_id,
            role='worker',
            is_used=False
        ).first()

        if not record or record.full_name != full_name:
            messages.error(request, "Access Denied: Invalid credentials or name mismatch.")
            return render(request, 'Shree1/signupWorker.html')

        # 3. Create the central User
        new_user = User.objects.create_user(
            username=user_id,
            university_id=user_id,
            first_name=full_name,
            password=password,
            role='worker'
        )

        # 4. !!! UPDATED: Link to EXISTING Worker Profile !!!
        try:
            worker_profile = Worker.objects.get(worker_id=user_id)
            worker_profile.user = new_user
            worker_profile.save()
        except Worker.DoesNotExist:
            # Fallback agar Admin ne pre-fill nahi kiya tha
            Worker.objects.create(user=new_user, worker_id=user_id, name=full_name)

        # 5. Mark record as used
        record.is_used = True
        record.save()

        # 6. Login the user
        login(request, new_user)
        messages.success(request, f"Welcome {full_name}!")
        return redirect('worker_dashboard')

    return render(request, 'Shree1/signupWorker.html')


def warden_signup_view(request):
    if request.method == "POST":
        # 1. Variables capture karein
        u_id = request.POST.get('user_id', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 2. Password Validation
        error = validate_password(password, confirm_password)
        if error:
            messages.error(request, error)
            return render(request, 'Shree1/signupWarden.html')

        # 3. UniversityID Check (Check if authorized and not yet used)
        record = UniversityID.objects.filter(
            university_id=u_id,
            role='warden',
            is_used=False
        ).first()

        if not record:
            messages.error(request, "Invalid ID or Account already exists.")
            return render(request, 'Shree1/signupWarden.html')

        # 4. Central User Create Karein
        new_user = User.objects.create_user(
            username=u_id,
            university_id=u_id,
            first_name=full_name,
            password=password,
            role='warden'
        )

        # 5. !!! CRITICAL CHANGE: Link to EXISTING Profile !!!
        # Naya create karne ke bajaye existing profile ko update karein
        try:
            warden_profile = Warden.objects.get(warden_id=u_id)
            warden_profile.user = new_user  # Auth user link kar diya
            warden_profile.save()
        except Warden.DoesNotExist:
            # Backup: Agar Admin ne profile nahi banayi thi, toh yahan bana dein
            Warden.objects.create(user=new_user, warden_id=u_id, name=full_name)

        # 6. Mark ID as used
        record.is_used = True
        record.save()

        # 7. Login and Redirect
        login(request, new_user)
        messages.success(request, f"Welcome Warden {full_name}!")
        return redirect('warden_dashboard')

    return render(request, 'Shree1/signupWarden.html')

def supplier_signup_view(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 1. Password Validation
        error = validate_password(password, confirm_password)
        if error:
            messages.error(request, error)
            return render(request, 'Shree1/signupSupplier.html')

        # 2. UniversityID Check
        record = UniversityID.objects.filter(
            university_id=user_id,
            role='supplier',
            is_used=False
        ).first()

        if not record or record.full_name != full_name:
            messages.error(request, "Access Denied: Invalid ID or name mismatch.")
            return render(request, 'Shree1/signupSupplier.html')

        # 3. Create central User
        new_user = User.objects.create_user(
            username=user_id,
            university_id=user_id,
            first_name=full_name,
            password=password,
            role='supplier'
        )

        # 4. !!! UPDATED: Link to EXISTING Supplier Profile !!!
        try:
            supplier_profile = Supplier.objects.get(supplier_id=user_id)
            supplier_profile.user = new_user
            supplier_profile.save()
        except Supplier.DoesNotExist:
            Supplier.objects.create(user=new_user, supplier_id=user_id, name=full_name)

        # 5. Mark used and Login
        record.is_used = True
        record.save()
        login(request, new_user)
        
        messages.success(request, f"Welcome {full_name}!")
        return redirect('supplier_dashboard')

    return render(request, 'Shree1/signupSupplier.html')


# -------------------------------
# 5. ADMIN ACTIONS (MANAGEMENT)
# -------------------------------

@login_required
def add_university_id(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        uni_id = request.POST.get('uni_id')
        role = request.POST.get('role')
        UniversityID.objects.create(university_id=uni_id, full_name=full_name, role=role)
        messages.success(request, f"ID {uni_id} authorized.")
    return redirect('admin_user_management')

@login_required
def delete_uni_id(request, pk):
    record = get_object_or_404(UniversityID, id=pk)
    record.delete()
    messages.success(request, "Record removed.")
    return redirect('admin_user_management')

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    UniversityID.objects.filter(university_id=user.university_id).update(is_used=False)
    user.delete()
    messages.success(request, "User deleted.")
    return redirect('admin_user_management')

# -------------------------------
# 4. DASHBOARDS & FEATURES
# -------------------------------


@login_required(login_url='warden_login')
def warden_dashboard(request):
    try:
        warden = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        return redirect('warden_login')

    # Data Fetching
    worker_count = Worker.objects.count()
    
    # Sirf Pending requests fetch karein (Dashboard ke liye top 3)
    pending_requests = LeaveRequest.objects.filter(status='Pending').order_by('-created_at')[:3]
    pending_count = LeaveRequest.objects.filter(status='Pending').count()

    # Low Stock Logic (Agar current stock 50% se kam hai)
    # Note: Aapke Model mein 'Inventory' table honi chahiye
    low_stock_items = []
    # Static fallback agar model abhi ready nahi hai, warna niche wala logic use karein:
    # low_stock_items = Inventory.objects.filter(current_stock__lt=F('required_stock')*0.5)

    return render(request, 'Shree1/dashboardWarden.html', {
        'warden': warden,
        'worker_count': worker_count,
        'pending_requests': pending_requests,
        'pending_count': pending_count,
        'low_stock_items': [
            {'name': 'Rice', 'current': 50, 'required': 100, 'percent': 50},
            {'name': 'Cooking Oil', 'current': 15, 'required': 30, 'percent': 50},
            {'name': 'Cleaning Supplies', 'current': 5, 'required': 20, 'percent': 25},
        ]
    })

@login_required
def attendance_view(request):
    try:
        warden = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        return redirect('welcome_role')

    master_list = UniversityID.objects.filter(role='worker')
    today_date = timezone.now().date()

    if request.method == "POST":
        date_str = request.POST.get('attendance_date')

        if date_str != str(today_date):
            messages.error(request, "Attendance sirf aaj ki date (Today) ke liye li ja sakti hai!")
            return redirect('attendance')

        for person in master_list:
            status = request.POST.get(f'status_{person.university_id}')

            print("Worker:", person.university_id, "Status:", status)

            if status:
                Attendance.objects.update_or_create(
                    worker_master=person,
                    date=date_str,
                    defaults={'status': status, 'warden': warden}
                )

        messages.success(request, f"Attendance for {today_date} has been saved.")
        return redirect('attendance')

    # 👇 ADD THIS BLOCK
    existing_attendance = Attendance.objects.filter(date=today_date)

    attendance_dict = {
        att.worker_master.university_id: att.status
        for att in existing_attendance
    }

    context = {
        'workers': master_list,
        'today': today_date.strftime('%Y-%m-%d'),
        'warden': warden,
        'attendance_dict': attendance_dict
    }

    return render(request, 'Shree1/warden_attendance.html', context)
@login_required
def worker_dashboard(request):
    try:
        # 1. Profile aur Master Record Linkage (Aapka Security Logic)
        worker_profile = Worker.objects.get(user=request.user)
        master_record = UniversityID.objects.get(university_id=worker_profile.worker_id)

    except (Worker.DoesNotExist, UniversityID.DoesNotExist):
        return redirect('welcome_role')

    # 2. Attendance Metrics (Aapke Friend ka Dynamic Logic)
    # Pura record fetch karna summary ke liye
    all_attendance = Attendance.objects.filter(worker_master=master_record)
    
    # Latest 5 records table mein dikhane ke liye (Aapka Filter)
    latest_attendance = all_attendance.order_by('-date')[:5]

    present_days = all_attendance.filter(status='Present').count()
    total_days = all_attendance.count()

    # 3. Dynamic Leave & Notifications (Added New Features)
    # Worker ki pending leaves count karna
    pending_leaves = LeaveRequest.objects.filter(
        worker=worker_profile, 
        status='Pending'
    ).count()

    # Leave balance (Worker profile table se real data)
    # Agar model mein leave_balance field hai toh:
    leave_balance = getattr(worker_profile, 'leave_balance', 0)

    context = {
        # Profile Data
        'worker': worker_profile,
        'master': master_record,
        'full_name': master_record.full_name,
        
        # Attendance Data
        'attendance_list': latest_attendance,
        'present_days': present_days,
        'total_days': total_days,
        
        # New Dynamic Features
        'leave_balance': leave_balance,
        'notifications_count': pending_leaves, # Pending requests ko as notification dikhayenge
        'salary': 15000, # Abhi static hai, baad mein calculation logic lagayenge
    }

    return render(request, 'Shree1/dashboardWorker.html', context)


from django.db.models import F
from django.contrib import messages

@login_required
def supplier_dashboard(request):
    # 1. Jo items Critical/Low hain aur abhi tak deliver nahi hue (Pending)
    pending_deliveries = Inventory.objects.filter(
        is_delivered=False, 
        current_stock__lt=F('required_stock')
    )
    
    # 2. Jo items Supplier ne bhej diye hain (is_delivered=True)
    sent_items = Inventory.objects.filter(is_delivered=True)

    # 3. Handle 'Mark as Delivered' button click
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        try:
            item = Inventory.objects.get(item_id=item_id)
            item.is_delivered = True  # Status True karo taaki Warden ko alert mile
            item.save()
            messages.success(request, f"{item.item_name} marked as sent to Hostel!")
        except Inventory.DoesNotExist:
            messages.error(request, "Item not found.")
        
        return redirect('supplier_dashboard')

    return render(request, 'Shree1/dashboardSupplier.html', {
        'pending': pending_deliveries,
        'sent': sent_items
    })


@login_required
def worker_profile(request):
    try:
        worker = Worker.objects.get(user=request.user)
    except Worker.DoesNotExist:
        return redirect('welcome_role')

    # -------- SAVE DATA --------
    if request.method == "POST":
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        
        if not re.match(r'^[1-9][0-9]{9}$', phone):
            messages.error(request, "Phone number must be 10 digits and cannot start with 0.")
            return redirect('worker_profile')

        # update email in User model
        request.user.email = email
        request.user.save()

        # update phone in Worker model
        worker.email = email
        worker.phone_number = phone
        worker.save()


        messages.success(request, "Profile updated successfully!")
        return redirect('worker_profile')

    # -------- DISPLAY DATA --------
    context = {
        # 🔝 RIGHT TOP HEADER
         "display_name": worker.name,   # 👈 RIYA (DB se)
    "display_role": "Worker",

        # 📝 PROFILE FORM
        "full_name": worker.name,
        "employee_id": worker.worker_id,
        "email": request.user.email,
        "phone": worker.phone_number,
        "joining_date": request.user.date_joined.strftime("%d %B %Y"),

    }

    return render(request, "Shree1/workerProfile.html", context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Supplier


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Supplier


@login_required
def supplier_profile(request):
    try:
        supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        return redirect('welcome_role')

    # -------- SAVE DATA --------
    if request.method == "POST":
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        # Save email in User table
        request.user.email = email
        request.user.save()

        # Save phone in Supplier table
        supplier.phone_number = phone
        supplier.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('supplier_profile')

    # -------- DISPLAY DATA --------
    context = {
        "display_name": supplier.name,
        "display_role": "Supplier",

        "username": supplier.name,
        "employee_id": supplier.supplier_id,
        "email": 'supplier@gmail.com',
        "phone": '9876543210',
    }

    return render(request, 'Shree1/supplier_profile.html', context)

from django.db.models import Q

@login_required
def inventory_view(request):
    # Warden ki info nikalna (Sidebar ke liye)
    try:
        warden = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        warden = None

    # Search Logic
    search_query = request.GET.get('search', '')
    if search_query:
        items = Inventory.objects.filter(item_name__icontains=search_query) | Inventory.objects.filter(item_id__icontains=search_query)
    else:
        # DATABASE SE SARE ITEMS NIKALNA
        items = Inventory.objects.all()

    # Stats Calculation (Dynamic Cards)
    total_items = items.count()
    # Critical logic: Stock < 20% of Required
    critical_count = sum(1 for i in items if i.current_stock < (i.required_stock * 0.2))
    low_count = sum(1 for i in items if i.current_stock < (i.required_stock * 0.5) and i.current_stock >= (i.required_stock * 0.2))
    good_count = total_items - critical_count - low_count

    context = {
        'items': items,
        'warden': warden,
        'total_items': total_items,
        'critical_count': critical_count,
        'low_count': low_count,
        'good_count': good_count,
        'search_query': search_query
    }
    return render(request, 'Shree1/warden_inventory.html', context)


@login_required
def update_inventory_stock(request):
    if request.method == "POST":
        items = Inventory.objects.all()
        updated = False
        
        for item in items:
            # HTML input name 'qty_{{item.item_id}}' se match kar raha hai
            qty_change = request.POST.get(f'qty_{item.item_id}')
            
            if qty_change and qty_change != '0':
                try:
                    item.current_stock += float(qty_change)
                    
                    if item.current_stock < 0:
                        item.current_stock = 0
                    
                    # --- CRITICAL LOGIC ---
                    # Jab Warden stock update kar de, toh delivery cycle khatam!
                    # Isliye is_delivered ko wapas False kar rahe hain.
                    item.is_delivered = False 
                    
                    item.save()
                    updated = True
                except ValueError:
                    continue
        
        if updated:
            messages.success(request, "Inventory updated and delivery status reset successfully!")
        else:
            messages.info(request, "No changes were made.")
            
    return redirect('inventory')

def warden_leave_view(request):
    try:
        current_warden = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        messages.error(request, "Warden profile not found.")
        return redirect('login')

    if request.method == "POST":
        action_type = request.POST.get('action_type')
        leave_type = request.POST.get('leave_type')
        start_date_val = request.POST.get('start_date')
        end_date_val = request.POST.get('end_date')
        reason = request.POST.get('reason')

        try:
            s_date = date.fromisoformat(start_date_val)
            e_date = date.fromisoformat(end_date_val)
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('warden_leave')

        if s_date < date.today():
            messages.error(request, "Pichli dates valid nahi hain.")
            return redirect('warden_leave')

        if action_type == 'self':
            LeaveRequest.objects.create(
                warden=current_warden,
                is_warden_request=True,
                leave_type=leave_type,
                start_date=s_date,
                end_date=e_date,
                reason=reason
            )
            messages.success(request, "Warden leave request created.")
        else:
            w_id = request.POST.get('worker_id') 
            try:
                # Reflection logic ensure karta hai ki UniversityID add hote hi 
                # Worker profile ban jati hai
                worker_obj = Worker.objects.get(worker_id=w_id)
                LeaveRequest.objects.create(
                    worker=worker_obj,
                    warden=current_warden,
                    is_warden_request=False,
                    leave_type=leave_type,
                    start_date=s_date, 
                    end_date=e_date,
                    reason=reason
                )
                messages.success(request, f"Request for {worker_obj.name} created.")
            except Worker.DoesNotExist:
                messages.error(request, "Worker record not found in profile table.")

        return redirect('warden_leave')

    # UPDATED: Seedha UniversityID table se workers ko filter karein
    context = {
        'workers': UniversityID.objects.filter(role='worker'), 
        'today': date.today().strftime('%Y-%m-%d'),
        'warden': current_warden,
        'pending': LeaveRequest.objects.filter(warden=current_warden, status='Pending'),
        'history': LeaveRequest.objects.filter(warden=current_warden).exclude(status='Pending')
    }
    return render(request, 'Shree1/warden_leave.html', context)





@login_required
def warden_profile(request):
    try:
        warden = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        return redirect('welcome_role')

    # -------- SAVE DATA --------
    if request.method == "POST":
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        
        if not re.match(r'^[1-9][0-9]{9}$', phone):
            messages.error(request, "Phone number must be 10 digits and cannot start with 0.")
            return redirect('warden_profile')

        # update email in User model
        request.user.email = email
        request.user.save()

        # update phone in Warden model
        warden.email = email
        warden.phone_number = phone
        warden.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('warden_profile')

    # -------- DISPLAY DATA --------
    context = {
        "display_name": warden.name,
        "display_role": "Warden",

        "full_name": warden.name,
        "email": request.user.email,
        "phone": warden.phone_number,
        "warden_id": warden.warden_id,
        "joining_date": request.user.date_joined.strftime("%d %B %Y"),
    }

    return render(request, "Shree1/warden_profile.html", context)



def admin_dashboard(request):
    # 1. Fetch Totals for the Statistic Cards
    total_wardens = Warden.objects.count()
    total_workers = Worker.objects.count()
    total_suppliers = Supplier.objects.count()
    
    # 2. Logic for Inventory Alerts (Example: items with stock < 20)
    # If you haven't created an Inventory model yet, we can pass dummy data for now
    # but the counts above are 100% dynamic.
    
    context = {
        'warden_count': total_wardens,
        'worker_count': total_workers,
        'supplier_count': total_suppliers,
        'admin_name': request.user.username, # Shows the logged-in Admin ID/Name
    }
    
    return render(request, 'Shree1/dashboardAdmin.html', context)

# -------------------------------
# 5. LOGIN PAGES (FUNCTIONAL)
# -------------------------------

def worker_login(request):
    if request.method == "POST":
        u_id = request.POST.get('worker_id')  # Matches HTML name="worker_id"
        passw = request.POST.get('password')
        user = authenticate(request, username=u_id, password=passw)
        if user and user.role == 'worker':
            login(request, user)
            return redirect('worker_dashboard')
        messages.error(request, "Invalid Worker Credentials")
    return render(request, 'Shree1/loginWorker.html')

def warden_login(request):
    if request.method == "POST":
        u_id = request.POST.get('warden_id') # Matches HTML name="warden_id"
        passw = request.POST.get('password')
        user = authenticate(request, username=u_id, password=passw)
        if user and user.role == 'warden':
            login(request, user)
            return redirect('warden_dashboard')
        messages.error(request, "Invalid Warden Credentials")
    return render(request, 'Shree1/loginWarden.html')

def supplier_login(request):
    if request.method == "POST":
        u_id = request.POST.get('supplier_id') # Matches HTML name="supplier_id"
        passw = request.POST.get('password')
        user = authenticate(request, username=u_id, password=passw)
        if user and user.role == 'supplier':
            login(request, user)
            return redirect('supplier_dashboard')
        messages.error(request, "Invalid Supplier Credentials")
    return render(request, 'Shree1/loginSupplier.html')

def admin_login(request):
    if request.method == "POST":
        u_id = request.POST.get('user_id') # Matches HTML name="user_id"
        passw = request.POST.get('password')
        user = authenticate(request, username=u_id, password=passw)
        if user and (user.role == 'admin' or user.is_staff):
            login(request, user)
            return redirect('admin_dashboard')
        messages.error(request, "Invalid Admin Credentials")
    return render(request, 'Shree1/loginAdmin.html')

def approve_leave_logic(request, leave_request_id):
    leave_req = LeaveRequest.objects.get(id=leave_request_id)
    
    if leave_req.status == 'Pending':
        # Leave days calculate karein (Start aur End date ke beech ka difference)
        delta = leave_req.end_date - leave_req.start_date
        days_requested = delta.days + 1 # +1 kyunki starting day bhi count hota hai

        worker = leave_req.worker
        
        # Check karein ki balance bacha hai ya nahi
        if worker.leave_balance >= days_requested:
            # 1. Balance deduct karein
            worker.leave_balance -= days_requested
            worker.save()
            
            # 2. Status update karein
            leave_req.status = 'Approved'
            leave_req.save()
            
            messages.success(request, f"Leave Approved! {days_requested} days deducted from {worker.name}'s balance.")
        else:
            # Agar balance kam hai
            messages.error(request, f"Insufficient Balance! {worker.name} only has {worker.leave_balance} leaves left.")
            leave_req.status = 'Rejected'
            leave_req.save()
            
    return redirect('admin_dashboard') # Ya jahan aapka admin dashboard ho

def forget_password(request):
    return render(request, 'Shree1/forget_password.html')