from rest_framework import serializers
from .models import Doctor, DoctorTiming, HospitalInfo, Department


class HospitalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = HospitalInfo
        fields = ['id', 'firm_name', 'address1', 'synced_at']


class DoctorTimingSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DoctorTiming
        fields = ['slno', 'code', 't1', 't2', 'synced_at']


class DoctorSerializer(serializers.ModelSerializer):
    timings = serializers.SerializerMethodField()

    class Meta:
        model  = Doctor
        fields = [
            'code', 'name', 'rate', 'department',
            'avgcontime', 'qualification', 'synced_at', 'timings'
        ]

    def get_timings(self, obj):
        timings = DoctorTiming.objects.filter(code=obj.code)
        return DoctorTimingSerializer(timings, many=True).data


class DoctorWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Doctor
        fields = ['code', 'name', 'rate', 'department', 'avgcontime', 'qualification']


class DoctorTimingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DoctorTiming
        fields = ['slno', 'code', 't1', 't2']


class SyncPayloadSerializer(serializers.Serializer):
    """Full sync payload sent by the sync tool"""
    hospital    = HospitalInfoSerializer(required=False)
    doctors     = DoctorWriteSerializer(many=True, required=False)
    timings     = DoctorTimingWriteSerializer(many=True, required=False)
    sync_source = serializers.CharField(required=False, default='sync_tool')
    sync_time   = serializers.DateTimeField(required=False)

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Department
        fields = ["code", "name", "synced_at"]