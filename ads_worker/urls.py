from django.urls import path

from . import views

urlpatterns = [
    path('', views.worker, name='worker'),
]