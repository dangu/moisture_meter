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

SIMULATION = False

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
        self.db = None # Start with no database connection

    def attachDb(self, db):
        """Attach a database object"""
        self.db = db

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
                ts = time.strftime("%Y-%m-%d %H:%M:%S") # Get timestamp
                # Do not log empty data
                if resp != '':
                    logString=""
                    for data in resp:
                        logString += data.strip() + ";"
                    logString = logString[:-1]
                    info(logString)
                    
                    # Log to database
                    if self.db is not None:
                        data = []
                        for line in resp:
                            strippedData = line.strip()
                            dataList = strippedData.split(';')
                            sensorId = int(dataList[0])
                            temp    = dataList[1]
                            rh      = dataList[2]
                            if not (("Error" in temp) or ("Error" in rh)):
                                data.append({'sensor_id':sensorId, 'values':(float(temp),float(rh),)})
                            else:
                                error("Sensor read error: " + str(dataList))
                        self.db.addData(ts,data) 
                        self.db.commit()
                        
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
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 0','Blue. Position C. In wall, upper left.')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 1','Blue/White. Position A. In wall lower left.')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 2','Green. Position D2. In wall center.')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 3','Green/White. Position D1. In air gap center.')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 4','Purple. Position E1. In air gap right wall.')")
        c.execute("INSERT INTO sensors (name, description) VALUES ('Sensor 5','Purple/White. Position E2. In right wall.')")
        
        # Save (commit) the changes
        self.conn.commit()
        
    def close(self):
        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        self.conn.close()
    
    def commit(self):
        """Commit the changes"""
        self.conn.commit()
        
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
        """Add one measurement to the database
        ts    A string with the timestamp to use
        measurement_values    A list with dicts with the keys sensor_id and values     
        """
        c = self.conn.cursor()        

        # Add measurement
        c.execute ('INSERT INTO measurements (ts) VALUES (?)', (ts,))
        measurement_id = c.lastrowid
        
        for value in measurement_values:
            c.execute('INSERT INTO measurement_values (measurement_id, sensor_id, temperature, rh) VALUES (?,?,?,?)', 
                      (measurement_id,value['sensor_id'],) + value['values'])
    def addOldData(self, filename):
        inFile = open(filename,'r')
        for line in inFile:
            row = line.strip()
            inData = row.split(';')
            ts = inData[0][0:19]
            data = []
            for sensorId in range(6):
                temp = inData[3+sensorId*3]
                rh = inData[4+sensorId*3]
                if not (("Error" in temp) or ("Error" in rh)):
                    data.append({'sensor_id':sensorId, 'values':(float(temp),float(rh),)})
                else:
                    print "Error found here: " + row 
            self.addData(ts,data) 
        self.conn.commit()
        
    def getData(self):
        """
        SELECT ts, rh 
FROM measurement_values mv
INNER JOIN measurements m ON m.id=mv.measurement_id
WHERE sensor_id=2 AND ts >="2016-06-15 00:00:00" AND ts <="2016-06-16 00:00:00"
"""
        pass
    
def createDb(dbFilename):
    """Create the database with the default tables"""
    myDb = Db(dbFilename)
    myDb.createTables()
    myDb.update1()

    myDb.close()
    
def testDb():
    """Test database functions"""
    dbFilename = "measurement.sqlite"
    createDb(dbFilename)
    
    # Add old log data
    myDb = Db(dbFilename)
    myDb.addOldData('room.log')
    
    # Connect the database to the logger and start logging
    myLogger = Logger("/dev/ttyUSB0", "test1.log", sampleTime=3)
    myLogger.attachDb(myDb)
    myLogger.start()
    
def testSimulation():
    """Test simulated data"""
    mode = 0
    if mode ==0:
        print "No input arguments, defaulting to /dev/ttyUSB0, room.log, measurement.sqlite, sampleTime=300"
        myLogger = Logger("/dev/ttyUSB0", "test1.log", sampleTime=3)
        myDb = Db("measurement.sqlite")
        myLogger.attachDb(myDb)
        myLogger.start()
        myLogger.close()
    else:
        print "Test mode..."
        while(1):
            myLogger = Logger("/dev/ttyUSB0", "test2.log", sampleTime=5)
            print myLogger.getReading()
            
if __name__=="__main__":
    if len(sys.argv) <2:
        sampleTime = 5*60 #[s]
        print "No input arguments, defaulting to /dev/ttyUSB0, room.log, measurement.sqlite, sampleTime=%ds" %sampleTime
        myLogger = Logger("/dev/ttyUSB0", "room.log", sampleTime=sampleTime)
        myDb = Db("measurement.sqlite")
        myLogger.attachDb(myDb)
        myLogger.start()
        myLogger.close()
    else:
        if("test" in sys.argv[1]):
            print "Test mode..."
            while(1):
                myLogger = Logger("/dev/ttyUSB0", "test.log", sampleTime=5)
                print myLogger.getReading()
        elif "create_db" in sys.argv[1] and len(sys.argv)==(2+1):
            dbFilename = sys.argv[2]
            print "Creating empty database with name " + dbFilename
            createDb(dbFilename)

        elif "add_old" in sys.argv[1] and len(sys.argv)==(3+1):
            print "Adding old data to the database..."
            logFilename = sys.argv[2]
            dbFilename = sys.argv[3]
                # Add old log data
            myDb = Db(dbFilename)
            myDb.addOldData(logFilename)
            myDb.close()
      


