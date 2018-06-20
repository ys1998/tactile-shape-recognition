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
# Description: Library implementing different control algorithms. The classes
# are not related to the application in any way. Feedback signals should be
# input directly. Likewise, the generated outputs should be sent to the proper
# hardware such as the iLimb or UR10 after processing
#-------------------------------------------------------------------------------
'''
#-------------------------------------------------------------------------------
import numpy as np
from copy import copy
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
'''
check later how to use an abstract class and it is really interesting
for control systems
class BaseController(ABC):
    def __init__(self, _min=0, _max=500):
        self.minOutput = _min
        self.maxOutput = _max
        super().__init__()

    @abstractmethod
    def run():
        pass
'''
#-------------------------------------------------------------------------------
#Proportional controller for feedback-based control
#This can be used for pressing the switches, for example
class Pcontroller():
    def __init__(self,_Kp=0.1,_min=0,_max=500,_initCond=0):
        self.Kp = _Kp #proportional gain
        self.minOutput = _min #minimum output
        self.maxOutput = _max #maximum output
        self.initCond = _initCond #initial condition
        self.currentOutput = self.initCond
    #run the
    def run(self,_inputSignal,_setPoint):
        #error signal
        error = _setPoint - _inputSignal
        #define the output
        self.output += self.Kp*error
        #saturation
        if self.output > self.maxOutput:
            self.output = self.maxOutput
        elif self.output < self.minOutput:
            self.output = self.minOutput
        #return the current output
        return copy(self.output)
#-------------------------------------------------------------------------------
#Ref: Prach et al., 2017: "Pareto-front analysis of a monotonic PI control law
#for slip suppression in a robotic manipulator"
class SlipController():
    def __init__(self,_MPI_Kp=0.1,_MPI_Ki=0.2,_min=0,_max=500,_dt=0.1,_initCond=0):
        self.MPI_Kp = _MPI_Kp #Proportional gain
        self.MPI_Ki = _MPI_Ki #Integral gain
        self.minOutput = _min #minimum output value
        self.maxOutput = _max #maximum output value
        #initial condition is necessary when the output is already at a level
        #which is usually the case like baseline force or joint position that
        #establishes contact between the robotic hand and the object
        self.initCond = _initCond
        #necessary for the derivative of the input signal which will be used
        #as the velocity signal
        self.prevSample = 0
        #velocity generated signal
        self.velocity = 0
        #position signal
        self.position = 0
        self.dt = _dt #necessary since this is discrete-time formulation
        self.MPI = self.initCond #current MPI output
        self.prevMPI = 0 #previous MPI output, necessary for monotonic behavior

        self.MPI_crossed = False

    #resets the MPI controller
    def reset(self):
        self.MPI = 0
        self.prevMPI = 0
        self.position = 0
        self.velocity = 0

    #run the MPI control and returns its output
    #input: velocity
    def run(self,_inputVelocity):
        self.velocity = _inputVelocity
        #integrate the obtained velocity signal = position
        self.position += (self.velocity*self.dt)
        #print(self.velocity, self.position) #debugging
        #debugging
        #print('mpi', _inputSignal, self.velocity, self.position)
        #MPI output
        #Renaming variables to maintain the same structure as used
		#in the simulink files developed by Dr. Anna Prach
        v = self.velocity
        z = self.position
        #print('mpi', 'v', v, 'z', z)  #debugging
        self.MPI += self.MPI_Kp*np.sign(v)*np.abs(v) #+ self.MPI_Ki*np.sign(z)*np.abs(z)
        #self.MPI = self.initCond + self.MPI
        aux = copy(self.MPI)
        self.MPI = int(np.round(self.MPI))
        #print('init cond', self.initCond, 'MPI', self.MPI) #debugging
        #saturation
        if self.MPI > self.maxOutput:
            self.MPI = self.maxOutput
            if v > 0 :
                self.MPI_crossed = False
            else :
                self.MPI_crossed = False
        elif self.MPI < self.minOutput:
            self.MPI = self.minOutput
        #MPI: output is maintained at the maximum value obtained so far
        if v > 0:
            print('v', v, 'z', z, 'aux', aux, 'MPI', self.MPI, 'prevMPI', self.prevMPI)
    
        if self.MPI < self.prevMPI:
            self.MPI = self.prevMPI
        else:
            self.prevMPI = self.MPI

        if self.MPI < self.maxOutput :
            self.MPI_crossed = False

        #return current MPI output
        return [copy(self.MPI),self.MPI_crossed]
#-------------------------------------------------------------------------------
#examples for the library
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    #create a ramp signal for the position
    #parameters
    dt = 0.001 #sampling period
    t0 = 0 #intial time
    tr0 = 2
    tr1 = 4
    t1 = 6 #final time
    timevec = np.arange(t0,t1,dt)
    posvec = np.zeros(np.shape(timevec))
    mpi = np.zeros(np.shape(timevec))
    #slip controller
    slipCont = SlipController(_MPI_Kp=0.1,_MPI_Ki=0.2,_min=0,_max=500,_dt=dt,_initCond=0)

    #generate the signal and simulate the slip controller
    for k in range(len(timevec)):
        #create the ramp
        if timevec[k] >= tr0 and timevec[k] <= tr1:
            posvec[k] = (posvec[k-1]+1)
        elif timevec[k] > tr1:
            posvec[k] = posvec[k-1]

        mpi[k] = slipCont.run(posvec[k])

    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(timevec,posvec)
    plt.subplot(2,1,2)
    plt.plot(timevec,mpi)
    plt.show()
    #input('press any key to finish...')
