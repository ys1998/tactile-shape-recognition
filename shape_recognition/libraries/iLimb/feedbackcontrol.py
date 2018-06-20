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
#-------------------------------------------------------------------------------
def update():
    global rightTactile,ilimb,findex,fthumb,auxcounter,pos,flagIndexOk, flagThumbOk, flagFingers,thProc
    q = rightTactile.getData()
    n = len(q)
    for k in range(n): #only one tactile sensor being used
        tactileSample = q.popleft()
        for z in range(2):
            
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

                print(meanindex, meanthumb)

                #print('index', meanindex, 'thumb', meanthumb)

                if meanindex < 0.05 and meanthumb < 0.05:
                    ilimb.control(['thumb','index'],['position']*2,[pos]*2)
                    pos += 10
                else:
                    if meanindex < 0.25:
                        ilimb.control('index','close',297)
                        flagIndexOk = True
                    else:
                        flagIndexOk = False
                        #print('index')

                    if meanthumb < 0.18:
                        #ilimb.control(['thumb','middle','ring','little'],['close']*4,[297]*4)
                        ilimb.control('thumb','close',297)
                        #print('thumb')
                        flagThumbOk = True
                    else:
                        flagThumbOk = False

                    if flagThumbOk == True and flagIndexOk == True:
                        flagFingers = True
                    
                time.sleep(0.05)

                auxcounter = 0
                findex = []
                fthumb = []
            else:
                auxcounter += 1

    if flagFingers == True:
        time.sleep(0.1)
        ilimb.control('middle','close',297)
        time.sleep(0.1)
        ilimb.control('ring','close',297)
        time.sleep(0.1)
        ilimb.control('little','close',297)
        time.sleep(0.1)
        #ilimb.control(['middle','ring','little'],['close']*3,[297]*3)
        #ilimb.control(['middle','ring','little'],['close']*3,[297]*3)
        #ilimb.control(['middle','ring','little'],['close']*3,[297]*3)
        #ilimb.setPose('openHand')
        print('fingers!')
        thProc.kill()

    time.sleep(0.001)

a = input('')
thProc = ThreadHandler(update)
rightTactile.start()
thProc.start()
a = input('press enter to stop')


