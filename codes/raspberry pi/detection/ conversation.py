#!/usr/bin/env python3

def conversationStart(studentName, studentEmotion):
        
    import logging
    import platform
    import subprocess
    import sys
    import threading
    import os
    import serial
    import random
    import RPi.GPIO as GPIO

    from google.assistant.library.event import EventType

    from aiy.assistant import auth_helpers
    from aiy.assistant.library import Assistant
    from aiy.board import Board, Led
    from aiy.voice import tts
    from time import sleep

    #GPIO.setup(channel, GPIO.OUT)
    ser = serial.Serial('/dev/ttyUSB0', 9600)
    sleep(5)


    stop = threading.Event()


    greetings = ["hi", "hello", "hey", "greetings", "howdy", ] #list of greeting words
    sentences = ["you look",]

    a_good = ["i'm fine thank you", "good", "i'm fine", "very well thanks", "very well", "couldn't be better", "i feel great"] #list for good answers
    a_bad = ["not too good", "bad", "i'm not fine", "i'm bad"] #list for bad answers

    questions = ["are you having a good day?", "are you okay?", "how are you?", "how is your day going?", "how is everything going?", "how's everything?", "what's up?", "you all right?", "whassup?"]
    questions1 = ["are you having a good day?", "how is your day going?", "how is everything going?", "how's everything?", "what's up?"]

    def good():
        ser.write(str.encode("G"))
        tts.say('Great to hear',speed=85)
        print("Got answer for good!")
        stop.set()
        return "done"

    def bad():
        ser.write(str.encode("B"))
        tts.say("Sorry to hear that would you like to talk to someone",speed=85)
        print("Got answer for bad!")
        stop.set()
        return "done"

    def process_event(assistant, led, event):
        logging.info(event)
        if event.type == EventType.ON_START_FINISHED:
            led.state = Led.BEACON_DARK  # Ready.
            ser.write(str.encode("R"))
            tts.say((random.choice(greetings), studentName), speed=85)
            if studentEmotion == "happy" or "neutral":
                ser.write(str.encode("R"))
                tts.say("You look happy", speed=85)
                tts.say(random.choice(questions1), speed=85)
            else:
                ser.write(str.encode("R"))
                tts.say(random.choice(questions), speed=85)
            #---
            print('Say "OK, Google" then speak, or press Ctrl+C to quit...')
            sleep(2)
            tts.say("Ok Google")
        elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            led.state = Led.ON  # Listening.
        elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
            print('You said:', event.args['text'])
            text = event.args['text'].lower()
            if text in a_good:
                assistant.stop_conversation()
                good()
            elif text in a_bad:
                assistant.stop_conversation()
                bad()
        elif event.type == EventType.ON_END_OF_UTTERANCE:
            led.state = Led.PULSE_QUICK  # Thinking.
        elif (event.type == EventType.ON_CONVERSATION_TURN_FINISHED
            or event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT
            or event.type == EventType.ON_NO_RESPONSE):
            led.state = Led.BEACON_DARK  # Ready
            stop.set()
        elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
            stop.set()
            


    def main():
        logging.basicConfig(level=logging.INFO)

        credentials = auth_helpers.get_assistant_credentials()
        with Board() as board, Assistant(credentials) as assistant:
            for event in assistant.start():
                process_event(assistant, board.led, event)
                print("processed event")
                if stop.is_set():
                    print("breaking")
                    break


    if __name__ == 'conversation':
        main()