#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TITLE: DisplayBot
# AUTHOR: Alessandro Montaldo
# DESCRIPTION: A raspberry pi telegram bot connected to LED RGB matrix
# NOTE: THIS SCRIPT USES THE LIBRARY:
#       https://github.com/hzeller/rpi-rgb-led-matrix
#       BE SURE TO CLONE IT AND READ THE README 

from samplebase import SampleBase #rpi-rgb samplebase
from rgbmatrix import graphics
from myColor import MyColor #smooth color
import os
import os.path
import time
import datetime #for clock functionality
import sys
import random
import telepot #for telegram bot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
import emoji

class DisplayBox(SampleBase):
    messages = [] #contains telegram messages received
    jobs = [] #contains jobs
    botToken = 'YOURTOKEN' #!!!fill with telegram bot token 
    bot = telepot.Bot(botToken)
    tgMsgFile = "messagesFile.dat" #msg to be shown
    tgMsgBackUp = "messagesBackUp.dat" #all msgs ever received

    def __init__(self, *args, **kwargs):
        super(DisplayBox, self).__init__(*args, **kwargs)
        self.parser.add_argument("-s", "--sec", help="Time for scrolling in seconds", default=0.07)

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()

        #load and set up fonts
        font7x13 = graphics.Font()
        font7x13.LoadFont("fonts/7x13.bdf") #!!!fill with path to bdf font
        font5x8 = graphics.Font() 
        font5x8.LoadFont("fonts/5x8.bdf") #!!!fill with path to bdf font

        #set up variables
        myColor = MyColor() #used for customized colors
        smoothColor = graphics.Color(0, 0, 0)
        my_sec = float(self.args.sec) #time for scrolling
        finish = False #flag for end of string scrolling
        clockWidht = 25 #width set to 25 (content of clock lenght)

        #telegram bot loop
        MessageLoop(self.bot, self.on_chat_message).run_as_thread()

        #import telegram messages from old run
        self.messages = self.importFromFile(self.tgMsgFile)

        while True:

            #------------GET CONTROLSTATICALLY--------------
            self.jobs = [] #empty out job list
            self.jobs.append({'description': 'clock'})
            self.jobs.append({'description': 'telegramBotText'})
            #add other jobs..

            #do every job
            for job in self.jobs:
                command = job["description"]
                
                #SHOW CLOCK
                #------------ clock  ------------------------------------
                if command == "clock":
                    start_time = time.time() #get starting time
                    clockDuration = 10 #seconds of showing clock
                    x_pos = int(self.matrix.width/2 - clockWidht/2) #Center horizzontally (from lf to rg): half of display width - half of the content
                    y_pos = int(self.matrix.height-(self.matrix.height/2 - 7/2)) #Center vertically (from top to bot): proper for 7x13 font (instead change 7/2)

                    while(time.time() < (start_time + clockDuration)): #clock for clockDuration sec
                        self.matrix.brightness = 40
                        
                        r, g, b = myColor.smoothColor() #get rgb color
                        smoothColor = graphics.Color(r, g, b) #set up color
                        clockTime = datetime.datetime.now().strftime("%H:%M") #get time
                        time.sleep(0.2) #wait a little

                        #clockWidht = self.showText(x_pos, y_pos, offscreen_canvas, font5x8, smoothColor, clockTime) #return text width
                        clockWidht = self.showTextAndBack(x_pos, y_pos, offscreen_canvas, font5x8, smoothColor, clockTime, b - (b/1.5), r - (r/1.5), g - (g/1.5)) #return text width

                #SHOW MESSAGES RECEIVED FROM TELEGRAM
                #------------  telegramBot Text ------------------------------------
                elif command == "telegramBotText":
                    x_pos = int(self.matrix.width) #start at right
                    y_pos = int(self.matrix.height-(self.matrix.height/2 - 7/2)) #Center vertically (from top to bot): proper for 7x13 font (instead change 7/2)
                    #for every msg in list
                    if (self.messages != []):
                        for msg in self.messages:
                            #print ('msg: %s' % msg)
                            #begin scrolling item
                            while True:
                                self.matrix.brightness = 40 #adjust brightness
                                r, g, b = myColor.smoothColor() #get rgb color
                                smoothColor = graphics.Color(r, g, b) #set up color
                                finish, x_pos = self.showScrollingText(x_pos, y_pos, offscreen_canvas, font7x13, smoothColor, msg) #returns finish flag and next position

                                if(finish == True):
                                    finish = False #item finished
                                    x_pos = offscreen_canvas.width #reset position
                                    break

                                #scrolling time in s
                                time.sleep(my_sec)

                else:
                    print("Command not recognized")

    #Get list of strings separated from \n imported from filePath
    def importFromFile(self, filePath):
        list = [] #empty out list
        if os.path.isfile(filePath) : #check if file exists
            f=open(filePath,"r")
            fileString = f.read() #get all file content
            fileSplitted = fileString.split("\n") #use \n as elements separator
            for msg in fileSplitted:
                if (msg != ""): #delete empty strings
                    list.append(msg)
            #close file
            f.close()
        return list

    #After telegram message received: process message
    def on_chat_message(self, msg):
        #get infos from telegram message
        content_type, chat_type, chat_id = telepot.glance(msg)
        #setup Buttons layout
        markup = ReplyKeyboardMarkup(keyboard=[
                        ['Mostra messaggi', 'Cancella messaggi'],
                        #['Plain text', KeyboardButton(text='Text only')],
                    ])

        #process text
        if content_type == 'text':
            msgText = msg['text']

            if content_type != 'text':
                self.bot.sendMessage(chat_id, emoji.emojize('Solo testo per favore :confounded:', use_aliases=True), reply_markup=markup)

            #-----FIRST ACCESS------
            elif msgText == "/start":
                #self.bot.sendMessage(chat_id, 'Ciao \nScrivi un messaggio per visualizzarlo sulla DisplayBox', reply_markup=markup)
                self.bot.sendMessage(chat_id, emoji.emojize('Ciao :smile: \nScrivi un messaggio per visualizzarlo sulla DisplayBox (ma niente emoticons)', use_aliases=True), reply_markup=markup)

            #-----SHOW MESSAGES------
            elif msgText == "Mostra messaggi":
                if self.messages == []:
                    self.bot.sendMessage(chat_id, emoji.emojize(u'Non ci sono messaggi :confounded:', use_aliases=True), reply_markup=markup)
                else:   
                    self.bot.sendMessage(chat_id, emoji.emojize('Ecco la lista dei messaggi:', use_aliases=True), reply_markup=markup)
                    for message in self.messages:
                        self.bot.sendMessage(chat_id, message)

            #-----DELETE MESSAGES------
            elif msgText == "Cancella messaggi":
                if self.messages == []:
                    self.bot.sendMessage(chat_id, emoji.emojize(u'La lista è gia vuota :confounded:', use_aliases=True), reply_markup=markup)
                else:       
                    self.bot.sendMessage(chat_id, emoji.emojize('Piazza pulita :sunglasses:', use_aliases=True), reply_markup=markup)
                #reset list
                self.messages = []
                if os.path.isfile(self.tgMsgFile): #check if file exists
                    os.remove(self.tgMsgFile) #delete file

            #-----NEW MESSAGE----------
            else:
                #insert msg in messages list
                self.messages.append(msgText)
                #send back to user insertion confirmation
                self.bot.sendMessage(chat_id, emoji.emojize('Messaggio aggiunto alla lista :wink:', use_aliases=True), reply_markup=markup)
                self.backUpMsg(msgText, self.tgMsgFile) #add msg in the temporary shown messages
                self.backUpMsg(msgText, self.tgMsgBackUp) #add msg even permanently

    #write a msgText and a separator (\n) in a file
    def backUpMsg(self, msgText, fileName):
        #open messages File
        f=open(fileName,"a+")
        #update messagesBackUp
        f.write(u"%s\n" % msgText)
        #close file
        f.close()

    def showScrollingText(self, x_pos, y_pos, offscreen_canvas, font, textColor, text):
        len = self.showText(x_pos, y_pos, offscreen_canvas, font, textColor, text)

        #scroll text
        x_pos -= 1 #decrement position
        if (x_pos + len < 0): #when the text has been entirely scrolled
            #finish = True
            return True, x_pos

        return False, x_pos

    def showText(self, x_pos, y_pos, offscreen_canvas, font, textColor, text):
        offscreen_canvas.Clear() #clear screen
        # draw text on matrix
        # 4-th arg is the vertical position for text
        len = graphics.DrawText(offscreen_canvas, font, x_pos, y_pos, textColor, text)
        #show the new matrix
        offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
        return len #return text width in pixel

    #show text and upper and lower lines as decoration
    def showTextAndBack(self, x_pos, y_pos, offscreen_canvas, font, textColor, text, r, g, b):
        offscreen_canvas.Clear() #clear screen
        #back
        #offscreen_canvas.Fill(r, g, b)
        self.drowCorner(x_pos, y_pos, offscreen_canvas, font, textColor, text, r, g, b)

        # draw text on matrix
        # 4-th arg is the vertical position for text
        len = graphics.DrawText(offscreen_canvas, font, x_pos, y_pos, textColor, text)
        #show the new matrix
        offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
        return len #return text width in pixel

    def drowCorner(self, x_pos, y_pos, offscreen_canvas, font, textColor, text, r, g, b):
        col = graphics.Color(r, g, b)
        graphics.DrawLine(offscreen_canvas, 0, 15, 31, 15, col)
        graphics.DrawLine(offscreen_canvas, 0, 14, 31, 14, col)
        graphics.DrawLine(offscreen_canvas, 0, 13, 31, 13, col)
        graphics.DrawLine(offscreen_canvas, 0, 2, 31, 2, col)
        graphics.DrawLine(offscreen_canvas, 0, 1, 31, 1, col)
        graphics.DrawLine(offscreen_canvas, 0, 0, 31, 0, col)
        return

# Main function
if __name__ == "__main__":
    display_box = DisplayBox()
    if (not display_box.process()):
        display_box.print_help()
