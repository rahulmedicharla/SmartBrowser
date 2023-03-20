from django.urls import path
from browserApp import views

urlpatterns = [
    path('', views.browserApp, name = "browserApp"),
    path('updateSearchModeToAcademia/', views.updateSearchModeToAcademia, name = "updateSearchModeToAcademia"),
    path('updateSearchModeToDevelopment/', views.updateSearchModeToDevelopment, name = "updateSearchModeToDevelopment"),
    path('updateSearchModeToAssistant/', views.updateSearchModeToAssistant, name = "updateSearchModeToAssistant"),
    path('recordAudio/', views.recordAudio, name = "recordAudio")
]
    