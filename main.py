import elevenlabs
import wave
import json
import librosa
import pandas as pd
import matplotlib.pylab as plt
import librosa.display
from resemblyzer import VoiceEncoder,preprocess_wav
import numpy as np
import os

jsonFile = open("APIKey.json")
key = json.load(jsonFile)
errors = [] #An array of errors that will print out to the reader if there is a problem
KEY = key["APIKey"]#The API Key. Never public post your key.
def SetKey(key):
    elevenlabs.set_api_key(key)#sets the key
def GetVoices():
    voicelist = elevenlabs.voices()

    for voice in voicelist:#fetches all the voices avaliable to the API key
        print(voice.name)
def GenerateVoice(text, name):
    foundflag = False
    voicelist = elevenlabs.voices()

    for voice in voicelist:
        if(voice.name==name):#looks to see if the name is in the list
            
            voice_id = voice.voice_id
            print("found voice")
            foundflag = True

            break
    
    if(foundflag==True):
        voicesound = elevenlabs.generate(text=text,voice= elevenlabs.Voice(voice_id=voice_id,settings=VoiceSettings))#generates the voice (in bytes) by sending the text, voice ID, and settings
        2
        elevenlabs.play(voicesound)#play the sound. The ffmpeg.exe should be in this folder or on your PATH
        filename = "AIClips/AIVoice"+RemoveSpaces(name)+".wav"#save the sound we made in the "AIClips/AIVoice" folder.
        elevenlabs.save(audio=voicesound, filename=filename)
        return filename #path of the new ai voice file
       
    else:
        errors.append("Voice not found. Please try again.")
def CloneVoice():
    print("Please make sure the voice samples is in the audio_data/clone_data/[Name of AI voice] folder")
    foldername=input("Insert the name you want to clone: ")
    path = "audiodata/clonedata/"+foldername
    clonename = MakeUniqueName(foldername,0)
    print("My voice "+ clonename)
    if os.path.exists(path) and os.path.isdir(path):
        file_list = []
        for file_name in os.listdir(path):
            print(file_name)
            file_list.append("audiodata/clonedata/"+foldername+"/"+file_name)
        elevenlabs.clone(
            name = clonename,
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
     
    DrawGraph(generatedvoice, realvoice)
   
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
    similarity= int(similarity)
    print("Similarity: %"+ str(similarity))



def DrawGraph(AIVoice, realVoice): 
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
    plt.savefig("Graphs/"+AIFileName+"Versus"+realFileName+".png")
    plt.show()
    

def RemoveSpaces(stringWithSpaces):
    stringNoSpaces = ''.join(stringWithSpaces.split())
    return stringNoSpaces
option =0
def PrintErrors():#Why are we adding errors to an array? It'll be useful url redirection for flask
    if(errors.__len__() > 0):
        for error in errors:
            print(error)
    errors.clear()
#CompareVoice("AIClips/FakeGrant.wav","audiodata/Grant2.wav") 
#DrawGraph("AIClips/VoiceclipKyleVoice.wav","audio_data/KyleDo2.wav")
print("Hello, and welcome to the AI voice mimic!")
print("Remember to set your API key!")
SetKey(KEY)
VoiceSettings = elevenlabs.VoiceSettings(stability=.75,similarity_boost=.5, use_speaker_boost=True, style= 0.0)
while(option!=-1):
    print("Would you like to (1) list avaliable options, (2) to generate audio, (3) to enter Compare Mode, (4) to clone a voice, (5) to delete a voice, or (6) generation settings (-1) to exit")
    option = int(input("Enter your option now: "))
    if(option==-1):
        print("I hope you have a fantasy day. Goodbye!")
        exit()
    if(option==1):
        print("Here's your list of avaliable voices: ")
        GetVoices()
    if(option==2):
        voice=input("Enter the voice you want to use: ")
        text=input("Enter the text you want this voice to mimic: ")
        GenerateVoice(text, voice)
    if(option==3):
        realvoicefile= input("Enter the file name of the voice you want to compare: ")
        realvoicefile = "audiodata/"+realvoicefile+".wav"
        voice = input("Enter the relevent AI voice: ")
        text = input("Enter the text the voice is trying to mimic: ")
        generatedvoiceFile = GenerateVoice(text, voice)
        CompareVoice(generatedvoiceFile, realvoicefile)
    if(option==4):
        CloneVoice()
    if(option==5):
        print("This will delete the oldest voice with the given name. This voice will be gone for good so be careful!")
        name = input("Enter the name of the voice you want to enter: ")
        RemoveVoice(name)
    if(option==6):
        ChangeSettings()    
    PrintErrors()

3