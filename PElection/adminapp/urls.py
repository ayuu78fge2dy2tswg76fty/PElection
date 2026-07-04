from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('musharax/', views.musharax_view, name='musharax'),
    path('voiteid/', views.voiteid_view, name='voiteid'),
    path('codbixiye/', views.codbixiye_view, name='codbixiye'),
    path('manageadmin/', views.manageadmin_view, name='manageadmin'),
]
