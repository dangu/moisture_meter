#!/usr/bin/python
import serial
import time
import logging
import traceback
import sys
import sqlite3

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
                timeToSleep =self.sampleTime-operationTime
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

class Db:
    def __init__(self, dbFilename):
        self.conn = sqlite3.connect(dbFilename)


    def createTables(self):
        c = self.conn.cursor()
        
        # Create table senors
        c.execute('''
                CREATE TABLE sensors (
                    id integer primary key autoincrement not null,
                    name varchar,
                    description varchar,
                    enabled boolean default 1
                );
            ''')

        # Create table measurements
        c.execute('''
                CREATE TABLE measurements (
                    id integer primary key autoincrement not null,
                    ts timestamp
                );
            ''')

        # Create table values
        c.execute('''
                CREATE TABLE values (
                    measurement_id integer primary key autoincrement not null,
                    sensor_id integer,
                    moisture float,
                    temperature float
                );
            ''')
        
        # Create indexes
        c.execute('''CREATE UNIQUE INDEX "unique_values" ON "values" ("measurement_id" ASC, "sensor_id" ASC)''')
        
        # Insert sensors
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 1','Monterad i väggen mot vägen')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 2','Monterad i väggen mot vägen')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 3','Monterad i väggen mot vägen')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 4','Monterad i väggen mot vägen')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 5','Monterad i väggen mot vägen')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 6','Monterad i väggen mot vägen')")
        
        # Save (commit) the changes
        self.conn.commit()
        
        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        self.conn.close()
        

if __name__=="__main__":
    myDb = Db('measurement.sqlite')
    


