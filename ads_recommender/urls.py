from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sign_in', views.SignIn.as_view(), name='sign_in'),
    path('sign_up', views.SignUp.as_view(), name='sign_up'),
    # path('worker', views.worker, name='worker'),
]
