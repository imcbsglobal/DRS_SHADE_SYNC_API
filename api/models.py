from django.db import models


class HospitalInfo(models.Model):
    """Maps to sync_misel — written by sync tool"""
    firm_name = models.CharField(max_length=150, blank=True, null=True)
    address1  = models.CharField(max_length=50,  blank=True, null=True)
    synced_at = models.TextField(blank=True, null=True)

    class Meta:
        db_table  = 'sync_misel'      # ← matches sync tool table
        managed   = False             # ← Django won't create/drop this table

    def __str__(self):
        return self.firm_name or "Hospital"


class Doctor(models.Model):
    """Maps to sync_doctors — written by sync tool"""
    code          = models.CharField(max_length=5, primary_key=True)
    name          = models.CharField(max_length=40,  blank=True, null=True)
    rate          = models.FloatField(blank=True, null=True)
    department    = models.CharField(max_length=5,   blank=True, null=True)
    avgcontime    = models.IntegerField(blank=True, null=True)
    qualification = models.CharField(max_length=60,  blank=True, null=True)
    synced_at     = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'sync_doctors'     # ← matches sync tool table
        managed  = False              # ← Django won't create/drop this table

    def __str__(self):
        return f"{self.code} - {self.name}"


class DoctorTiming(models.Model):
    """Maps to sync_doctorstiming — written by sync tool"""
    slno      = models.BigIntegerField(primary_key=True)
    code      = models.CharField(max_length=5, blank=True, null=True)
    t1        = models.FloatField(blank=True, null=True)
    t2        = models.FloatField(blank=True, null=True)
    synced_at = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'sync_doctorstiming'   # ← matches sync tool table
        managed  = False                  # ← Django won't create/drop this table

    def __str__(self):
        return f"Timing {self.slno} - Dr {self.code}"


class Department(models.Model):
    """Maps to sync_department — written by sync tool"""
    code      = models.CharField(max_length=5, primary_key=True)
    name      = models.CharField(max_length=100, blank=True, null=True)
    synced_at = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'sync_department'  # ← matches sync tool table
        managed  = False              # ← Django won't create/drop this table

    def __str__(self):
        return f"{self.code} - {self.name}"