#!/usr/bin/env python

# 
# 
# LCD 2x16

from time import sleep
import os
import RPi.GPIO as GPIO
import subprocess
import lcddriver
import time
import datetime
import sys
import csv

# ----- SETUP -----
pin_up = 23
pin_down = 24
pin_play = 8
pin_stop = 25
pin_off = 22

list_of_stations = "stations.csv"

name = "RasPy Radio v0.7"
hostname = "google.com"
# ----- END of SETUP ------

count = 0 
up = False
down = False
d_station = 1
d_volume = 75

# Load stations
with open(list_of_station, 'rb') as f:
    reader = csv.reader(f)
    radio_list = list(reader)

playlist = [
"http://icecast3.play.cz:80/bonton-128.mp3",
"http://kocka.limemedia.cz:8000/blanikcz128.mp3",
"http://173.244.199.248:80",
"http://icecast4.play.cz:443/country128.mp3",
"http://icecast6.play.cz/egrensis128.mp3",
"http://icecast6.play.cz/dance-radio320.mp3",
"http://icecast4.play.cz/krokodyl128.mp3",
"http://pool.cdn.lagardere.cz:80/fm-bbc-world-128",
"http://icecast3.play.cz:80/evropa2-128.mp3",
"http://icecast8.play.cz/cro1-128.mp3",
"http://amp.cesnet.cz:8000/cro2-256.ogg",
"http://icecast2.play.cz/croplzen128.mp3",
"http://amp.cesnet.cz:8000/cro-radio-wave-256.ogg",
"http://paris.discovertrance.com:8006",
"http://37.59.14.77:8352/stream",
"http://206.190.136.141:5022/Live"
]

name_list = [
"Bonton",
"BlanikCZ",
"SmoothJazz.com",
"Country Radio",
"Radio Egrensis",
"Dance radio",
"Krokodyl",
"BBC-World",
"Evropa2",
"CRO 1",
"CRO 2",
"CRO-Plzen",
"Radio Wave",
"Discover Trance Radio",
"Blues Radio",
"Music City Roadhouse"
]

# https://listenonline.eu/cz/cz.html
# https://www.shoutcast.com/
                          
# --- nemenit ---
print "Inicializace ..."
# set up the pins
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
GPIO.setup(pin_up,GPIO.IN)
GPIO.setup(pin_up, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_down,GPIO.IN)
GPIO.setup(pin_down, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_play,GPIO.IN)
GPIO.setup(pin_play, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_stop,GPIO.IN)
GPIO.setup(pin_stop, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_off,GPIO.IN)
GPIO.setup(pin_off, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# init LCD
lcd = lcddriver.lcd()
line1 = " "
line2 = " "
lcd.lcd_clear();

# init
firstrun = 1
currentChannel = 0
channelCount = 0
index = 1
down = False
up = False
play = False
stop = False
#cmd = " "
stdout = " "
#radio_text = " "
status = " "
ConnectionStatus = " "

# --- ---

def setLCD():
  lcd.lcd_clear();
  lcd.lcd_display_string(str(currentChannel) + "/" + str(channelCount) + " " + name_list[currentChannel - 1], 1)
  lcd.lcd_display_string(str(status), 2)
  return

def test_connection():
  global ConnectionStatus
  response = os.system("ping -c 1 " + hostname)
  if response == 0:
    ConnectionStatus = "Connected"    
  else:
    ConnectionStatus = "Disconnected"
  return

def first_run():
  print name
#   global index
  global d_station
  global cmd
  global stdout
  global currentChannel
  global channelCount
  global status
  
  # nastaveni audio
  os.system("sudo modprobe snd_bcm2835")

  # nastaveni playlistu
  os.system("sudo mpc rm mine")
  sleep(.75)
  os.system("sudo mpc clear")
  sleep(.75)
#   os.system("sudo mpc add http://icecast3.play.cz:80/bonton-128.mp3")
#   sleep(.75)
#   os.system("sudo mpc add http://kocka.limemedia.cz:8000/blanikcz128.mp3")
#   sleep(.75)
#   os.system("sudo mpc add http://173.244.199.248:80")

# naplneni playlistu
  for i in range(len(playlist)):
    os.system("sudo mpc add " + playlist[i])
    sleep(.75)    
  # "mine" je playlist v kterem lze listovat
  os.system("sudo mpc save mine")
  sleep(.75)
  os.system("sudo mpc clear")
  sleep(.75)
  os.system("sudo mpc load mine")

  # zjisteni delky playlistu > channelCount 
  cmd = subprocess.Popen("sudo mpc playlist",shell=True, stdout=subprocess.PIPE)
  stations = cmd.stdout.readlines()
  channelCount = len(stations)

  # spusteni prni stanice
  os.system("sudo mpc volume 0")
  currentChannel = d_station
  os.system("sudo mpc play " + str(currentChannel))
  sleep(.75)
  os.system("sudo mpc volume " + str(d_volume))
  status = "play"
  setLCD()
  return
  
# main loop
def main():
  global down
  global up
  global play
  global stop
  global currentChannel
  global channelCount
  global index
  global d_station
  global stdout
  global status
  
  if(status=="play"):
    if(down==True):
      if(GPIO.input(pin_up)==False):
        print "BUTTON UP PRESSED, SWITCHING TO: "
        if(currentChannel<channelCount):
          currentChannel = currentChannel + 1
        else:
          currentChannel = 1      
        cmd = subprocess.Popen("sudo mpc play " + str(currentChannel),shell=True, stdout=subprocess.PIPE)
        print str(currentChannel) + ": " + cmd.stdout.readline()
        setLCD()
  
    down = GPIO.input(pin_up)
  
    if(up==True):
      if(GPIO.input(pin_down)==False):
        print "BUTTON DOWN PRESSED, SWITCHING TO: "
        if(currentChannel>1):
          currentChannel = currentChannel - 1
        else:
          currentChannel = channelCount      
        cmd = subprocess.Popen("sudo mpc play " + str(currentChannel),shell=True, stdout=subprocess.PIPE)
        print str(currentChannel) + ": " + cmd.stdout.readline()
        setLCD()
  
    up = GPIO.input(pin_down)

  if(stop==True):
    if(GPIO.input(pin_play)==False):
      print "BUTTON PLAY PRESSED, PLAY: "
      cmd = subprocess.Popen("sudo mpc play " + str(currentChannel),shell=True, stdout=subprocess.PIPE)
      print str(currentChannel) + ": " + cmd.stdout.readline()
      status = "play"
      setLCD()

  stop = GPIO.input(pin_play)

  if(play==True):
    if(GPIO.input(pin_stop)==False):
      print "BUTTON STOP PRESSED, STOP: "
      cmd = subprocess.Popen("sudo mpc stop " ,shell=True, stdout=subprocess.PIPE)
      print "STOP"
      status = "stop"
      setLCD()

  play = GPIO.input(pin_stop)  

  return
  
# --- ---

if len(sys.argv) > 1:
  if sys.argv[1] == 'stop':
    print "Koncim ..."
    os.system("sudo mpc stop")
    print "Ukonceno"
    lcd.lcd_clear();
    lcd.lcd_display_string(name, 1)
    lcd.lcd_display_string("Ukonceno", 2)
    GPIO.cleanup()
    quit()

# --- ---

try:
  lcd.lcd_display_string(name, 1)
  lcd.lcd_display_string("  Boot ...", 2)
  sleep(1)
  while not (ConnectionStatus == "Connected"):
    test_connection()  
    lcd.lcd_display_string(str(ConnectionStatus), 2)
    sleep (1)
    
  while True:    
    if (firstrun==1):
#      global firstrun
      first_run()
      firstrun = 2
    else:
      main()
      sleep(.1)
      
      
except KeyboardInterrupt:
  print "Koncim ..."
  os.system("sudo mpc stop")
  print "Ukonceno"
  lcd.lcd_clear();
  lcd.lcd_display_string(name, 1)
  lcd.lcd_display_string("Ukonceno", 2)
  GPIO.cleanup()
