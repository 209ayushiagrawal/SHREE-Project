# Shree1/views.py
from django.shortcuts import render,redirect


def welcome_role(request):
    return render(request, 'Shree1/home.html')

def login_selection(request):
    return render(request, 'Shree1/login_role.html')

def role_selection(request):
    return render(request, 'Shree1/signup_role.html')

def supplier_profile(request):
    return render(request, 'Shree1/profileSupplier.html')



def admin_user_management(request):
    return render(request, 'Shree1/admin_user_management.html')

def admin_attendance(request):
    return render(request, 'Shree1/admin_attendance.html')

def admin_inventory(request):
    return render(request, 'Shree1/admin_inventory.html')

def admin_leave_Management(request):
    return render(request, 'Shree1/admin_leave_Management.html')

def admin_profile(request):
    # You can pass real user data here if using request.user
    context = {
        'username': 'slzmdl',
        'role': 'Admin',
        'email': 'slzmdl@gmail.com',
        'phone': '+91 98765 43210',
        'employee_id': 'EMP001',
        'department': 'Kitchen',
        'joining_date': '15-01-2024',
        'address': '123 Main Street, City, State'
    }
    return render(request, 'Shree1/admin_profile.html')

def admin_employee_evaluation(request):
    # Sample data matching your screenshot
    employees = [
        {'name': 'Rajesh Kumar', 'role': 'Kitchen Staff'},
        {'name': 'Priya Sharma', 'role': 'Cleaning Staff'},
    ]
    return render(request, 'Shree1/admin_employee_evaluation.html', {'employees': employees})

def admin_reports(request):
    # Hardcoded data to match your screenshot exactly
    static_reports = [
        {
            'title': 'Attendance Report',
            'date_range': 'December 2025',
            'record_count': '1250',
            'generated_at': '2026-01-01'
        },
        {
            'title': 'Inventory Report',
            'date_range': 'December 2025',
            'record_count': '85',
            'generated_at': '2026-01-01'
        },
        {
            'title': 'Salary Report',
            'date_range': 'December 2025',
            'record_count': '45',
            'generated_at': '2026-01-01'
        }
    ]
    
    context = {
        'reports': static_reports,
        'segment': 'reports',
        'username': 'slzmdl',  # Matching your screenshot
        'role': 'Admin'
    }
    
    return render(request, 'Shree1/admin_reports.html')


def admin_salary(request):
    # Summary stats matching the screenshot
    stats = {
        'total_payroll': '74,200',
        'total_employees': '5',
        'avg_salary': '14,840',
        'total_deductions': '5,800'
    }

    # Employee list matching the screenshot
    salary_data = [
        {'name': 'Rajesh Kumar', 'role': 'Kitchen Staff', 'basic': '12,000', 'allowance': '+2,000', 'deduction': '-1,000', 'net': '13,000'},
        {'name': 'Priya Sharma', 'role': 'Cleaning Staff', 'basic': '10,000', 'allowance': '+1,500', 'deduction': '-800', 'net': '10,700'},
        {'name': 'Amit Patel', 'role': 'Warden', 'basic': '20,000', 'allowance': '+5,000', 'deduction': '-2,000', 'net': '23,000'},
        {'name': 'Sunita Devi', 'role': 'Cleaning Staff', 'basic': '10,000', 'allowance': '+1,500', 'deduction': '-500', 'net': '11,000'},
    ]

    context = {
        'stats': stats,
        'salaries': salary_data,
        'username': 'dfehr', # From your screenshot
        'role': 'Admin'
    }
    return render(request, 'Shree1/admin_salary.html', context)
