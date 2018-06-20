# -*- coding: utf-8 -*-
'''
#-------------------------------------------------------------------------------
# NATIONAL UNIVERSITY OF SINGAPORE - NUS
# SINGAPORE INSTITUTE FOR NEUROTECHNOLOGY - SINAPSE
# Singapore
# URL: http://www.sinapseinstitute.org
#-------------------------------------------------------------------------------
# Neuromorphic Engineering Group
# Author: Anupam Kumar Gupta, PhD
# Contact:
#-------------------------------------------------------------------------------
# Description: Braile recognition test script
#-------------------------------------------------------------------------------
'''
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#LIBRARIES
#-------------------------------------------------------------------------------
import numpy as np
from sklearn.svm import SVC
from BrailleSVMTrain import detect_peaks
#-------------------------------------------------------------------------------

def BrailleSVMPredict(testdata,SVMModelBraille):

     ### testdata
    MovAvgWin = 10
    nrows = 4
    ncols = 4
    #eakcount = np.zeros((len(dataRMat),nrows*ncols))
    peakcount = np.zeros((1,nrows*ncols))


    tmpdata = testdata
    tmpdata1 = np.zeros((np.size(tmpdata,2),nrows*ncols))
    #corrected, missing variable 'a'
    a = 0
    for nrw in range(0,nrows):
        for ncl in range(0,ncols):
            tmpdata1[:,a] = np.squeeze(tmpdata[nrw,ncl,:])
            a += 1

    for ncl1 in range(0,np.size(tmpdata1,1)):
        tmpdata2 = tmpdata1[:,ncl1]
        tmpdata3 = np.convolve(tmpdata2,np.ones(MovAvgWin)/10)
    #        plt.plot(tmpdata3)
    #        pause(2)
        #corrected to include in the loop
        tmppeaks = detect_peaks(tmpdata3,mph=300,mpd=20,show=False)
        peakcount[0,ncl1] = len(tmppeaks)
    print(peakcount,peakcount.shape)

    #corrected, it is already the feature vector, no need to use [peakcount]
    svmclassifyBraille = SVMModelBraille.predict(peakcount)

    if (svmclassifyBraille == 1):
        char = "Green"
    elif (svmclassifyBraille == 2):
        char = "Yellow"
    elif (svmclassifyBraille == 3):
        char = "Blue"
    elif(svmclassifyBraille == 4):
        char = "Red"
    else:
        char = "White"
    return char
