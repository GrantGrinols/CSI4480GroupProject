# CSI4480GroupProject
A project concerning mimicking real people's voices with the help of AI.
## Overview

This project hosts a local website (done via the Flask framework) on your machine. On this website, you can generate AI voice clips and compare these voice clips to other predefined voice samples. Additionally, you can also clone and delete custom voices, should you have paid access to Elevenlabs' exclusive features.

This project also allows for automated testing with Selenium Webdriver by running Selenium.py while main.py is already running. This is particularly useful if you want to get similarity rates in batch or using this software against voice recognition software.



## Requirements
Required Python libraries: elevenlabs, json, resemblyzer, matplotlib, numpy, os, pandas, flask, random
Optional Python libraries (for Selenium.py): selenium, time
Make sure you've made a 'APIKey.json' file with "APIKey": (your key as a string)
ffmpeg.exe is required to play the files. Download it here: https://ffmpeg.org/
In order for this project to function, you need an Elevenlabs API key. You can get an API key by making an account at https://elevenlabs.io/
