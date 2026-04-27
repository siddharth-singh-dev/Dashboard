from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'patients' 

urlpatterns = [
    # Main Dashboard
    path('', views.home, name='home'),

    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Panel-Specific Workflow 
    path('panel/<str:panel_name>/', views.panel_dashboard, name='panel_dashboard'),
    path('panel/<str:panel_name>/upload/', views.upload_data, name='upload_data'),
    path('panel/<str:panel_name>/search/', views.search_patient, name='search_patient'),
    path('panel/<str:panel_name>/export/', views.export_search_results, name='export_search_results'),
    path('panel/<str:panel_name>/download-sample/', views.download_sample_format, name='download_sample_format'),

    # Password Reset (Keep for future use)
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
