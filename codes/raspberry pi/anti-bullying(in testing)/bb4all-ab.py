""" Library Import """
import pandas as pd 
import time
import board
import adafruit_tcs34725
from gpiozero import PWMOutputDevice, Robot, LineSensor
from time import sleep
import ScanUtility
import bluetooth._bluetooth as bluez

""" Sensor Settings """

i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)

sensor.active(False)

""" Motor Settings """

rightFront_FMotor = PWMOutputDevice(26)  # Right Motor - At Front - Forward
rightFront_BMotor = PWMOutputDevice(17)  # Right Motor - At Front - Backward
rightBack_FMotor = PWMOutputDevice(22)   # Right Motor - At Back  - Forward
rightBack_BMotor = PWMOutputDevice(27)   # Right Motor - At Back  - Backward


leftFront_FMotor = PWMOutputDevice(13)   # Left Motor - At Front - Forward
leftFront_BMotor = PWMOutputDevice(5)    # Left Motor - At Front - Backward
leftBack_FMotor = PWMOutputDevice(12)    # Left Motor - At Back  - Forward
leftBack_BMotor = PWMOutputDevice(24)    # Left Motor - At Back  - Backward 

rightFront_FMotor.value = 0
rightBack_FMotor.value = 0
leftFront_FMotor.value = 0
leftBack_FMotor.value = 0
rightFront_BMotor.value = 0
rightBack_BMotor.value = 0
leftFront_BMotor.value = 0
leftBack_BMotor.value = 0


""" Dataset Create """

df_Color = pd.read_csv("baileysColorLibrary.csv")
df_ClassNames = pd.read_csv("roomIDs.csv")


""" Color Get """

dev_id = 0
sock = bluez.hci_open_dev(dev_id)
ScanUtility.hci_enable_le_scan(sock)
trial = 0
#Scans for iBeacons
while trial == 0:
    returnedList = ScanUtility.parse_events(sock, 10)
    for yourBeacon in returnedList:
        print(yourBeacon)
        print("")
        trial += 1
        break

yourRoomUUID = yourBeacon['uuid']
#print(roomUUID) #Uncomment for debug 
#print("") #Uncomment for debug

matchRooms = df_ClassNames.isin([yourRoomUUID]).any().any()
if (matchRooms == True):
    yourRoomColor = df_ClassNames.loc[df_ClassNames.roomUUID == yourRoomUUID, 'roomColor'].values[0]
    yourColor = yourRoomColor
else: 
    print("There was a problem. Please contact your IT Team.")
        
left_sensor = LineSensor(17)
right_sensor= LineSensor(27)
speed = 0.65


""" Motor Function Create """

def leftTurn():
    rightFront_FMotor.value = 0.6
    rightBack_FMotor.value = 0.6


def stopMotors():
    rightFront_FMotor.value = 0
    rightBack_FMotor.value = 0
    leftFront_FMotor.value = 0
    leftBack_FMotor.value = 0
    rightFront_BMotor.value = 0
    rightBack_BMotor.value = 0
    leftFront_BMotor.value = 0
    leftBack_BMotor.value = 0

""" Motor Setup For Line Follow"""

def motorSetup():
    #Motor Defining Part 1
    rightForwardMotors = (rightFront_FMotor, rightBack_FMotor)
    rightBackwardMotors = (rightFront_BMotor, rightBack_BMotor)
    leftForwardMotors = (leftFront_FMotor, leftBack_FMotor)
    leftBackwardMotors = (leftFront_BMotor, leftBack_BMotor)

    #Motor Defining Part 2
    robot = Robot(left=(leftForwardMotors, leftBackwardMotors), right=(rightForwardMotors, rightBackwardMotors))
    # Or ... robot = Robot(left=((13,12), (5,24)), right=((26,22), (17,27)))

""" Motor Speed Set Up for Line Follow """
def motor_speed():
    while True:
        left_detect  = int(left_sensor.value)
        right_detect = int(right_sensor.value)
        ## Stage 1
        if left_detect == 0 and right_detect == 0:
            left_mot = 1
            right_mot = 1
        ## Stage 2
        if left_detect == 0 and right_detect == 1:
            left_mot = -1
        if left_detect == 1 and right_detect == 0:
            right_mot = -1
        #print(r, l)
        yield (right_mot * speed, left_mot * speed)
    
""" Follow Line Function """

def lineFollow():
    print("Line Follow Started")
    motorSetup()
    robot.source = motor_speed()
    sleep(60)
    robot.stop()
    robot.source = None
    robot.close()
    left_sensor.close()
    right_sensor.close()

""" Correct Line Find Function Create """

def lineFind(yourList):
    print("Line Find Started")
    sensor.active(True)
    leftTurn()
    for x in yourList:
        print(x)
        if x == sensor.color:
            stopMotors()
            break
    sensor.active(False)
    lineFollow()


""" Color Finding """

isColorFound = df_Color.isin([yourColor]).any().any()
if (isColorFound == True):
    yourDecimalList = df_Color.loc[df_Color.color == yourColor, 'decimal'].values.tolist()
    print("Color found! Your decimal codes are: ", yourDecimalList)
    lineFind(yourDecimalList)
elif (isColorFound == False):
    print("Color not found. Please contact your IT team.")