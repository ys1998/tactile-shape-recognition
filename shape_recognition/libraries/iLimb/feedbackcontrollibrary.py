import os, sys
sys.path.append('../general')
sys.path.append('../neuromorphic')
from threadhandler import *
from neuromorphic import *
from tactileboard import *
from collections import deque
from iLimb import *
ilimb = iLimbController('COM16')
ilimb.connect()
ilimb.control(['thumb','index','middle','ring','little'],['open']*5,[297]*5)
time.sleep(1)
#ilimb.control(['thumb','index'],['close']*2,[297]*2)
#time.sleep(0.1)
#ilimb.control(['middle','ring','little'],['close']*3,[297]*3)
#a = input('')
#-------------------------------------------------------------------------------
rightTactile = TactileBoard('COM59',_sensitivity=TBCONSTS.DEFAULT_SENS)
rightTactile.start()
rightTactile.startCalibration(100)
time.sleep(0.5)
rightTactile.loadCalibration()
rightTactile.useCalib = True
auxcounter = 0
findex = []
fthumb = []
flagType = 0
pos = 0
dataQueue = deque()
flagIndexOk = False
flagThumbOk = False
flagFingers = False
flagRun = True
thProc = None
fingerArray = [['thumb',2,0.2],['index',4,0.1]]#,['ring',3,0.1]]
#-------------------------------------------------------------------------------
def update():
    global rightTactile,ilimb,findex,fthumb,auxcounter,pos,flagIndexOk, flagThumbOk, flagFingers,thProc, flagRun, fingerArray
    if flagRun is True:
        q = rightTactile.getData()
        n = len(q)
        for k in range(n): #only one tactile sensor being used
            tactileSample = q.popleft()
            if flagRun:
                #ret = ilimb.doFeedbackPowerGrasp(tactileSample,fingerArray,5)
                ret = ilimb.doFeedbackPowerGrasp(tactileSample,fingerArray,5)
                if ret is True:
                    print('finished main')
                    flagRun = False
                    break

    time.sleep(0.001)

a = input('')
thProc = ThreadHandler(update)
rightTactile.start()
thProc.start()
a = input('press enter to stop')
