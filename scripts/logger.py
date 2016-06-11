#!/usr/bin/python
import serial
import time
import logging
import traceback
import sys

info = logging.getLogger(__name__).info
error = logging.getLogger(__name__).error

class Logger:
    def __init__(self, portName, logfile, sampleTime):
        """Init method"""
        self.ser = serial.Serial(port=portName)
        self.ser.timeout=2 # [s] timeout
        self.ser.baudrate =9600
        self.sampleTime = sampleTime
        # configure logging
        self.log = logging.basicConfig(level=logging.INFO,
                        filename=logfile, # log to this file
                        format='%(asctime)s;%(levelname)s;%(message)s') # include timestamp

 

    def start(self):
        """Start logging"""
        oldtime=time.time()-self.sampleTime
        timeToSleep=self.sampleTime
        oldTimeToSleep = timeToSleep
        while(True):
            try:
                realDelay=(time.time()-oldtime)
                operationTime = realDelay-oldTimeToSleep
                #print "Operation time: %g" %operationTime
                timeToSleep =sampleTime-operationTime
                #print "Real delay: %g" %(realDelay)
                oldtime=time.time()
                oldTimeToSleep = timeToSleep
                #print "Time to sleep: %g" %timeToSleep
                        
                time.sleep(max(0, timeToSleep)) # Sleeping this time
                resp=self.getReading()
                # Do not log empty data
                if resp != '':
                    logString=""
                    for data in resp:
                        logString += data.strip() + ";"
                    logString = logString[:-1]
                    info(logString)
            except KeyboardInterrupt:
                break
            except:
                error(traceback.format_exc())

    def getReading(self):
        """Get a reading of all sensors"""
        self.ser.write("read\n")
        resp=self.ser.readlines()
        return resp
        
                
    def close(self):
        self.ser.close()


if __name__=="__main__":
    if len(sys.argv) <2:
        print "Joh"
        print "No input arguments, defaulting to /dev/ttyUSB0, room.log, sampleTime=300"
        myLogger = Logger("/dev/ttyUSB0", "room.log", sampleTime=300)
        myLogger.start()
        myLogger.close()
    else:
        if("test" in sys.argv[1]):
            print "Test mode..."
            while(1):
                myLogger = Logger("/dev/ttyUSB0", "test.log", sampleTime=5)
                print myLogger.getReading()

