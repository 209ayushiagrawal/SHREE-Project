from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, UniversityID, Worker, Warden, Supplier, Attendance, Inventory, LeaveRequest
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from django.db.models import F
from datetime import datetime




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

        # 2. UniversityID Record Check
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

        # 4. Create the Worker Profile (Corrected syntax)
        Worker.objects.create(
            user=new_user,
            worker_id=user_id,
            name=full_name
        )

        # 5. Mark record as used
        record.is_used = True
        record.save()

        # 6. IMPORTANT: Login the user so the session starts
        login(request, new_user)

        messages.success(request, f"Welcome {full_name}! Registration successful.")
        return redirect('worker_dashboard')

    return render(request, 'Shree1/signupWorker.html')

def warden_signup_view(request):
    if request.method == "POST":
        # 1. Variables ko theek se capture karein (HTML 'name' attribute se match hona chahiye)
        u_id = request.POST.get('user_id', '').strip()  # Iska naam u_id rakhte hain
        full_name = request.POST.get('full_name', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Basic Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'Shree1/signupWarden.html')

        # 2. UniversityID check karein
        record = UniversityID.objects.filter(
            university_id=u_id,
            role='warden',
            is_used=False
        ).first()

        if not record:
            messages.error(request, "Invalid University ID or ID already in use.")
            return render(request, 'Shree1/signupWarden.html')

        # 3. User Create Karein (Yahan dhayan dein variables par)
        new_user = User.objects.create_user(
            username=u_id,          # u_id use karein
            university_id=u_id,     # u_id use karein
            first_name=full_name,
            password=password,
            role='warden'
        )

        # 4. Warden Profile Create Karein
        Warden.objects.create(
            user=new_user,
            warden_id=u_id,         # u_id use karein
            name=full_name
        )

        # Record mark karein as used
        record.is_used = True
        record.save()

        # 5. Login and Redirect
        from django.contrib.auth import login
        login(request, new_user)
        
        messages.success(request, "Welcome, Warden!")
        return redirect('warden_dashboard')

    return render(request, 'Shree1/signupWarden.html')

def supplier_signup_view(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        error = validate_password(password, confirm_password)
        if error:
            messages.error(request, error)
            return render(request, 'Shree1/signupSupplier.html')

        record = UniversityID.objects.filter(
            university_id=user_id,
            role='supplier',
            is_used=False
        ).first()

        if not record or record.full_name != full_name:
            messages.error(request, "Access Denied: Invalid credentials or name mismatch.")
            return render(request, 'Shree1/signupSupplier.html')

        new_user = User.objects.create_user(
            username=user_id,
            university_id=user_id,
            first_name=full_name,
            password=password,
            role='supplier'
        )

        # NEW: Create the specific Supplier profile table entry (ER Match)
        Supplier.objects.create(
            user=new_user,
            supplier_id=user_id, 
            name=full_name     
        )

        record.is_used = True
        record.save()
        return redirect('supplier_dashboard')

    return render(request, 'Shree1/signupSupplier.html')

# -------------------------------
# 4. DASHBOARDS & FEATURES
# -------------------------------


@login_required
def warden_dashboard(request):
    # 1. Warden profile fetch karenge
    try:
        warden_profile = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        return redirect('welcome_role') 

    # 2. DYNAMIC STATS (Using Master List)
    # Hum 'UniversityID' use karenge taaki signed-up + non-signed-up dono count ho ske
    worker_count = UniversityID.objects.filter(role='worker').count()

    # 3. Today's Attendance Dynamic Count
    today = timezone.now().date()
    present_today = Attendance.objects.filter(date=today, status='Present').count()
    
    # 4. Pseudo Data (Hardcoded for now)
    context = {
        'warden': warden_profile,
        'worker_count': worker_count,      # Real count from Master List
        'present_count': present_today,    # Real count from Attendance Table
        'pending_leaves': 3,               # Placeholder pseudo value for now
        'low_stock_count': 5,              # Placeholder
        'tasks_completed': 12,             # Placeholder
    }
    return render(request, 'Shree1/dashboardWarden.html', context)


@login_required
def attendance_view(request):
    try:
        warden = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        return redirect('welcome_role')

    # role='worker' filter 
    master_list = UniversityID.objects.filter(role='worker')

    if request.method == "POST":
        date_str = request.POST.get('attendance_date')
        for person in master_list:
            # HTML form se status fetch karein
            status = request.POST.get(f'status_{person.university_id}')
            if status:
                Attendance.objects.update_or_create(
                    # Humne model mein isse worker_master banaya hai
                    worker_master=person, 
                    date=date_str,
                    defaults={'status': status, 'warden': warden}
                )
        return redirect('attendance')

    context = {
        'workers': master_list, # Template ke liye name 'workers' hi rakhein
        'today': timezone.now().date().strftime('%Y-%m-%d'),
        'warden': warden
    }
    return render(request, 'Shree1/warden_attendance.html', context)


@login_required
def worker_dashboard(request):
    try:
        # 1. Pehle logged-in user ki Worker profile nikalte hain
        worker_profile = Worker.objects.get(user=request.user)
        
        # 2. Worker profile se uski 'worker_id' uthate hain (Jo University ID hai)
        # Aur Master Table (UniversityID) se uska pura record match karte hain
        master_record = UniversityID.objects.get(university_id=worker_profile.worker_id)

    except (Worker.DoesNotExist, UniversityID.DoesNotExist):
        # Agar worker profile nahi milti toh logout ya error page par bhej dein
        return redirect('welcome_role')

    # 3. DYNAMIC DATA: Attendance Table se records nikalna
    # Hum 'worker_master' field use kar rahe hain jo seedha UniversityID se linked hai
    attendance_list = Attendance.objects.filter(
        worker_master=master_record
    ).order_by('-date')[:5] # Latest 5 records

    # Kitne din Present raha (Total Count)
    total_present = Attendance.objects.filter(
        worker_master=master_record, 
        status='Present'
    ).count()

    context = {
        'username': master_record.full_name, # Master List wala real name
        'role': 'Worker',
        'attendance_list': attendance_list,
        'total_present': total_present,
        'salary': '15,000', # Pseudo (Isse baad mein Attendance se link karenge)
        'leave_balance': '5', # Pseudo
        'notifications_count': '3', # Pseudo
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


def worker_profile(request):
    return render(request, 'Shree1/workerProfile.html')

def supplier_profile(request):
    return render(request, 'Shree1/suppierProfile.html')


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




@login_required
def warden_leave_view(request):
    try:
        current_warden = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        messages.error(request, "Warden profile not found.")
        return redirect('login')

    if request.method == "POST":
        w_id = request.POST.get('worker_id')
        l_type = request.POST.get('leave_type')
        s_date = request.POST.get('start_date')
        e_date = request.POST.get('end_date')
        l_reason = request.POST.get('reason', '')

        # Debugging prints
        print(f"DEBUG: w_id={w_id}, l_type={l_type}, s_date={s_date}")

        if w_id and l_type and s_date and e_date:
            try:
                LeaveRequest.objects.create(
                    worker_id=w_id, # worker_id is the PK of Worker model
                    warden=current_warden,
                    leave_type=l_type,
                    start_date=s_date,
                    end_date=e_date,
                    reason=l_reason,
                    status='Pending'
                )
                messages.success(request, "Leave request submitted to Admin!")
                return redirect('warden_leave')
            except Exception as e:
                print(f"DB Error: {e}")
                messages.error(request, f"Error: {e}")
        else:
            messages.error(request, "Validation Failed: All fields are required.")

    # Data for frontend
    workers = Worker.objects.all()
    pending = LeaveRequest.objects.filter(warden=current_warden, status='Pending')
    history = LeaveRequest.objects.filter(warden=current_warden).exclude(status='Pending').order_by('-created_at')

    return render(request, 'Shree1/warden_leave.html', {
        'workers': workers, 
        'pending': pending, 
        'history': history, 
        'warden': current_warden
    })

@login_required
def warden_profile(request):
    # Logged-in Warden ki profile nikalna
    try:
        warden = Warden.objects.get(user=request.user)
    except Warden.DoesNotExist:
        return redirect('welcome_role')

    if request.method == "POST":
        # Form se data uthana
        new_name = request.POST.get('full_name')
        new_phone = request.POST.get('phone')
        new_address = request.POST.get('address')
        new_email = request.POST.get('email')

        # Database mein update karna
        warden.name = new_name
        warden.phone = new_phone
        # Agar aapne address field model mein banayi hai
        if hasattr(warden, 'address'):
            warden.address = new_address
        
        warden.save()

        # Email user table mein hoti hai
        user = request.user
        user.email = new_email
        user.save()

        return redirect('warden_profile')

    return render(request, 'Shree1/warden_profile.html', {'warden': warden})

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


# Admin view ya action mein ye logic dalna hai
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

@login_required
def admin_user_management(request):
    # Registered Profiles
    wardens = Warden.objects.all()
    workers = Worker.objects.all()
    
    # Authorized IDs (Jo abhi signup ke liye pending hain)
    auth_ids = UniversityID.objects.all().order_by('-id') # Saari IDs dekhne ke liye

    return render(request, 'Shree1/admin_user_management.html', {
        'wardens': wardens,
        'workers': workers,
        'auth_ids': auth_ids # Ise template mein use karenge
    })

def add_university_id(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        uni_id = request.POST.get('uni_id')
        role = request.POST.get('role')
        
        UniversityID.objects.create(
            university_id=uni_id,
            full_name=full_name,
            role=role
        )
        messages.success(request, f"ID {uni_id} authorized for {role} role.")
    return redirect('admin_user_management')

def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    # Reset university ID status
    UniversityID.objects.filter(university_id=user.university_id).update(is_used=False)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('admin_user_management')