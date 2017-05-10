import serial, time, os, unittest
import numpy as np

class Keithley2401(object):
    """
    Class that allows serial control of a Keithley2401 source measure
    unit (SMU) using SCPI (Standard Commands for Programmable Instruments)
    protocalls.
    """
    def __init__(self,port='/dev/ttyUSB0' ):
        self.ser = serial.Serial(
            port=port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=3
        )

    def check_Keithley2401(self,v=False):
        isOpen=self.ser.isOpen()
        self.ser.write(b"*IDN?\r")
        time.sleep(0.1)
        out=self.get()
        if v:
            print("serial open:",isOpen)
            print(out)
        return [isOpen,out]

    # helper functions to handle conversions when sending and recieving
    def send(self,message,v=False):
        self.ser.write((message+"\r").encode())
        if v:
            print(message)
    def get(self,v=False):
        out = self.ser.readline()
        if v:
            print(out.decode("utf-8").rstrip() )
        return out.decode("utf-8").rstrip()
    def call_response(self,message,v=False):
        self.send(message)
        # could be updated with a querry for when the machine is ready
        time.sleep(0.1)
        return self.get()
    def get_data(self,v=False):
        data = self.fetch()
        n=int(len(data.split(','))/5) # should equal arm x trigger
        data=np.array( [float(x) for x in data.split(',')] )
        data=np.reshape(data , (n,5))
        data[:,2]=data[:,0]/data[:,1]
        if v:
            print(data)
        return data


    # simplifications of simple commands that would be sent to the smu
    def initiate(self):
        self.send(":initiate")
    def fetch(self):
        return self.call_response(":fetch?")


    # direct smu interaction functions. deal with related commands
    def set_source(self,sourceType,sourceMode,sourceRange,sourceAmplitude, v=False):
        #voltage, current or memory
        self.send(":source:function:mode "+sourceType,v)
        # fixed, list or sweep
        self.send(":source:voltage:mode "+sourceMode,v)
        #minimum, maximum or numerical value
        self.send(":source:voltage:range "+sourceRange,v) #0.21V =minimum
        # value of source level. must be < range
        self.send(":source:voltage:level:immediate:amplitude " + sourceAmplitude,v)

    def check_source(self,v=False):
        sourceType = self.call_response(":source:function:mode?",v)
        sourceMode = self.call_response(":source:voltage:mode?",v)
        sourceRange = self.call_response(":source:voltage:range?",v)
        sourceAmplitude = self.call_response(":source:voltage:level?",v)
        if v:
            print("Sourcing : ",sourceType)
            print("Mode : ",sourceMode)
            print("Range : ",sourceRange)
            print("Value : ",sourceAmplitude)
        return [sourceType,sourceMode,sourceRange,sourceAmplitude]

    def set_sense(self, senseType, senseRange, senseCompliance, v=False):

        self.send(":sense:function '"+senseType+"'")
        self.send(":sense:"+senseType+":protection "+senseCompliance)

        if senseRange=="auto":
            self.send(":sense:"+senseType+":range:auto on")
        else:
            self.send(":sense:"+senseType+":range "+senseRange)
            assert float(senseCompliance) >= float(senseRange), "your range is beyond your compliance range"

    def check_sense(self,v=False):
        # to check which function is being measured
        senseType = self.call_response(":sense:function:on?")
        # determines the range
        senseRange = self.call_response(":sense:current:range?")
        #puts an upper limit on the range
        senseCompliance = self.call_response("sense:current:protection?")
        hitCompliance = self.call_response("sense:current:protection:tripped?")
        if hitCompliance == "1":
            hitCompliance = True
        else:
            hitCompliance = False
        assert hitCompliance == False , "Compliance hit!"
        if v:
            print("Sensing : ",senseType)
            print("Range : ",senseRange)
            print("Compliance : ",senseCompliance)

        return [senseType, senseRange, senseCompliance, hitCompliance]

    def measure(self,v=False):
        """
        note that ascii data format is of the following format:
        V, I, R, t, status
        """
        self.initiate()
        return self.get_data(v)

    def set_trigger(self, arm, trigger, v=False):
        """
        see page 210 of manual for trigger model diagram

        """
        self.send(":arm:count "+str(arm)) # number of sets of triggered data
        self.send(":trigger:count "+str(trigger)) #number of triggers per arm



    def close(self):
        self.ser.close()

class MyTest(unittest.TestCase):
    def setUp(self):
        self.smu=Keithley2401()
    def test_trivial(self):
        self.assertTrue(True)
    def test_ID(self):
        check = self.smu.check_Keithley2401()
        self.assertTrue(check[0])
        self.assertEqual(check[1],'KEITHLEY INSTRUMENTS INC.,MODEL 2401,4095154,A01 Aug 25 2011 12:57:43/A02  /T/K')
    def test_source(self):
        self.smu.set_source("voltage", "fixed","minimum","0.1")
        self.assertEqual(self.smu.check_source(), ['VOLT', 'FIX', '0.21', '1.000000E-01'])
    def test_sense(self):
        self.smu.set_sense("current", "1E-6","1E-3")
        self.assertEqual(self.smu.check_sense(), ['"CURR:DC"', '1.050000E-06', '1.000000E-03', False])
    def tearDown(self):
        self.smu.close()



if __name__ == "__main__":
    #ensures that test cases are not run when importing the module.
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    suite = unittest.TestLoader().loadTestsFromTestCase(MyTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
