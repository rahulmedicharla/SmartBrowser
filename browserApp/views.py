from django.shortcuts import render
from .models import SearchMode

def browserApp(request):
    renderSearchModeObj = SearchMode.objects.first()
    
    context = {'search_mode': renderSearchModeObj.search_mode}
    return render(request, 'browserApp.html', context)

def updateSearchModeToAcademia(request):
    obj = SearchMode.objects.first()
    obj.search_mode = "Academia"
    obj.save()
    context = {'search_mode': obj.search_mode}
    return render(request, 'browserApp.html', context)

def updateSearchModeToDevelopment(request):
    obj = SearchMode.objects.first()
    obj.search_mode = "Development"
    obj.save()
    context = {'search_mode': obj.search_mode}
    return render(request, 'browserApp.html', context)

def updateSearchModeToAssistant(request):
    obj = SearchMode.objects.first()
    obj.search_mode = "Assistant"
    obj.save()
    context = {'search_mode': obj.search_mode}
    return render(request, 'browserApp.html', context)