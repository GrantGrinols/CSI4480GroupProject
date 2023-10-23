import elevenlabs
import wave
import json

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
            print("found voice")
            foundflag = True

            break
    
    if(foundflag==True):
        voicesound = elevenlabs.generate(text,KEY, name)#generates the voice (in bytes) by sending the text, key, and name over to elevenlabs
        
        elevenlabs.play(voicesound)#play the sound. The ffmpeg.exe should be in this folder or on your PATH
        filename = "AIClips/Voiceclip"+name+".wav"#save the sound we made. Useful for later.
        with wave.open(filename, 'w') as wave_file:
            wave_file.setnchannels(2)
            wave_file.setsampwidth(2)
            wave_file.setframerate(44100)
            wave_file.writeframes(voicesound)
        return filename #name of the new ai voice file
       
    else:
        print("Voice not found. Please try again")

def CompareVoice(generatedvoice, realvoice):
    #print out the graph of each voice
    #Find some way to compare generatevoice with realvoice
    #print out the similarity
    print("Work in progress")

    


option =0
print("Hello, and welcome to the AI voice mimic!")
print("Remember to set your API key!")
SetKey(KEY)
while(option!=-1):
    print("Would you like to (1) list avaliable options or (2) enter text or (3) Compare mode (-1) to exit")
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
        voice = input("Enter the relevent AI voice: ")
        text = input("Enter the text the voice is trying to mimic: ")
        generatedvoiceFile = GenerateVoice(text, voice)
        CompareVoice(generatedvoiceFile, realvoicefile)
        
    

