from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
from .models import SearchMode
from .keys import openaikey
import base64
import openai


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

def recordAudio(request):
    audio_file = request.FILES.get('audio')
    print(audio_file.content_type)

    path = default_storage.save('audioFile.wav', ContentFile(audio_file.read()))
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)

    openai.api_key = openaikey
    
    file = open(tmp_file, 'rb')
    transcription = openai.Audio.translate("whisper-1", file)

    print(transcription["text"])

    file.close()
    default_storage.delete(tmp_file)
    
    return render(request, 'browserApp.html')

def updateInputMode():
    return
    