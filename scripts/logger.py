#!/usr/bin/python
import serial
import time
import logging
import traceback

info = logging.getLogger(__name__).info
error = logging.getLogger(__name__).error

class Logger:
    def __init__(self, portName, logfile):
        """Init method"""
        self.ser = serial.Serial(port=portName)
        self.ser.timeout=2 # [s] timeout
 
        # configure logging
        self.log = logging.basicConfig(level=logging.INFO,
                        filename=logfile, # log to this file
                        format='%(asctime)s;%(levelname)s;%(message)s') # include timestamp

 

    def start(self):
        """Start logging"""
        sampleTime=3 #[s]
        oldtime=time.time()-sampleTime
        timeToSleep=sampleTime
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
                self.ser.write("read\n")
                self.ser.baudrate =9600
                resp=self.ser.readlines()
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
                error("Error 1")
                error(traceback.format_exc())
                error("Error 2")
        
                
    def close(self):
        self.ser.close()


if __name__=="__main__":
    myLogger = Logger("/dev/ttyUSB0", "room.log")
    myLogger.start()
    myLogger.close()

