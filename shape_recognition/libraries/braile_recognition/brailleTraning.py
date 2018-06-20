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
# Description: Testing the braille class
#-------------------------------------------------------------------------------
'''
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#LIBRARIES
import os, os.path, sys
sys.path.append('../general')
import numpy as np
import scipy as sp
from sklearn.externals import joblib
from dataprocessing import * #import the detect_peaks method
from braille import *
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
NROWS = 4 #number of rows in the tactile array
NCOLS = 4 #number of columns in the tactile array

#training data coming from the text files
#70% training
files = [   'NewData_BRC/BRC_Y1.txt',
            'NewData_BRC/BRC_Y2.txt',
            'NewData_BRC/BRC_Y3.txt',
            'NewData_BRC/BRC_Y4.txt',
            'NewData_BRC/BRC_Y5.txt',
            'NewData_BRC/BRC_Y6.txt',
            'NewData_BRC/BRC_Y7.txt',
            'NewData_BRC/BRC_B1.txt',
            'NewData_BRC/BRC_B2.txt',
            'NewData_BRC/BRC_B3.txt',
            'NewData_BRC/BRC_B4.txt',
            'NewData_BRC/BRC_B5.txt',
            'NewData_BRC/BRC_B6.txt',
            'NewData_BRC/BRC_B7.txt',
            'NewData_BRC/BRC_G1.txt',
            'NewData_BRC/BRC_G2.txt',
            'NewData_BRC/BRC_G3.txt',
            'NewData_BRC/BRC_G4.txt',
            'NewData_BRC/BRC_G5.txt',
            'NewData_BRC/BRC_G6.txt',
            'NewData_BRC/BRC_G7.txt',
            'NewData_BRC/BRC_W1.txt',
            'NewData_BRC/BRC_W2.txt',
            'NewData_BRC/BRC_W3.txt',
            'NewData_BRC/BRC_W4.txt',
            'NewData_BRC/BRC_W5.txt',
            'NewData_BRC/BRC_W6.txt',
            'NewData_BRC/BRC_W7.txt',
            'NewData_BRC/BRC_R1.txt',
            'NewData_BRC/BRC_R2.txt',
            'NewData_BRC/BRC_R3.txt',
            'NewData_BRC/BRC_R4.txt',
            'NewData_BRC/BRC_R5.txt',
            'NewData_BRC/BRC_R6.txt',
            'NewData_BRC/BRC_R7.txt',
        ]
#training data
training = BrailleHandler.createTrainingData(files,NROWS,NCOLS,filt=True)
#labels or clases
labels = [1,1,1,1,1,1,1,2,2,2,2,2,2,2,3,3,3,3,3,3,3,4,4,4,4,4,4,4,5,5,5,5,5,5,5]

#creating a SVM classifier for Braille
brailleSVM = Braille()
#training the SVM model
brailleSVM.train(training,labels)
print(brailleSVM.modelSVM)

#classifying data
testData = BrailleHandler.loadFile('NewData_BRC/BRC_B10.txt')
testData = BrailleHandler.convert2vector(testData,NROWS,NCOLS)
peakTh = 300
features = BrailleHandler.countPeaks(testData,peakTh)
#print the feature vector
print(features)
#classification
resp = brailleSVM.classify(features.reshape(1,-1))
print(resp)

#save the SVM model
brailleSVM.save('newbraillesvm')
#-------------------------------------------------------------------------------
