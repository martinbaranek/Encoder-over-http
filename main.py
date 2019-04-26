#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import requests
import threading
import json


RoAPin = 27    # pin11
RoBPin = 22    # pin12
RoSPin = 17    # pin13

fCounter = 0

selector = 0
modes = 4
RoBold=0;RoBval=0; busy=0
outdata=[0,255,190,150]
def setup():
    GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by physical location
    GPIO.setup(RoAPin, GPIO.IN)    # input mode
    GPIO.setup(RoBPin, GPIO.IN)
    GPIO.setup(RoSPin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    rotarySetup()

addr="http://192.168.1.28:80/led"
headers={'content-type':'application/json'}
def senddata(data):

    dictdata=dict()
    for i in range(3):
        dictdata["led"+str(3*3+i)]=int(data[0]*data[i+1])
    print("sending: ")
    print(dictdata)
    r=requests.post(addr, data=json.dumps(dictdata), headers=headers)
    print(r.text)




def rotaryDeal(channel):
    global RoBold,RoBval
    global fCounter
    RoBval= GPIO.input(RoBPin)
    RoAval= GPIO.input(RoAPin)
    
    if (RoBold == 0) and (RoBval == 1):
        fCounter += RoAval
        print(fCounter)
    if (RoBold == 1) and (RoBval == 0):
        fCounter -= RoAval
        print(fCounter)
    p = threading.Thread(target=parse,args=[])
    p.start()
    RoBold = GPIO.input(RoBPin)
    

    
def clear(ev=None):
    global selector,fCounter
    fCounter=0
    selector=(selector+1)%modes
    print("selector: "+str(selector))
def rotarySetup():
    GPIO.add_event_detect(RoSPin, GPIO.FALLING, callback=clear,bouncetime=300) # wait for falling
    GPIO.add_event_detect(RoAPin, GPIO.BOTH, callback=rotaryDeal)


def parse():
    global fCounter,outdata,busy
    if fCounter!=0 and busy==0:
        busy=1
        lCounter=fCounter
        fCounter=0
        if selector==0: #total intensity of light
            outdata[0]+=lCounter
            if outdata[0]>16:
                outdata[0]=16
            elif outdata[0]<0:
                outdata[0]=0
        for mode in range(modes):
            if selector==1+mode:
                outdata[1+mode]+=lCounter
                if outdata[1+mode]>255:
                    outdata[1+mode]=255
                elif outdata[1+mode]<0:
                    outdata[1+mode]=0
        print(outdata)
        t=threading.Thread(target=senddata,args=[outdata])
        t.start()
        time.sleep(0.2)
        busy=0
    elif busy==1:
        time.sleep(0.2)
        parse()
def loop():
    while True:
        time.sleep(1)



            
#       print(globalCounter)

def destroy():
    GPIO.cleanup()             # Release resource

if __name__ == '__main__':     # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()