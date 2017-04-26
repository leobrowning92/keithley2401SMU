import serial, time


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
        self.check_Keithley2400()
    def check_Keithley2400(self,v=True):
        print("serial open:",self.ser.isOpen())
        self.ser.write(b"*IDN?\r")
        time.sleep(0.1)
        out=self.ser.readline()
        if v:
            print(out)
        return out
    def send(self,message,v=True):
        self.ser.write((message+"\r").encode())
        if v:
            print(message)
    def get(self,v=True):
        out = self.ser.readline()
        if v:
            print(out)
        return out
    def set_source(self, v=True):
        self.send(":source:function:mode voltage")
        self.send(":source:voltage:mode fixed")
        if v:
            self.send(":source:function:mode?") #fixed by default
            self.get()
            self.send(":source:voltage:mode?") #fixed by default
            self.get()

        self.send(":source:voltage:range minimum") #0.21V
        if v:
            self.send(":source:voltage:range?")
            self.get()
        # sets source level. must be < range
        self.send(":source:voltage:level:immediate:amplitude 0.1")
        if v:
            self.send(":source:voltage:level?")
            self.get()
    def measure(self):
        self.send(":measure?")
        self.get()

    def close(self):
        self.ser.close()
