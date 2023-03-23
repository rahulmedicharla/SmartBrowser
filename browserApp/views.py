from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
from .models import BrowserContent
from .keys import openaikey
from bs4 import BeautifulSoup
import json, requests
import openai

ACADEMIA_CONTEXT = "You are a tutor bot. I will ask questions related to academia and you must give me simple to understand explanations in laymans format. If applicable also give examples that can help solidify the concept, and possible practice questions, again if applicable. Do not give answers that don't relate to my question. I would like your output to be your entire response to the question, given in HTML format. Make sure your explanation is in lay mans, can be understandable by a high schooler, and provide easy to understand examples. USE HTML TO EMBEDD TEXT. Use the examples below as a guideline. Do not use non ascii characters that are not escaped and DO NOT START YOUR RESPONSE WITH THE WORD SOLUTION:.Question: How does a JK flip-flop work? Solution: \"<p><b>JK-FlipFlops</b> <br><br> A <b>JK flip-flop</b> is a type of digital circuit that stores a single bit of information. It has two inputs, <b>J</b> (set) and <b>K</b> (reset), and two outputs, <b>Q</b> and <b>Q̅</b> (Q complement). When the J and K inputs are both low, the flip-flop remains in its previous state. When J is high and K is low, the flip-flop changes its state to high (Q=1). When K is high and J is low, the flip-flop changes its state to low (Q=0). When both J and K are high, the flip-flop toggles between its two states, which means that it switches from high to low or from low to high. <br><br>For example, suppose we start with the flip-flop in the reset state (Q=0). If we set J=1 and K=0, the flip-flop changes its state to high (Q=1). If we then set J=0 and K=1, the flip-flop changes its state to low (Q=0). If we now set J=1 and K=1, the flip-flop toggles its state and becomes high (Q=1) again. <br><br>The JK flip-flop is widely used in digital electronics, particularly in computer memory and microprocessors.</p>\" Question 2: What is the difference between Mitosis and Meiosis? Solution: \"<p><b>Mitosis vs. Meiosis</b> <br><br> Mitosis and meiosis are two types of cell division that occur in eukaryotic cells. Mitosis is the process of cell division that results in the formation of two genetically identical daughter cells, each having the same number of chromosomes as the parent cell. Meiosis is the process of cell division that results in the formation of four genetically diverse daughter cells, each having half the number of chromosomes as the parent cell. <br><br> The main differences between mitosis and meiosis are: </p><ul><li>Mitosis occurs in somatic cells, while meiosis occurs in germ cells</li><li>Mitosis results in two daughter cells, while meiosis results in four daughter cells</li><li>Mitosis produces genetically identical daughter cells, while meiosis produces genetically diverse daughter cells</li><li>Mitosis involves one round of cell division, while meiosis involves two rounds of cell division</li><li>Mitosis maintains the same number of chromosomes in daughter cells as in parent cells, while meiosis reduces the number of chromosomes in daughter cells by half</li></ul>\""
DEVELOPMENT_CONTEXT = "You are a development helper bot. I will ask questions related to coding and development and you must give me working code that best solves the problem. Make sure you check for the latest API's that may change your answer. Do not give answers that don't relate to my question. I would like your output to be a string that is your entire response to the question, given in HTML. Wrap any code or input that the user MUST type in a bold tag in HTML. ONLY GIVE  ME TEXT, DO NOT START YOUR RESPONSE WITH SOLUTION: AND NO NOTES AT THE END! Do not use non ascii characters that are not escaped. Follow these example below. Question: How do I create a react native expo app? Solution: \"<p>To create a new React Native Expo app, you can follow these steps: Install the Expo CLI by running the following command in your terminal:  \n\n<b> npm install -g expo-cli</b>. \n\nOnce the installation is complete, you can create a new Expo app by running the following command in your terminal:   \n\n<b>expo init my-app</b> \n\n Replace \"my-app\" with the name of your app. Follow the prompts in your terminal to choose a template for your app. You can choose a blank template, or a template with pre-configured navigation and other features. Once the app is created, navigate into the app directory by running:  \n\n<b>cd my-app</b>. \n\n Finally, start the development server by running:  \n\n<b>expo start</b> \n\nYour app should now be running in the Expo client on your phone or in an emulator on your computer.</p>\". Question 2: How I record audio in python. Solution: \"<p>You can record audio in Python using the PyAudio library. Here is some sample code to record audio:</p> \n\n<b>import pyaudio</b>\n<b>import wave<b> \n#set the format of the audio \n<b>FORMAT = pyaudio.paInt16CHANNELS = 2</b>\n<b>RATE = 44100CHUNK = 1024</b>\n<b>RECORD_SECONDS = 5</b>\n# initialize PyAudio<b>audio = pyaudio.PyAudio()</b>\n #start recording<b>stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)</b>\n <b>frames = []</b><b>for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):data = stream.read(CHUNK) frames.append(data)</b> \n#stop recording<b>stream.stop_stream()</b>\n<b>stream.close()</b>\n<b>audio.terminate()</b>\n #save the audio file<b>wf = wave.open(\"output.wav\", \"wb\")</b>\n<b>wf.setnchannels(CHANNELS)wf.setsampwidth(audio.get_sample_size(FORMAT))</b>\n<b>wf.setframerate(RATE)</b>\n<b>wf.writeframes(b''.join(frames))</b>\n<b>wf.close()</b></p>\" Remember, only provide what I asked for."
ASSISTANT_CONTEXT = "You are a assistant helper bot. I will ask questions related to real world problems or situations, give me the best solution. Do not give answers that don't relate to my question. I would like your output to be a string that is your entire response to the question, given in HTML format. ONLY GIVE ME THE YOUR RESPONE, DO NOT START WITH Solution:, NO NOTES AT THE END! Do not use non ascii characters that are not escaped Follow these examples below. Question: I have bread, eggs, avocado, and orange juice in my fridge, give me a recipe I can make. Solution: \"<p>You can make an avocado toast topped with a fried egg and a side of fresh orange juice. Here's how:</p><ol><li>Toast 2 slices of bread.</li><li>While the bread is toasting, heat a non-stick pan over medium heat.</li><li>Crack 2 eggs into the pan and cook until the whites are set but the yolks are still runny.</li><li>While the eggs are cooking, slice 1 avocado in half, remove the pit, and scoop out the flesh. Mash the avocado with a fork and spread it evenly on the toasted bread.</li><li>Place a fried egg on top of each slice of bread.</li><li>Serve with a glass of freshly squeezed orange juice.</li></ol>\"Question 2: How do I jump start a car? Solution: \"<p>To jump start a car, you will need a set of jumper cables and another car with a working battery. Here's how:</p><ol><li>Position the two cars so that their batteries are close enough to connect the jumper cables.</li><li>Turn off both cars and connect the red jumper cable to the positive (+) terminal of the dead battery.</li><li>Connect the other end of the red jumper cable to the positive (+) terminal of the good battery.</li><li>Connect the black jumper cable to the negative (-) terminal of the good battery.</li><li>Connect the other end of the black jumper cable to an unpainted metal surface on the engine block or frame of the car with the dead battery. DO NOT connect it to the negative terminal of the dead battery.</li><li>Start the engine of the car with the good battery and let it run for a few minutes.</li><li>Try to start the engine of the car with the dead battery. If it starts, let both cars run for a few minutes.</li><li>Remove the jumper cables in the reverse order that you connected them.</li></ol>\""
URLS_CONTEXT = "Give me two article links, one youtube link, and one img src url for the topic given below. Make sure the links are valid and given them to me as a string seperated by commas. Follow this format \"link one, link two, video link one, img src one\""

def browserApp(request):
    renderSearchModeObj = BrowserContent.objects.first()
    
    context = {
        'search_mode': renderSearchModeObj.search_mode, 
        'input_question': renderSearchModeObj.input_question,
        'result' : renderSearchModeObj.result,
        'related_link_one': renderSearchModeObj.related_link_one,
        'related_link_two': renderSearchModeObj.related_link_two,
        'related_link_three': renderSearchModeObj.related_link_three,
        'img_link': renderSearchModeObj.img_link
        }
    return render(request, 'browserApp.html', context)

def updateSearchModeToAcademia(request):
    obj = BrowserContent.objects.first()
    obj.search_mode = "Academia"
    obj.save()
    context = {
        'search_mode': obj.search_mode, 
        'input_question': obj.input_question,
        'result' : obj.result,
        'related_link_one': obj.related_link_one,
        'related_link_two': obj.related_link_two,
        'related_link_three': obj.related_link_three,
        'img_link': obj.img_link
    }
    return render(request, 'browserApp.html', context)

def updateSearchModeToDevelopment(request):
    obj = BrowserContent.objects.first()
    obj.search_mode = "Development"
    obj.save()
    context = {
        'search_mode': obj.search_mode, 
        'input_question': obj.input_question,
        'result' : obj.result,
        'related_link_one': obj.related_link_one,
        'related_link_two': obj.related_link_two,
        'related_link_three': obj.related_link_three,
        'img_link': obj.img_link
    }
    return render(request, 'browserApp.html', context)

def updateSearchModeToAssistant(request):
    obj = BrowserContent.objects.first()
    obj.search_mode = "Assistant"
    obj.save()
    context = {
        'search_mode': obj.search_mode, 
        'input_question': obj.input_question,
        'result' : obj.result,
        'related_link_one': obj.related_link_one,
        'related_link_two': obj.related_link_two,
        'related_link_three': obj.related_link_three,
        'img_link': obj.img_link
    }
    return render(request, 'browserApp.html', context)

def textRequest(request):
    obj = BrowserContent.objects.first()
    obj.input_question = request.POST.get('inputRequest')
    obj.save()

    text =  receiveAnswer("Question: " + obj.input_question, obj.search_mode)
    obj.result = text
    obj.save()
    
    context = {
        'search_mode': obj.search_mode, 
        'input_question': obj.input_question,
        'result' : obj.result,
        'related_link_one': obj.related_link_one,
        'related_link_two': obj.related_link_two,
        'related_link_three': obj.related_link_three,
        'img_link': obj.img_link
    }
    return render(request, 'browserApp.html', context)



def recordAudio(request):

    #get audio file from request and save in temp file
    audio_file = request.FILES.get('audio')
    print(audio_file.content_type)

    path = default_storage.save('audioFile.wav', ContentFile(audio_file.read()))
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)

    #get open ai transcription
    openai.api_key = openaikey
    
    file = open(tmp_file, 'rb')
    transcription = openai.Audio.translate("whisper-1", file)

    #update front end values and delete temp file
    file.close()
    default_storage.delete(tmp_file)

    print(transcription["text"])

    obj = BrowserContent.objects.first()
    obj.input_question = transcription["text"]
    obj.save()


    text = receiveAnswer(obj.input_question, obj.search_mode)
    obj.result = text
    obj.save()
    
    context = {
        'search_mode': obj.search_mode, 
        'input_question': obj.input_question,
        'result' : obj.result,
        'related_link_one': obj.related_link_one,
        'related_link_two': obj.related_link_two,
        'related_link_three': obj.related_link_three,
        'img_link': obj.img_link
    }
    
    return render(request, 'browserApp.html', context)

def receiveAnswer(question, search_mode):
    openai.api_key = openaikey

    context = ""

    if search_mode == 'Academia' :
        context = ACADEMIA_CONTEXT
    elif search_mode == 'Development' :
        context = DEVELOPMENT_CONTEXT
    else :
        context = ASSISTANT_CONTEXT
    
    question = "Question: " + question

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = [
            {"role" : "system", "content" : context},
            {"role" : "user", "content": question}
        ]
    )

    response = completion.choices[0].message.content
    return response
