# -*- coding: utf-8 -*-
'''
#-------------------------------------------------------------------------------
# NATIONAL UNIVERSITY OF SINGAPORE - NUS
# SINGAPORE INSTITUTE FOR NEUROTECHNOLOGY - SINAPSE
# Singapore
# URL: http://www.sinapseinstitute.org
#-------------------------------------------------------------------------------
# Neuromorphic Engineering Group
# Author: Andrei Nakagawa-Silva, MSc
# Contact: nakagawa.andrei@gmail.com
#-------------------------------------------------------------------------------
# Description: Library implementing a simple spike conversion algorithm where
# consecutive samples are compared to a single threshold. If the difference
# is greater than the threshold, a spike is fired. Whenever the run method
# is called, it also returns the number of spikes inside a time window
# for further processing
#-------------------------------------------------------------------------------
'''
#-------------------------------------------------------------------------------
import numpy as np
from copy import copy
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class Spikify():
    #constructor
    def __init__(self,_threshold=0.1,_windowtime=0.05,_sampfreq=100):
        self.threshold = _threshold #threshold
        self.windowTime = _windowtime #time duration of the processing window
        self.sampfreq = _sampfreq #sampling frequency
        self.dt = 1.0 / self.sampfreq #sampling period
        #window size
        self.windowSize = int(self.windowTime*self.sampfreq)
        #processing window
        self.windowproc = np.zeros(self.windowSize)
        #varaibles
        self.prevsample = 0 #previous sample
        self.spikeCounter = 0 #count the number of events processed
        self.genspike = 0 #value of the spike
        self.nspikes =  0 #number of spikes in the processing window
        self.acc_change = 0
        self.maxIntegSamples = int(0.5 * self.sampfreq) #every 200 ms, it gets reset
        self.integCounter = 0

    #generate spikes from input data
    def run(self,_sample):
        #check if the difference exceeds the threshold
        #print('diff', np.abs(_sample - self.prevsample)) #debugging
        if np.abs(_sample - self.prevsample) >= self.threshold:
            self.genspike = 1
            self.acc_change = 0
            self.integCounter = 0
        elif np.abs(self.acc_change + (_sample-self.prevsample)) >= self.threshold :
            self.genspike = 1
            self.acc_change = 0
            self.integCounter = 0
        else:
            if self.integCounter < self.maxIntegSamples:
                self.acc_change += _sample-self.prevsample
                self.genspike = 0
                self.integCounter +=1
            else:
                self.acc_change = 0
                self.genspike = 0
                self.integCounter = 0

        #updates the variable for next iteration
        self.prevsample = _sample

        #keeps track of the number of spikes in the processing window
        self.windowproc[self.spikeCounter] = self.genspike
        self.spikeCounter += 1 #counts how many samples have been collected

        #if the number of samples is greater than the size of the window
        #count the number of spikes and make the counter equal to zero again
        if self.spikeCounter >= len(self.windowproc):
            self.spikeCounter = 0
            self.nspikes = np.sum(self.windowproc)
        else:
            self.nspikes = False #if the window is not filled, return False

        #return the spike response and the number of spikes in the window, if possible
        return [self.genspike,self.nspikes]
#-------------------------------------------------------------------------------
#testing the library
if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt

    #loads the data
    datafile = np.loadtxt('data.txt')

    #spikify parameters
    th = 0.7 #threshold
    windowtime = 0.1 #time in ms for counting spikes
    sampfreq = 100 #sampling frequency in Hz
    #create a spikify object
    spk = Spikify(th,windowtime,sampfreq)
    #spikify the data
    #for all the samples existing in the file, spikify the input
    input = datafile[:,2] #moving average from the optic sensor
    spikeOutput = np.zeros(np.size(input))
    spikeCounts = []
    timev = [0]
    tspk = [0]
    for k in range(len(datafile)):
        genspike,spikecount = spk.run(input[k])
        spikeOutput[k] = genspike
        timev.append(timev[-1]+(1.0/sampfreq))
        if spikecount is not False:
            spikeCounts.append(spikecount)
            tspk.append(tspk[-1] + (1.0/(windowtime*sampfreq)))

    #delete the last time sample
    del timev[-1]
    del tspk[-1]

    #plots
    plt.figure()
    plt.subplot(3,1,1)
    plt.plot(timev,input)
    plt.title('Optic Sensor Output')
    plt.subplot(3,1,2)
    plt.plot(timev,spikeOutput)
    plt.title('Spike Output')
    plt.subplot(3,1,3)
    plt.plot(tspk,spikeCounts)
    plt.title('Spike Count')
    plt.xlabel('Time (s)')
    plt.show()
#-------------------------------------------------------------------------------
