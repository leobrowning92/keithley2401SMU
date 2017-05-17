import control
import telnetlib
import time, datetime, re, sys, os
import matplotlib.pyplot as plt
import numpy as np


smu = control.Keithley2401()
def set_parameters(smu=smu):
    smu.setup_slow_resistance(v=True)



def collect(smu, show=True):
    data=np.empty((0,3))
    if show:
        col_width =10
        fig=plt.figure(figsize=(col_width,col_width*0.6), facecolor="white")
        ax1=plt.subplot(111)
        plt.ion()
    while True:
        try:
            print('collect :  {:%H:%M:%S}'.format(datetime.datetime.now()))
            smu.initiate()
            reading=smu.ask(":fetch?")
            reading=control.data_to_array(reading, 1)
            print (reading)
            data=np.concatenate((data,reading),axis=0)
            if show:
                ax1.clear()
                ax1.plot(data[:,2],data[:,0]/data[:,1],'ro')
                plt.pause(0.05)


        except Exception as e:
            print(e)
            break
    print(data)
    return data



if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    set_parameters(smu)
    data=collect(smu)
    np.savetxt("test.csv", data,header="V,I,t",delimiter=',')
