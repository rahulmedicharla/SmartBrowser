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

ACADEMIA_CONTEXT = "You are a tutor bot. I will ask questions related to academia and you must give me simple to understand explanations in laymans format. If applicable also give examples that can help solidify the concept, and possible practice questions, again if applicable. Do not give answers that don't relate to my question. I would like your output to be a JSON object. The first key in the object will be the 'response' key which is a string that is your entire response to the question, given in HTML format. The second key in the object is the 'links' key which is an array of HTML anchor tags that have at max three links that relate to the question and help solidify the concept. Make sure your explanation is in lay mans, can be understandable by a high schooler, and provide easy to understand examples. ONLY give me a json object with USE HTML TO EMBEDD LINKS AND TEXT. Use the examples below as a guideline. Provide your response in this format \{\"response\" : \"your response\"\, \"links\" : \"your links\"} Do not use extra commas, white space, non ascii characters that are not escaped, and non json elements. Question: How does a JK flip-flop work. { \"response\": \"<p><b>JK-FlipFlops</b> <br><br> A <b>JK flip-flop</b> is a type of digital circuit that stores a single bit of information. It has two inputs, <b>J</b> (set) and <b>K</b> (reset), and two outputs, <b>Q</b> and <b>Q̅</b> (Q complement). When the J and K inputs are both low, the flip-flop remains in its previous state. When J is high and K is low, the flip-flop changes its state to high (Q=1). When K is high and J is low, the flip-flop changes its state to low (Q=0). When both J and K are high, the flip-flop toggles between its two states, which means that it switches from high to low or from low to high. <br><br>For example, suppose we start with the flip-flop in the reset state (Q=0). If we set J=1 and K=0, the flip-flop changes its state to high (Q=1). If we then set J=0 and K=1, the flip-flop changes its state to low (Q=0). If we now set J=1 and K=1, the flip-flop toggles its state and becomes high (Q=1) again. <br><br>The JK flip-flop is widely used in digital electronics, particularly in computer memory and microprocessors.</p>\", \"links\": \"[<a href=\"https://www.electronics-tutorials.ws/sequential/seq_4.html\" target=\"_blank\">Sequential Circuits</a>, <a href= \"https://www.electronics-notes.com/articles/logic_digital/jk-flip-flop-tutorial-basics.php\" target=\"_blank\">Jk Flip Flop Tutorial</a>, <a href=\"https://www.youtube.com/watch?v=F1OC5e7Tn_o\" target=\"_blank\">JK Flip Flop Video</a>]\"}. Question 2: What is the difference between Mitosis and Meiosis. {\"response\": \"<p><b>Mitosis vs. Meiosis</b> <br><br> Mitosis and meiosis are two types of cell division that occur in eukaryotic cells. Mitosis is the process of cell division that results in the formation of two genetically identical daughter cells, each having the same number of chromosomes as the parent cell. Meiosis is the process of cell division that results in the formation of four genetically diverse daughter cells, each having half the number of chromosomes as the parent cell. <br><br> The main differences between mitosis and meiosis are: </p><ul><li>Mitosis occurs in somatic cells, while meiosis occurs in germ cells</li><li>Mitosis results in two daughter cells, while meiosis results in four daughter cells</li><li>Mitosis produces genetically identical daughter cells, while meiosis produces genetically diverse daughter cells</li><li>Mitosis involves one round of cell division, while meiosis involves two rounds of cell division</li><li>Mitosis maintains the same number of chromosomes in daughter cells as in parent cells, while meiosis reduces the number of chromosomes in daughter cells by half</li></ul>\", \"links\": [\"< a href = \"https://www.khanacademy.org/science/biology/cellular-molecular-biology/stem-cells-and-cancer/a/mitosis-overview\" target=\"_blank\"> Mitosis Overview < /a>,<a href=\"https:/ / www.khanacademy.org / science / biology / classical - genetics / meiosis / a / intro - to - meiosis \" target=\"_blank\">Meiosis Overview</a>,<a href=\"https: //www.youtube.com/watch?v=ijj58pjIWjo\" target=\"_blank\">Mitosis vs Meiosis Video</a>\"]} Remember, only provide what I asked for."
DEVELOPMENT_CONTEXT = "You are a development helper bot. I will ask questions related to coding and development and you must give me working code that best solves the problem. Make sure you check for the latest API's that may change your answer. Do not give answers that don't relate to my question. I would like your output to be a JSON object. The first key in the object will be the 'response' key which is a string that is your entire response to the question, given in HTML. Wrap any code or input that the user MUST type in a bold tag in HTML The second key in the object is the 'links' key which is an array of anchor tags with max three links that relate to the question and could solve and potential errors. Put an emphasis on finding good links to use, possibly from 'stackoverflow', 'w3 schools', and other development websites. ONLY GIVE ME THE JSON OBJECT, NO NOTES AT THE END! Provide your response in this format \{\"response\" : \"your response\"\, \"links\" : \"your links\"} Do not use extra commas, white space, non ascii characters that are not escaped, and non json elements Follow these example below. Question: How do I create a react native expo app? {\"response\": \"<p>To create a new React Native Expo app, you can follow these steps: Install the Expo CLI by running the following command in your terminal:  <b> npm install -g expo-cli</b>. Once the installation is complete, you can create a new Expo app by running the following command in your terminal:   <b>expo init my-app</b>  Replace \"my-app\" with the name of your app. Follow the prompts in your terminal to choose a template for your app. You can choose a blank template, or a template with pre-configured navigation and other features. Once the app is created, navigate into the app directory by running:  <b>cd my-app</b>. Finally, start the development server by running:  <b>expo start</b> Your app should now be running in the Expo client on your phone or in an emulator on your computer.</p>\", \"links\": [\"<a href=\"https://reactnative.dev/docs/environment-setup\" target=\"_blank\"> ReactNative Docs </a>\",\"<a href=\"https://docs.expo.io/\" target=\"_blank\">Expo Docs</a>\",\"<a href=\"https://expo.io/\" target=\"_blank\">Expo<a>\"]} Question 2: How I record audio in python. \"{\"response\": \"<p>You can record audio in Python using the PyAudio library. Here is some sample code to record audio:</p> <b>pythonimport pyaudio</b> <b>import wave<b> #set the format of the audio <b>FORMAT = pyaudio.paInt16CHANNELS = 2</b><b>RATE = 44100CHUNK = 1024</b><b>RECORD_SECONDS = 5</b># initialize PyAudio<b>audio = pyaudio.PyAudio()</b> #start recording<b>stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)</b> <b>frames = []</b><b>for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):data = stream.read(CHUNK) frames.append(data)</b> #stop recording<b>stream.stop_stream()</b><b>stream.close()</b><b>audio.terminate()</b> #save the audio file<b>wf = wave.open(\"output.wav\", \"wb\")</b><b>wf.setnchannels(CHANNELS)wf.setsampwidth(audio.get_sample_size(FORMAT))</b><b>wf.setframerate(RATE)</b><b>wf.writeframes(b''.join(frames))</b><b>wf.close()</b>\",\"links\": \"[\"<a href=\"https: //people.csail.mit.edu/hubert/pyaudio/docs/\" target=\"_blank\">PyAudio Docs</a>\",\"<a href=\"https: //realpython.com/playing-and-recording-sound-python/\" target=\"_blank\">Real Python Tutorial on Audio Recording</a>\", \"<a href=\"https: //www.thepythoncode.com/article/using-microphone-input-in-python\" target=\"_blank\">The Python Code Tutorial on Microphone Input</a>\"]\"} Remember, only provide what I asked for."
ASSISTANT_CONTEXT = "You are a assistant helper bot. I will ask questions related to real world problems or situations, give me the best solution. Do not give answers that don't relate to my question. I would like your output to be a JSON object. The first key in the object will be the 'response' key which is a string that is your entire response to the question, given in HTML format. The second key in the object is the 'links' key which is an an array of anchor tags with max three links that relate to the question Put an emphasis on finding good links to use, ONLY GIVE ME THE JSON OBJECT, NO NOTES AT THE END! Provide your response in this format \{\"response\" : \"your response\"\, \"links\" : \"your links\"} Do not use extra commas, white space, non ascii characters that are not escaped, and non json elements. Follow these examples below. Question: I have bread, eggs, avocado, and orange juice in my fridge, give me a recipe I can make. {\"response\": \"<p>You can make an avocado toast topped with a fried egg and a side of fresh orange juice. Here's how:</p><ol><li>Toast 2 slices of bread.</li><li>While the bread is toasting, heat a non-stick pan over medium heat.</li><li>Crack 2 eggs into the pan and cook until the whites are set but the yolks are still runny.</li><li>While the eggs are cooking, slice 1 avocado in half, remove the pit, and scoop out the flesh. Mash the avocado with a fork and spread it evenly on the toasted bread.</li><li>Place a fried egg on top of each slice of bread.</li><li>Serve with a glass of freshly squeezed orange juice.</li></ol>\",\"links\": \" [\"<a href=\"https://www.delish.com/uk/cooking/recipes/a31080242/avocado-toast-recipe/\" target = \"_blank\">Avocado Toast Recipe</a>\",\"<a href=\"https://www.bonappetit.com/recipe/perfect-fried-eggs\" target = \"_blank\">Perfect Fried Eggs Recipe</a>\",\"<a href=\"https://www.foodnetwork.com/recipes/articles/how-to-squeeze-and-store-citrus-juice\" target = \"_blank\">How to squeeze and store citrus juice</a>\"]\"}  Question 2: How do I jump start a car? {\"response\": \"<p>To jump start a car, you will need a set of jumper cables and another car with a working battery. Here's how:</p><ol><li>Position the two cars so that their batteries are close enough to connect the jumper cables.</li><li>Turn off both cars and connect the red jumper cable to the positive (+) terminal of the dead battery.</li><li>Connect the other end of the red jumper cable to the positive (+) terminal of the good battery.</li><li>Connect the black jumper cable to the negative (-) terminal of the good battery.</li><li>Connect the other end of the black jumper cable to an unpainted metal surface on the engine block or frame of the car with the dead battery. DO NOT connect it to the negative terminal of the dead battery.</li><li>Start the engine of the car with the good battery and let it run for a few minutes.</li><li>Try to start the engine of the car with the dead battery. If it starts, let both cars run for a few minutes.</li><li>Remove the jumper cables in the reverse order that you connected them.</li></ol>\",\"links\": \"[\"<a href=\"https: //www.popularmechanics.com/cars/how-to/a3110/jump-start-car-battery/\" target = \"_blank\">Jump-Start Car Battery</a>\", \"<a href=\"https://www.youtube.com/watch?v=Z2tFKx1FgTs\" target = \"_blank\">How to Jump Start a Car</a>\", \"<a href=\"https://www.dmv.org/how-to-guides/jump-start-car.php\" target = \"_blank\">How to Jump Start a Car - DMV.org</a>\"]\"}"

def browserApp(request):
    renderSearchModeObj = BrowserContent.objects.first()
    
    context = {
        'search_mode': renderSearchModeObj.search_mode, 
        'input_question': renderSearchModeObj.input_question,
        'result' : renderSearchModeObj.result,
        'related_link_one': renderSearchModeObj.related_link_one,
        'related_link_two': renderSearchModeObj.related_link_two,
        'related_link_three': renderSearchModeObj.related_link_three,
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
    }
    return render(request, 'browserApp.html', context)

def textRequest(request):
    obj = BrowserContent.objects.first()
    obj.input_question = request.POST.get('inputRequest')
    obj.save()

    result =  receiveAnswer("Question: " + obj.input_question, obj.search_mode)
    print(result)
    try:
        response = json.loads(result)

        obj.result = response["response"]
        obj.related_link_one = response["links"][0]
        obj.related_link_two = response["links"][1]
        obj.related_link_three = response["links"][2]
        obj.save()

    except Exception as e:
        obj.result = "Invalid question, try again"
        obj.related_link_one = ""
        obj.related_link_two = ""
        obj.related_link_three = ""
        obj.save()
    
    context = {
        'search_mode': obj.search_mode, 
        'input_question': obj.input_question,
        'result' : obj.result,
        'related_link_one': obj.related_link_one,
        'related_link_two': obj.related_link_two,
        'related_link_three': obj.related_link_three,
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


    result =  receiveAnswer(obj.input_question, obj.search_mode)
    print(result)
    try:
        response = json.loads(result)

        obj.result = response["response"]
        obj.related_link_one = response["links"][0]
        obj.related_link_two = response["links"][1]
        obj.related_link_three = response["links"][2]
        obj.save()

    except Exception as e:
        obj.result = "Invalid question, try again"
        obj.related_link_one = ""
        obj.related_link_two = ""
        obj.related_link_three = ""
        obj.save()
    
    context = {
        'search_mode': obj.search_mode, 
        'input_question': obj.input_question,
        'result' : obj.result,
        'related_link_one': obj.related_link_one,
        'related_link_two': obj.related_link_two,
        'related_link_three': obj.related_link_three,
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