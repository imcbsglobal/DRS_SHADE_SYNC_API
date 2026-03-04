from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Doctor, DoctorTiming, HospitalInfo, Department
from .serializers import (
    DoctorSerializer, DoctorWriteSerializer,
    DoctorTimingSerializer, DoctorTimingWriteSerializer,
    HospitalInfoSerializer, SyncPayloadSerializer,
    DepartmentSerializer
)


# ──────────────────────────────────────────────────────────────
#  Hospital Info
# ──────────────────────────────────────────────────────────────
class HospitalInfoView(APIView):
    """
    GET  /api/hospital/   - return hospital info
    POST /api/hospital/   - upsert hospital info
    """

    def get(self, request):
        obj = HospitalInfo.objects.first()
        if not obj:
            return Response({'detail': 'No hospital info found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(HospitalInfoSerializer(obj).data)

    def post(self, request):
        data = request.data
        obj  = HospitalInfo.objects.first()
        if obj:
            ser = HospitalInfoSerializer(obj, data=data, partial=True)
        else:
            ser = HospitalInfoSerializer(data=data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────────────────────
#  Doctors
# ──────────────────────────────────────────────────────────────
class DoctorListView(APIView):
    """
    GET  /api/doctors/          - list all doctors (with timings)
    POST /api/doctors/          - create / upsert a doctor
    """

    def get(self, request):
        dept = request.query_params.get('department')
        qs   = Doctor.objects.all()
        if dept:
            qs = qs.filter(department=dept)
        return Response(DoctorSerializer(qs, many=True).data)

    def post(self, request):
        ser = DoctorWriteSerializer(data=request.data)
        if ser.is_valid():
            obj, created = Doctor.objects.update_or_create(
                code=ser.validated_data['code'],
                defaults=ser.validated_data
            )
            return Response(
                DoctorSerializer(obj).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorDetailView(APIView):
    """
    GET  /api/doctors/<code>/   - single doctor
    POST /api/doctors/<code>/   - update doctor
    """

    def get(self, request, code):
        doctor = get_object_or_404(Doctor, code=code.strip())
        return Response(DoctorSerializer(doctor).data)

    def post(self, request, code):
        doctor = get_object_or_404(Doctor, code=code.strip())
        ser    = DoctorWriteSerializer(doctor, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(DoctorSerializer(doctor).data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────────────────────
#  Doctor Timings
# ──────────────────────────────────────────────────────────────
class DoctorTimingListView(APIView):
    """
    GET  /api/timings/          - list all timings (filter ?code=XX)
    POST /api/timings/          - create / upsert a timing record
    """

    def get(self, request):
        code = request.query_params.get('code')
        qs   = DoctorTiming.objects.all()
        if code:
            qs = qs.filter(code=code.strip())
        return Response(DoctorTimingSerializer(qs, many=True).data)

    def post(self, request):
        ser = DoctorTimingWriteSerializer(data=request.data)
        if ser.is_valid():
            obj, created = DoctorTiming.objects.update_or_create(
                slno=ser.validated_data['slno'],
                defaults=ser.validated_data
            )
            return Response(
                DoctorTimingSerializer(obj).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────────────────────
#  Bulk Sync Endpoint
# ──────────────────────────────────────────────────────────────
class BulkSyncView(APIView):
    """
    POST /api/sync/
    Accepts full payload from sync tool:
    {
        "hospital": { "firm_name": "...", "address1": "..." },
        "doctors":  [ { "code": "...", "name": "...", ... } ],
        "timings":  [ { "slno": 1, "code": "...", "t1": 9.00, "t2": 17.00 } ]
    }
    """

    def post(self, request):
        ser = SyncPayloadSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        data    = ser.validated_data
        results = {'doctors': 0, 'timings': 0, 'hospital': False, 'errors': []}

        # Hospital info
        hospital_data = data.get('hospital')
        if hospital_data:
            obj = HospitalInfo.objects.first()
            hs  = HospitalInfoSerializer(obj, data=hospital_data, partial=True) if obj \
                  else HospitalInfoSerializer(data=hospital_data)
            if hs.is_valid():
                hs.save()
                results['hospital'] = True
            else:
                results['errors'].append({'hospital': hs.errors})

        # Doctors
        for doc in data.get('doctors', []):
            ds = DoctorWriteSerializer(data=doc)
            if ds.is_valid():
                Doctor.objects.update_or_create(
                    code=ds.validated_data['code'],
                    defaults=ds.validated_data
                )
                results['doctors'] += 1
            else:
                results['errors'].append({'doctor': ds.errors})

        # Timings
        for timing in data.get('timings', []):
            ts = DoctorTimingWriteSerializer(data=timing)
            if ts.is_valid():
                DoctorTiming.objects.update_or_create(
                    slno=ts.validated_data['slno'],
                    defaults=ts.validated_data
                )
                results['timings'] += 1
            else:
                results['errors'].append({'timing': ts.errors})

        http_status = status.HTTP_200_OK if not results['errors'] else status.HTTP_207_MULTI_STATUS
        return Response({'status': 'sync complete', 'results': results}, status=http_status)

    def get(self, request):
        """Return current sync status / counts"""
        return Response({
            'doctors_count':  Doctor.objects.count(),
            'timings_count':  DoctorTiming.objects.count(),
            'hospital_ready': HospitalInfo.objects.exists(),
        })

# ──────────────────────────────────────────────────────────────
#  Departments
# ──────────────────────────────────────────────────────────────
class DepartmentListView(APIView):
    """
    GET  /api/departments/       - list all departments
    GET  /api/departments/<code>/ - single department
    """

    def get(self, request):
        qs = Department.objects.all().order_by("code")
        return Response(DepartmentSerializer(qs, many=True).data)


class DepartmentDetailView(APIView):

    def get(self, request, code):
        from django.shortcuts import get_object_or_404
        dept = get_object_or_404(Department, code=code.strip())
        return Response(DepartmentSerializer(dept).data)