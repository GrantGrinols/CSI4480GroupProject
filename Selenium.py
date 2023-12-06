from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

#setting up the webdriver

service = Service()
options = webdriver.EdgeOptions()
driver = webdriver.Edge(service=service, options= options)

#If the page doesn't load in 20 seconds, the driver will start and most likely fail
wait = WebDriverWait(driver, 20)

#How many tests we will perform
maxcount = 5
currentcount = 0
nametoselect = "Kyle2"
similarityarray = []
driver.get("http://127.0.0.1:5000/compare")
wait.until(EC.presence_of_element_located((By.TAG_NAME,'body')))
while(currentcount<maxcount):
    
    wait.until(EC.presence_of_element_located((By.TAG_NAME,'body')))##WAIT until the page is loaded
    dropbox = Select(driver.find_element(By.ID, 'dropdown'))#locate the dropdown box by ID
    dropbox.select_by_value(nametoselect)#Select the name of the clone we are interested in
    input_field = driver.find_element(By.ID,'input_field') #enter the input to input box
    input_field.send_keys("Alexa... who am I?")
    path = driver.find_element(By.ID, 'path_to_real_voice')
    path.send_keys('static/audiodata/KyleDo2.wav')
    button = driver.find_element(By.ID,'comparebutton')
    #breakpoint()
    button.click()#click the button
    wait.until(EC.presence_of_element_located((By.TAG_NAME,'body')))#wait until we are loaded to the page again
    currentcount += 1##this is one iteration
    similarity = wait.until(EC.presence_of_element_located((By.ID,'similarityPercent')))#find the similaritypercent of the fake voice vs real voice
    similarity = similarity.text
    similarity = similarity.replace('%','')
    similarity = float(similarity)##and convert it to a more readable float number
    similarity = similarity *.01
    similarity = round(similarity, 3)
    similarityarray.append(similarity)
    time.sleep(5) #give some time to give the human tester to write the needed information down
driver.close()
print("Testing concluded!")
print("Results:")
for sim in similarityarray:
    print(sim)


               










