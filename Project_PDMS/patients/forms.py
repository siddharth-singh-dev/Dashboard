from django import forms
from .models import PatientClinicalHistory

# Form for Patient Clinical History
class PatientClinicalHistoryForm(forms.ModelForm):
    class Meta:
        model = PatientClinicalHistory
        fields = [
            'card_number', 
            'patient_name', 
            'relation', 
            'admit_date', 
            'discharge_date', 
            'claim_id', 
            'hospital_name', 
            'io', 
            'claim_amount', 
            'stay', 
            'ailment'
        ]
        widgets = {
            'card_number': forms.TextInput(attrs={'class': 'form-control'}),
            'patient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'relation': forms.TextInput(attrs={'class': 'form-control'}),
            'admit_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'discharge_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'claim_id': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-control'}),
            'io': forms.TextInput(attrs={'class': 'form-control'}),
            'claim_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'stay': forms.NumberInput(attrs={'class': 'form-control'}),
            'ailment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    # Validate card number to ensure it only contains digits
    def clean_card_number(self):
        card_number = self.cleaned_data['card_number']
        if not card_number.isdigit():
            raise forms.ValidationError("Card number must contain only digits.")
        return card_number

    # Cross-field validation for dates
    def clean(self):
        cleaned_data = super().clean()
        admit_date = cleaned_data.get('admit_date')
        discharge_date = cleaned_data.get('discharge_date')
        if admit_date and discharge_date and admit_date > discharge_date:
            raise forms.ValidationError("Admit date cannot be after discharge date.")
        return cleaned_data


# Login Form 
class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
