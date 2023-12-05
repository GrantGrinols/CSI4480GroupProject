import elevenlabs
import json
import librosa
import pandas as pd
import matplotlib.pylab as plt
import librosa.display
from resemblyzer import VoiceEncoder,preprocess_wav
import numpy as np
import os
from flask import Flask, redirect, url_for, render_template, request
import random

KEY = "None"
if(os.path.exists("APIKey.json")):
    jsonFile = open("APIKey.json")
    key = json.load(jsonFile)
    errors = [] #An array of errors that will print out to the reader if there is a problem
    KEY = key["APIKey"]#The API Key. Never public post your key.
    elevenlabs.set_api_key(KEY)
    print("key loaded")
    
else:
    print("Warning: No Key detected. Be sure to enter it in the home page")

def GetVoices():
    voicelist = elevenlabs.voices()

    for voice in voicelist:#fetches all the voices avaliable to the API key
        print(voice.name)
def GenerateVoice(text, name,settings):
    foundflag = False
    voicelist = elevenlabs.voices()
    for voice in voicelist:
        
        if(voice.name==name):#looks to see if the name is in the list
            
            voice_id = voice.voice_id
            print("found voice")
            foundflag = True

            break
    
    if(foundflag==True):
        voicesound = elevenlabs.generate(text=text,voice= elevenlabs.Voice(voice_id=voice_id,settings=settings))#generates the voice (in bytes) by sending the text, voice ID, and settings
        filename = "static/AIClips/AIVoice"+RemoveSpaces(name)+".wav"#save the sound we made in the "AIClips/AIVoice" folder.
        elevenlabs.save(audio=voicesound, filename=filename)
        return filename #path of the new ai voice file
       
    else:
        errors.append("Voice not found. Please try again.")
def CloneVoice(path,name):
    print("Please make sure the voice samples is in the audio_data/clone_data/[Name of AI voice] folder")
    
    name = MakeUniqueName(name,0)
    
    
    if os.path.exists(path) and os.path.isdir(path):
        file_list = []
        for file_name in os.listdir(path):
            print(file_name)
            file_list.append(path+"/"+file_name)
        elevenlabs.clone(
            name = name,
            description = "A new voice added to the Elevenlabs library via the Python project",
            files = file_list,

        )

    else:
        errors.append("Folder not found.")


def MakeUniqueName(foldername,number):
    dupeflag = False
    testname = foldername
    if(number > 0):
        testname = testname + str(number)
    ## This function makes sure the clone name is unique. This just makes finding the name we want... so much easier.
    voicelist = elevenlabs.voices()
    for voice in voicelist:
        if(voice.name == testname):
            print("Duplication detected")
            number = number + 1
            dupeflag = True
            break
    if(not(dupeflag)):
        if(number > 0):
            foldername = foldername + str(number)#if there is a duplicate name, add a number to do to make sure the name is unique.
        print("Voice name: "+ foldername)
        return foldername
    else:
        return MakeUniqueName(foldername,number)#keep looping numbers until a 
    
def RemoveVoice(name):
    voicelist = elevenlabs.voices()##removes the voice 
    voice_id = ""
    foundflag = False
    for voice in voicelist:
        if(voice.name == name):
            print("Found voice.")
            voice_id = voice.voice_id
            foundflag = True
            break
    if(foundflag):
        url = "https://api.elevenlabs.io/v1/voices/" + voice_id #voice_id is the voice we are deleting

        headers = {#uses the request library, provided by elevenlabs, to request to delete the voice.
            "Accept":"application/json",
            "xi-api-key": KEY
        }
        response = elevenlabs.requests.delete(url, headers=headers)
        print(response.text)
        print("voice deleted")
    else:
        errors.append("Voice not found")



def ChangeSettings():
    print("These are the settings to set the Elevenlabs voice generation.")
    print("The default for our project is stability =.75 and similarity boost = .5")
    print("From our testing, this looks to be best result, but feel free to mess around!")
    print("Anything value less than 0 or greater than 1 will be clamped")
    stability = input("enter your stability: ")
    stability=Clamp(int(stability))
    similarity = input("enter your similarity boost: ")
    similarity = Clamp(int(similarity))
    VoiceSettings = elevenlabs.VoiceSettings(stability=stability,similarity_boost=similarity,use_speaker_boost=True, style= 0.0)
    print("Changes made")

def Clamp(number, minvalue, maxvalue):
    return max(min(number, maxvalue), minvalue)  
def CompareVoice(generatedvoice, realvoice):
    if(not(os.path.exists(realvoice))):
        errors.append("Real voice not found. Are you sure you've spelled it right and it's in the audiodata folder?")
        return
     
    pathToGraph=DrawGraph(generatedvoice, realvoice)
   
    #Find some way to compare generatevoice with realvoice
    #print out the similarity
    encoder = VoiceEncoder()
    processedfile1 = preprocess_wav(generatedvoice)
    processedfile2 = preprocess_wav(realvoice)
    embed1 = encoder.embed_utterance(processedfile1)
    embed2 = encoder.embed_utterance(processedfile2)
    dot_product_size = np.dot(embed1, embed2)
    norm_sound1 = np.linalg.norm(embed1)
    norm_sound2 = np.linalg.norm(embed2)

    similarity = dot_product_size / (norm_sound1 * norm_sound2)
    similarity = similarity * 100
    similarity= str(similarity)
    graphAndSimilarity = [pathToGraph, similarity]
    return graphAndSimilarity



def DrawGraph(AIVoice, realVoice):
    plt.cla()
    #print out the graph of each voice
    y1, sr1 = librosa.load(AIVoice)
    y2, sr2 = librosa.load(realVoice)

    AIFileName = os.path.basename(AIVoice)
    realFileName = os.path.basename(realVoice)
    AIFileName = str(os.path.splitext(AIFileName)[0])
    realFileName = str(os.path.splitext(realFileName)[0])
    AIFileName = AIFileName.lstrip('/')
    realFileName = realFileName.lstrip('/')


    time1 = librosa.times_like(y1, sr=sr1)
    time2 = librosa.times_like(y2, sr=sr2)
    plt.subplot(2,1,1)
    plt.title("AI Audio: "+ AIFileName)
    plt.ylabel('Amplitude')
    pd.Series(y1[:10000]).plot(figsize=(10,5))
    plt.subplot(2,1,2)
    plt.title("Real Audio: "+ realFileName)
    plt.ylabel('Amplitude')
    pd.Series(y2[:10000]).plot(figsize=(10,5))
    path = "static/Graphs/"+AIFileName+"Versus"+realFileName+".png"
    plt.savefig(path)
    plt.close()
    
    return path
    

def RemoveSpaces(stringWithSpaces):
    stringNoSpaces = ''.join(stringWithSpaces.split())
    return stringNoSpaces
option =0
def PrintErrors():#Why are we adding errors to an array? It'll be useful url redirection for flask
    if(errors.__len__() > 0):
        for error in errors:
            print(error)
    errors.clear()
def FetchNames():#simplies fetches the voices found in the elevenlabs account
    names = []
    voicelist = elevenlabs.voices()
    for voice in voicelist:
        names.append(voice.name)
    return names

def GetRandomPlaceholder():
    RandomList = ["Never gonna give you up.\nNever gonna let you down.\nNever gonna clown around and desert you.",
                  "The next big thing is here: Using Text-To-Speech generation. Text To Speech generation has been making waves recently. It's so fast for Congress to keep up.",
                  "A fun fact about computers is that the first electronic computer, known as ENIAC (Electronic Numerical Integrator and Computer), weighed around 27 tons and occupied about 1,800 square feet of floor space. It was built in the 1940s and used around 18,000 vacuum tubes, consuming a significant amount of electricity and generating a lot of heat. Despite being incredibly large and much less powerful than modern devices, it paved the way for the development of today's compact and high-speed computers. This was brought to you by Chat-GBT",
                  "Welcome to Oakland University.\nThe school hosts several highly education fields such as SECS, Arts, Health, Business, and so much more! The campus does its best to meet student expectations.",
                  "Hello fellow human. These are not the humans you are searching for. I am a human by the way.",
                  "Hello. This is your long lost uncle. I've been busy after it was discovered I was a nigerian prince. I have a large quanity of gold that needs to leave my royal estate, and I need your help.",
                  "Sometimes the only thing that keeps me up at night... is you",
                  "A bee's wing span can not in support its own body weight. Therefore, bees are witchcraft",
                  "This sentence costed you a fraction of a coin! Thank you for your patronage.",
                  "He's checking his list. Checking it twice. \nHe's checking whether you've been naughty or nice. \nAnnnyii Liu is coming to town!"]
    chosenstring = random.choice(RandomList)
    return chosenstring

print("Hello, and welcome to the AI voice mimic! Starting up web page...")



##here be flask implementations
app = Flask(__name__, static_url_path='/static')#Important: Put all images/audio and other paths in the static folder when you want to display it in the web page!
@app.route("/")
def home():##consider this the home page. This html loads when the python runs.
    return render_template("index.html")

@app.route("/process",methods=['POST','GET'])#Think as this as the 'central processor' that takes the user to the right url. Without this, request.form() would be confused trying to guess what you want.
def process():
    try:
        value = request.form['key_field']
        print(value)
        if(not(os.path.exists("APIKey.json"))):
            KEY = value
            elevenlabs.set_api_key(KEY)
            print("Key loaded")
    except:
        print("Key already loaded")
    try:
        destination= request.form['destination']#The page we are going to
        print("Redirecting To:" + destination)
        return redirect(url_for(destination))
    except:
        return url_for('error')#if there is a messup, go to the error page
    
@app.route('/generate', methods=['POST','GET'])##clicking the button with the action="{{url_for('generate')}}" goes here
def generate():
    generateflag = False
    AIvoiceUrl = ""
    staticUrl= ""
    errormessage = ""
    errorflag = False
    try:
        inputText = request.form['input_field']
        stability = float(request.form['stability_slider'])
        similarity_boost = float(request.form['similarity_boost_slider'])
        name = request.form['dropdown']
        if(inputText==""):
            errormessage = "You must enter text"
            errorflag = True
            raise "You must enter text"
               
        if(elevenlabs.get_api_key()==None):
            errormessage = "You must set the API key to use this application. Go back to home."
            errorflag = True
            raise "You must set the API key to use this application. Go back to home."
        VoiceSettings = elevenlabs.VoiceSettings(stability=stability,similarity_boost=similarity_boost, use_speaker_boost=True, style= 0.0)
        print("Generating a voice with "+ name)
        AIvoiceUrl=GenerateVoice(inputText,name,VoiceSettings)
        staticUrl = AIvoiceUrl.lstrip("static/")
        generateflag = True

    except:
        errorflag = True
        if(errormessage == ""):
            errormessage = "An error has occured, and we aren't sure why this has happened. If you're reading this, please contact the developers."
    inputText = GetRandomPlaceholder()
    names = FetchNames()
    return render_template("generate.html", names=names,placeholder=inputText, voiceUrl=staticUrl,generateflag=generateflag, errormessage = errormessage, errorflag = errorflag)

@app.route('/compare', methods=['POST','GET'])
def compare():
    compareflag = False
    AIvoiceUrl = ""
    staticUrl = ""
    realVoiceUrl = ""
    pathToGraph = ""##path to the graph png file
    similarityPercent = ""
    errormessage = ""
    errorflag = False
    try:
        inputText = request.form['input_field']#gets the value found in input_field, that's inside the form/button that executed this function.
        stability = float(request.form['stability_slider'])
        similarity_boost = float(request.form['similarity_boost_slider'])
        name = request.form['dropdown']
        if(elevenlabs.get_api_key()==None):
            errormessage = "You must set the API key to use this application. Go back to home."
            errorflag = True
            raise  "You must set the API key to use this application. Go back to home."
        
        realVoiceUrl = request.form['path_to_real_voice']#The path towards the real voice clip we'll use to compare
        VoiceSettings = elevenlabs.VoiceSettings(stability=stability,similarity_boost=similarity_boost, use_speaker_boost=True, style= 0.0)
        if(inputText==""):
            errormessage = "You must enter text"
            errorflag = True
            raise "You must enter text"
        if(os.path.exists(realVoiceUrl)):
            errormessage = "You did not enter a valid path"
            errorflag = True
            raise "You must enter a valid path"
        AIvoiceUrl=GenerateVoice(inputText,name,VoiceSettings)

        graphAndSimilarity = CompareVoice(AIvoiceUrl,realVoiceUrl)

        pathToGraph = graphAndSimilarity[0]
        similarityPercent = graphAndSimilarity[1]
        pathToGraph = pathToGraph.lstrip("static/")##When flask looks at paths, it considers the static folder as the home directory.
        staticUrl = AIvoiceUrl.lstrip("static/")
        compareflag = True
    except:
        errorflag = True
        if(errormessage == ""):
            errormessage = "An error has occured, and we aren't sure why this happened. If you're reading this, please contact the developers."


    inputText = GetRandomPlaceholder()
    names= FetchNames()
    return render_template("compare.html",names=names,placeholder=inputText,voiceUrl=staticUrl,similarityPercent=similarityPercent,pathToGraph=pathToGraph,compareflag=compareflag, errormessage = errormessage, errorflag = errorflag)    

@app.route('/clone', methods=['POST','GET'])
def clone():
    createcloneflag = False
    deletecloneflag = False
    name = ""
    path = ""
    errorflag = False
    errormessage = ""
    names = FetchNames()
    try:
        decision = request.form['decision']#If decision is == "clone", create a cloned voice. If decision is == "delete", delete the voice
        if(decision=="clone"):
            createcloneflag = True
        if(decision=="delete"):
            deletecloneflag = True
    except:
        createcloneflag = False
        deletecloneflag = False
    try:
        if(createcloneflag):
            name = request.form['clonename']##Here, name will be the name of the voice to be created.
            path = request.form['pathtofolder']#The user will have to manually paste the folder path himself. We can't do it due to security reasons.
            CloneVoice(path,name)
            if(name==""or name == None):
                createcloneflag = False
                errorflag = True
                errormessage = "You must enter a name of the clone"
                raise "You must enter a name of the clone"
        if(deletecloneflag):
            name = request.form['dropdown']##here, name will be selected from a dropdown box and this is the name that will be deleted.
            RemoveVoice(name)
            
    except:
        errorflag = False
    
    return render_template("clone.html",names=names,createcloneflag=createcloneflag,deletecloneflag=deletecloneflag,name=name)





if __name__ == "__main__":
    app.run(debug=True)


