from django.urls import path
from . import views

urlpatterns = [
    # Departments
    path("departments/",              views.DepartmentListView.as_view(),   name="department-list"),
    path("departments/<str:code>/",   views.DepartmentDetailView.as_view(), name="department-detail"),

    # Hospital info
    path('hospital/',              views.HospitalInfoView.as_view(),    name='hospital-info'),

    # Doctors
    path('doctors/',               views.DoctorListView.as_view(),      name='doctor-list'),
    path('doctors/<str:code>/',    views.DoctorDetailView.as_view(),    name='doctor-detail'),

    # Timings
    path('timings/',               views.DoctorTimingListView.as_view(), name='timing-list'),

    # Bulk sync
    path('sync/',                  views.BulkSyncView.as_view(),        name='bulk-sync'),
]