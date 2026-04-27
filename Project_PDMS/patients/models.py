from django.db import models

class ECHS(models.Model):
    card_number = models.CharField(max_length=50, db_index=True)
    service_number = models.CharField(max_length=50, db_index=True, default='Not Set')
    patient_name = models.CharField(max_length=100, db_index=True)
    relation = models.CharField(max_length=50, blank=True, null=True)
    admission_date = models.DateField(blank=True, null=True, verbose_name="Admission Date")  # Unified
    discharge_date = models.DateField(blank=True, null=True, verbose_name="Discharge Date")
    claim_id = models.CharField(max_length=50, blank=True, null=True)
    hospital_name = models.CharField(max_length=100, blank=True, null=True)
    io = models.CharField(max_length=50, blank=True, null=True)
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stay = models.IntegerField(blank=True, null=True)
    ailment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient_name} - {self.card_number}"


class CGHS(models.Model):
    card_number = models.CharField(max_length=50, db_index=True)
    family_id = models.CharField(max_length=50, db_index=True, default='Not Set')
    case_id = models.CharField(max_length=50, blank=True, null=True)
    patient_name = models.CharField(max_length=100, db_index=True)
    hospital_name = models.CharField(max_length=100, blank=True, null=True)
    registered_date = models.DateField(blank=True, null=True)
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    procedure = models.TextField(blank=True, null=True)
    admission_date = models.DateField(blank=True, null=True, verbose_name="Admission Date")  # Unified
    intimation_raised_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient_name} - {self.card_number}"


class CAPF(models.Model):
    card_number = models.CharField(max_length=50, db_index=True)
    family_id = models.CharField(max_length=50, db_index=True, default='Not Set')
    case_id = models.CharField(max_length=50, blank=True, null=True)
    patient_name = models.CharField(max_length=100, db_index=True)
    hospital_name = models.CharField(max_length=100, blank=True, null=True)
    registered_date = models.DateField(blank=True, null=True)
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    procedure = models.TextField(blank=True, null=True)
    admission_date = models.DateField(blank=True, null=True, verbose_name="Admission Date")  # Unified
    intimation_raised_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient_name} - {self.card_number}"
