from django.shortcuts import render, redirect
from .forms import TempInputForm
from .models import Temp

def browserApp(request):
    if request.method == 'POST':
        form = TempInputForm(request.POST)
        if form.is_valid():
            user_input = form.save()
            redirect('browserApp')
    else:
        form = TempInputForm()
    user_input = Temp.objects.last()
    context = {'form': form, 'user_input': user_input}
    return render(request, 'browserApp.html', context)
