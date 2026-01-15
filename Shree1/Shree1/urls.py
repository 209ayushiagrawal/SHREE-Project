# Shree1/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [


    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 🌐 Public pages
    path('', views.welcome_role, name='welcome_role'),
    path('choose-login/', views.login_selection, name='login_selection'),
    path('choose-signup/', views.role_selection, name='choose_signup'),

    # 🌍 Language
    path('i18n/', include('django.conf.urls.i18n')),

    # 👤 Accounts app (ALL auth, signup, dashboard)
    path('accounts/', include('accounts.urls')),

    # 🔐 Admin
    path('admin/', admin.site.urls),
    
    
    
    path('Shree-admin/users/', views.admin_user_management, name='admin_user_management'),

    path('Shree-admin/attendance/', views.admin_attendance, name='admin_attendance'),

   path('Shree-admin/inventory/', views.admin_inventory, name='admin_inventory'),
   
   path('Shree-admin/leave/', views.admin_leave_Management, name='admin_leave_Management'),
   
   path('Shree-admin/profile/', views.admin_profile, name='admin_profile'),
   
    path('Shree-admin/evaluation/', views.admin_employee_evaluation, name='admin_employee_evaluation'),
    
    path('Shree-admin/reports/', views.admin_reports, name='admin_reports'),
    
    path('Shree-admin/salary/', views.admin_salary, name='admin_salary'),
]

   

