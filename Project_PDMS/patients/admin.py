from django.contrib import admin
from .models import ECHS, CGHS, CAPF

@admin.register(ECHS)
class ECHSAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ECHS model.
    """
    list_display = [
        'id', 
        'card_number', 
        'patient_name', 
        'relation', 
        'admission_date', 
        'discharge_date', 
        'claim_id', 
        'hospital_name', 
        'io', 
        'claim_amount', 
        'stay', 
        'ailment'
    ]
    search_fields = ['card_number', 'patient_name']
    list_filter = ['admission_date', 'discharge_date']  
    ordering = ['-admission_date']  
    class Media:
        """
        Link the custom CSS file for wrapping text in the admin panel.
        """
        css = {
            'all': ('css/admin.css',)  
        }

@admin.register(CGHS)
class CGHSAdmin(admin.ModelAdmin):
    """
    Admin configuration for the CGHS model.
    """
    list_display = [
        'id', 
        'card_number', 
        'case_id', 
        'patient_name', 
        'hospital_name', 
        'registered_date', 
        'claim_amount', 
        'procedure', 
        'admission_date', 
        'intimation_raised_date'
    ]
    search_fields = ['card_number', 'patient_name', 'case_id']
    list_filter = ['registered_date', 'admission_date']
    ordering = ['-admission_date']

    class Media:
        """
        Link the custom CSS file for wrapping text in the admin panel.
        """
        css = {
            'all': ('css/admin.css',)  
        }

@admin.register(CAPF)
class CAPFAdmin(admin.ModelAdmin):
    """
    Admin configuration for the CAPF model.
    """
    list_display = [
        'id', 
        'card_number', 
        'case_id', 
        'patient_name', 
        'hospital_name', 
        'registered_date', 
        'claim_amount', 
        'procedure', 
        'admission_date', 
        'intimation_raised_date'
    ]
    search_fields = ['card_number', 'patient_name', 'case_id']
    list_filter = ['registered_date', 'admission_date']
    ordering = ['-admission_date']

    class Media:
        """
        Link the custom CSS file for wrapping text in the admin panel.
        """
        css = {
            'all': ('css/admin.css',)  
        }
