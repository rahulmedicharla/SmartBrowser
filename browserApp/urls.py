from django.urls import path
from browserApp import views

urlpatterns = [
    path('', views.browserApp, name = "browserApp")
]