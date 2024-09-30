from django.contrib import admin
from django.urls import path , include
from kd_dashboard import views

urlpatterns = [
    path('', views.allocated_dashboard),
    path('coe_dashoard/<str:plc_name>/<str:station_code>', views.main_page),
    path('plcDataCall/<str:plc_name>/<str:station_name>', views.get_plc_data),
    path('hourlyProdCall/<str:station_code>', views.hourly_call),
   ]
