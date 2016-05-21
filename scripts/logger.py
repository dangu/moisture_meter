#!/usr/bin/python
import serial
import time
import sys

class Logger:
    def __init__(self, portName):
        """Init method"""
        self.ser = serial.Serial(port=portName)
        print self.ser
        self.ser.timeout=2 # [s] timeout
     
    def start(self):
        """Start logging"""
        for i in range(10):
            self.ser.write("read\n")
            self.ser.baudrate =9600
            resp=self.ser.readlines()
            print "Data: "
            print resp
    
    def close(self):
        self.ser.close()


if __name__=="__main__":
    myLogger = Logger("/dev/ttyUSB0")
    myLogger.start()
    myLogger.close()

