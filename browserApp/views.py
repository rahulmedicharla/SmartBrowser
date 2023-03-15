from django.shortcuts import render

def browserApp(request):
    return render(request, 'browserApp.html', {})
