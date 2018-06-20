import os, sys
sys.path.append('../general')
sys.path.append('../neuromorphic')
from threadhandler import *
from neuromorphic import *
from tactileboard import *
from collections import deque
from iLimb import *
ilimb = iLimbController('COM9')
ilimb.connect()
ilimb.control(['thumb','index','middle','ring','little'],['open']*5,[297]*5)
time.sleep(1)
#ilimb.control(['thumb','index'],['close']*2,[297]*2)
#time.sleep(0.1)
#ilimb.control(['middle','ring','little'],['close']*3,[297]*3)
#a = input('')
#-------------------------------------------------------------------------------
rightTactile = TactileBoard('COM17',_sensitivity=TBCONSTS.DEFAULT_SENS)
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
thProc = None
posindex = 0
posthumb = 0
listTaxels = [[] for k in range(TBCONSTS.NCOLS*TBCONSTS.NROWS)]

#-------------------------------------------------------------------------------
def update():
    global rightTactile,ilimb,findex,fthumb,auxcounter,pos,flagIndexOk, flagThumbOk, flagFingers,thProc, posindex, posthumb
    q = rightTactile.getData()
    n = len(q)
    for k in range(n): #only one tactile sensor being used
        tactileSample = q.popleft()
        
        index = tactileSample[0]
        thumb = tactileSample[1]

        #maxIndex = np.max(index)
        #maxThumb = np.max(thumb)

        findex.append(index)
        fthumb.append(thumb)

        if auxcounter >= 2:
            auxmax = -1
            for w in range(len(findex)):
                if(np.max(findex[w]) > auxmax):
                    auxmax = np.max(findex[w])
                    posmaxindex = np.where(findex[w] == auxmax)
                    #print(posmax)
            auxmax = -1
            for w in range(len(fthumb)):
                if(np.max(fthumb[w]) > auxmax):
                    auxmax = np.max(fthumb[w])
                    posmaxthumb = np.where(fthumb[w] == auxmax)
            
            sumindex = 0
            sumthumb = 0
            for w in range(len(findex)):
                sumindex += findex[w][posmaxindex[0][0]][posmaxindex[1][0]]
                sumthumb += fthumb[w][posmaxthumb[0][0]][posmaxthumb[1][0]]

            meanindex = sumindex / len(findex)
            

            meanthumb = sumthumb / len(fthumb)

            #print('index', meanindex, 'thumb', meanthumb)

            print(meanindex, meanthumb)

            if meanindex < 0.1 and meanthumb < 0.1:
                ilimb.control(['thumb','index'],['position']*2,[pos]*2)
                pos += 3
                time.sleep(0.05)
            else:
                print('ok aqui')
                flagFingers = True
                break
            
            # time.sleep(0.05)

            auxcounter = 0
            findex = []
            fthumb = []
        else:
            auxcounter += 1

    if flagFingers:
        time.sleep(0.1)
        ilimb.control(['thumb','index'],['position']*2,[pos-25]*2)
        thProc.kill()
    time.sleep(0.001)

a = input('')
thProc = ThreadHandler(update)
#rightTactile.start()
thProc.start()
a = input('press enter to stop')


