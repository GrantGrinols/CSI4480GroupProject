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
            print(voice_id)
            print("found voice")
            foundflag = True

            break
    
    if(foundflag==True):
        voicesound = elevenlabs.generate(text=text,voice= elevenlabs.Voice(voice_id=voice_id,settings=VoiceSettings))#generates the voice (in bytes) by sending the text, key, and name over to elevenlabs
        2
        elevenlabs.play(voicesound)#play the sound. The ffmpeg.exe should be in this folder or on your PATH
        filename = "AIClips/AIVoice"+RemoveSpaces(name)+".wav"#save the sound we made. Useful for later.
        elevenlabs.save(audio=voicesound, filename=filename)
        return filename #path of the new ai voice file
       
    else:
        print("Voice not found. Please try again")
def CloneVoice():
    print("Please make sure the voice samples is in the audio_data/clone_data/[Name of AI voice] folder")
    foldername=input("Insert the name you want to clone: ")
    path = "audiodata/clonedata/"+foldername
    if os.path.exists(path) and os.path.isdir(path):
        file_list = []
        for file_name in os.listdir(path):
            print(file_name)
            file_list.append("audiodata/clonedata/"+foldername+"/"+file_name)
        elevenlabs.clone(
            name = foldername,
            description = "A new voice added to the Elevenlabs library via the Python project",
            files = file_list,

        )

    else:
        print("Folder not found")    
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

#CompareVoice("AIClips/FakeGrant.wav","audiodata/Grant2.wav") 
#DrawGraph("AIClips/VoiceclipKyleVoice.wav","audio_data/KyleDo2.wav")
print("Hello, and welcome to the AI voice mimic!")
print("Remember to set your API key!")
SetKey(KEY)
VoiceSettings = elevenlabs.VoiceSettings(stability=.75,similarity_boost=.5, use_speaker_boost=True, style= 0.0)
while(option!=-1):
    print("Would you like to (1) list avaliable options or (2) enter text or (3) Compare mode or (4) clone a voice or (5) generation settings (-1) to exit")
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
        ChangeSettings()    
    

3