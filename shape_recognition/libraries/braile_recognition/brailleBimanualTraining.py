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
files = [   'bimanual_data/sliding_braille_data_2p_1.txt',
            'bimanual_data/sliding_braille_data_2p_2.txt',
            'bimanual_data/sliding_braille_data_2p_3.txt',
            'bimanual_data/sliding_braille_data_2p_4.txt',
            'bimanual_data/sliding_braille_data_2p_5.txt',
            'bimanual_data/sliding_braille_data_2p_6.txt',
            'bimanual_data/sliding_braille_data_2p_7.txt',
            'bimanual_data/sliding_braille_data_2p_8.txt',
            'bimanual_data/sliding_braille_data_4p_1.txt',
            'bimanual_data/sliding_braille_data_4p_2.txt',
            'bimanual_data/sliding_braille_data_4p_3.txt',
            'bimanual_data/sliding_braille_data_4p_4.txt',
            'bimanual_data/sliding_braille_data_4p_5.txt',
            'bimanual_data/sliding_braille_data_4p_6.txt',
            'bimanual_data/sliding_braille_data_4p_7.txt',
            'bimanual_data/sliding_braille_data_4p_8.txt',
        ]
#training data
training = BrailleHandler.createTrainingData(files,NROWS,NCOLS,filt=True)
#labels or clases
labels = [1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2]

#creating a SVM classifier for Braille
brailleSVM = Braille()
#training the SVM model
brailleSVM.train(training,labels)
print(brailleSVM.modelSVM)

#classifying data
testData = BrailleHandler.loadFile('bimanual_data/sliding_braille_data_4p_10.txt')
testData = BrailleHandler.convert2vector(testData)
peakTh = 0.03
features = BrailleHandler.countPeaks(testData,peakTh)
#print the feature vector
print(features)
#classification
resp = brailleSVM.classify(features.reshape(1,-1))
print(resp)

#save the SVM model
brailleSVM.save('bimanualbraillesvm')
#-------------------------------------------------------------------------------
