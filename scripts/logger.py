#!/usr/bin/python
import serial
import time
import logging
import traceback
import sys
import sqlite3
import random

info = logging.getLogger(__name__).info
error = logging.getLogger(__name__).error

SIMULATION = True

class SerialSimulator:
    """Class used for simulating serial data"""
    def __init__(self):
        """Init"""
        self.timeout=None
        self.baudrate = None
    def write(self, dataToWrite):
        """Simulated serial write"""
        pass
    def readlines(self):
        """Simulated serial read"""
        temperature0 = 15
        rh0 = 57
        dataStr=[]
        for sensorId in range(6):
            temperature = temperature0 + random.random()*4
            rh = rh0 + random.random()*5
            dataStr.append("%d;%.2f;%.2f\n" %(sensorId, temperature, rh))
        return dataStr

class Logger:
    def __init__(self, portName, logfile, sampleTime):
        """Init method"""
        if SIMULATION:
            self.ser = SerialSimulator()
        else:
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
                    ts datetime
                );
            ''')

        # Create table values
        c.execute('''
                CREATE TABLE measurement_values (
                    measurement_id integer not null,
                    sensor_id integer not null,
                    temperature float
                );
            ''')
        
        # Create indexes
        c.execute('''CREATE UNIQUE INDEX "unique_values" ON "measurement_values" ("measurement_id" ASC, "sensor_id" ASC)''')
        
        # Insert sensors
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 1','Monterad')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 2','Monterad')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 3','Monterad')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 4','Monterad')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 5','Monterad')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 6','Monterad')")
        
        # Save (commit) the changes
        self.conn.commit()
        
    def close(self):
        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        self.conn.close()
        
    def update1(self):
        """Alter some tables"""
        c = self.conn.cursor()
        c.execute('''
                ALTER TABLE measurement_values ADD 
                    rh float
            ''')
        # Save (commit) the changes
        self.conn.commit()
        
    def addData(self,ts,measurement_values):
        """Add one measurement to the database"""
        c = self.conn.cursor()        

        # Add measurement
        c.execute ('INSERT INTO measurements (ts) VALUES (?)', ts)
        measurement_id = c.lastrowid
        
        for value in measurement_values:
            c.execute('INSERT INTO measurement_values (measurement_id, sensor_id, temperature, rh) VALUES (?,?,?,?)', 
                      (measurement_id,value['sensor_id'],) + value['values'])
    def addOldData(self, filename):
        inFile = open(filename,'r')
        for line in inFile:
            row = line.strip()
            inData = row.split(';')
            ts = (inData[0][0:19],)
            data = []
            for sensorId in range(6):
                temp = inData[3+sensorId*3]
                rh = inData[4+sensorId*3]
                if not (("Error" in temp) or ("Error" in rh)):
                    data.append({'sensor_id':sensorId, 'values':(float(temp),float(rh),)})
                    self.addData(ts,data) 
                else:
                    print "Error found here: " + row 
        self.conn.commit()
        
    def getData(self):
        """
        SELECT ts, rh 
FROM measurement_values mv
INNER JOIN measurements m ON m.id=mv.measurement_id
WHERE sensor_id=2 AND ts >="2016-06-15 00:00:00" AND ts <="2016-06-16 00:00:00"
"""
        pass
    

def testDb():
    """Test database functions"""
    myDb = Db('measurement.sqlite')
    myDb.createTables()
    myDb.update1()
    myDb.addOldData('room.log')
    
def testSimulation():
    """Test simulated data"""
    mode = 0
    if mode ==0:
        print "No input arguments, defaulting to /dev/ttyUSB0, room.log, sampleTime=300"
        myLogger = Logger("/dev/ttyUSB0", "test1.log", sampleTime=3)
        myLogger.start()
        myLogger.close()
    else:
        print "Test mode..."
        while(1):
            myLogger = Logger("/dev/ttyUSB0", "test2.log", sampleTime=5)
            print myLogger.getReading()
if __name__=="__main__":
    testSimulation()
    


