#!/usr/bin/python
import serial
import time
import logging

info = logging.getLogger(__name__).info

class Logger:
    def __init__(self, portName, logfile):
        """Init method"""
        self.ser = serial.Serial(port=portName)
        self.ser.timeout=2 # [s] timeout
 
        # configure logging
        self.log = logging.basicConfig(level=logging.INFO,
                        filename=logfile, # log to this file
                        format='%(asctime)s %(message)s') # include timestamp

 

    def start(self):
        """Start logging"""
        for i in range(3):
            self.ser.write("read\n")
            self.ser.baudrate =9600
            resp=self.ser.readlines()
            # Do not log empty data
            if resp != '':
                logString=""
                for data in resp:
                    logString += data.strip() + ";"
                    logString = logString[:-1]
                print repr(logString)
                info(logString)
                
    def close(self):
        self.ser.close()


if __name__=="__main__":
    myLogger = Logger("/dev/ttyUSB0", "room.log")
    myLogger.start()
    myLogger.close()

