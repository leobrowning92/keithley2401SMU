import serial, time, os, unittest
import numpy,pandas as np,pd

class Keithley2401(object):
    def __init__(self):
        self.ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=3
        )

    def check_Keithley2400(self,v=False):
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
        time.sleep(0.1)
        return self.get()
    def get_data(self,v=False):
        d = self.fetch()
        n=int(len(d.split(','))/5) # should equal arm x trigger
        data=np.reshape(np.array( [float(x) for x in d.split(',')] ) , (n,5))
        df = pd.DataFrame(dn,columns=["V", "I", "R", "t", "status"])
        df.R=df.V/df.I
        if v:
            print(df)
        self.last_data=df
        return df


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
        return [sourceType,sourceMode,sourceRange,sourceAmplitude]

    def measure(self):
        self.send(":measure?")
        self.get()

    def close(self):
        self.ser.close()

class MyTest(unittest.TestCase):
    def setUp(self):
        self.smu=Keithley2401()
    def test_trivial(self):
        self.assertTrue(True)
    def test_ID(self):
        check = self.smu.check_Keithley2400()
        self.assertTrue(check[0])
        self.assertEqual(check[1],'KEITHLEY INSTRUMENTS INC.,MODEL 2401,4095154,A01 Aug 25 2011 12:57:43/A02  /T/K')
    def test_source(self):
        self.smu.set_source("voltage", "fixed","minimum","0.1")
        self.assertEqual(self.smu.check_source(), ['VOLT', 'FIX', '0.21', '1.000000E-01'])
    def tearDown(self):
        self.smu.close()



if __name__ == "__main__":
    #ensures that test cases are not run when importing the module.
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    suite = unittest.TestLoader().loadTestsFromTestCase(MyTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
