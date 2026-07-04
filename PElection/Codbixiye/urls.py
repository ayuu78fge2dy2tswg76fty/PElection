from django.urls import path
from . import views

urlpatterns = [
    path('', views.codee_view, name='codee'),
    path('verify-id/', views.verify_id_ajax, name='verify_id'),
    path('submit/', views.submit_vote, name='submit_vote'),
]
