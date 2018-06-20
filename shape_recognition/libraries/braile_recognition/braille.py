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
# Description: defines classes for processing tactile data to be used for
# braille recognition.
# The 'Braille' class stores the SVM model used to recognize braille characters.
# this class abstracts the process of data processing, meaning that it only deals
# with the data ready for training and/or classification procedures.
# For handling data, the class 'BrailleHandler' should be used instead
#-------------------------------------------------------------------------------
'''
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#LIBRARIES
import os, os.path, sys
sys.path.append('../general')
import numpy as np
import scipy as sp
from sklearn.svm import SVC
from sklearn.externals import joblib
from dataprocessing import * #import the detect_peaks method
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#Feature extraction for SVM-based braille classification
class BrailleHandler():
    #---------------------------------------------------------------------------
    #read a file and return the data
    def loadFile(filepath):
        if os.path.isfile(filepath):
            #return the data contained in the data
            return np.loadtxt(filepath)
        else:
            return False #file not found

    def convert2vector(data):
        return np.transpose(data)

    #convert the data from a file into a vector
    def oldconvert2vector(data,nrows,ncols):
        #first convert to 3D matrix
        datamat = BrailleHandler.oldconvert2frames(data,nrows,ncols)
        numsamples = np.size(datamat,2) #number of samples or frames
        dataVector = np.zeros((nrows*ncols,numsamples))
        taxelCounter = 0
        for i in range(nrows):
            for j in range(ncols):
                dataVector[taxelCounter] = datamat[i,j,:]
                taxelCounter+=1
        return dataVector #return the dataVector

    #convert data from the file that are arranged
    #in a 2D array (every line contains reading from all rows for one column)
    #into a 3D array (row,col,frame)
    def oldconvert2frames(data,nrows,ncols):
        datamat = np.zeros((nrows,ncols,np.int(np.floor(np.divide(np.size(data,0),nrows)))),dtype=int)
        c = 0
        for ii in range(0,(np.size(data,0)-nrows),nrows):
            datamat[:,:,c] = data[ii:ii+nrows,:]
            c = c+1
        return datamat #return the 3D matrix
    #---------------------------------------------------------------------------
    #find the number of peaks in every single taxel
    def countPeaks(inputMatrix,threshold):
        if len(inputMatrix.shape) == 3: #3D matrix
            nrows = inputMatrix.shape[0] #number of rows
            ncols = inputMatrix.shape[1] #number of columns
            nsamples = inputMatrix.shape[2] #number of samples
            #feature vector containing the number of peaks for
            #each taxel of the tactile sensor
            featureVector = np.zeros(nrows*ncols)
            #matrix M*NxT where each row corresponds to a taxel and the
            #columns to the time series signal
            tactileSignal = np.zeros((nrows*ncols,nsamples))
            #counter for the index of the tactileSignal matrix
            counter = 0
            #loop through the rows
            for k in range(nrows):
                #loop through the columns
                for w in range(ncols):
                    #get a single taxel signal
                    tactileSignal[counter] = inputMatrix[k,w,:]
                    #count the number of peaks in the signal
                    #and built the feature vector
                    #find the peaks
                    tmppeaks = detect_peaks(tactileSignal[counter],mph=threshold,mpd=20,show=False)
                    #number of peaks is the length of 'tmppeaks'
                    featureVector[counter] = len(tmppeaks)
                    #increment the counter
                    counter+=1
        #list of list, every element of the list corresponds to
        #the time series of a single taxel
        else:
            #find the total number of taxels in the tactile array
            numberTaxels = len(inputMatrix)
            #feature vector containing the number of peaks for
            #each taxel of the tactile sensor
            featureVector = np.zeros(numberTaxels)
            #scan all the taxels
            for k in range(numberTaxels):
                #find the peaks
                tmppeaks = detect_peaks(inputMatrix[k],mph=threshold,mpd=20,show=False)
                #number of peaks is the length of 'tmppeaks'
                featureVector[k] = len(tmppeaks)
        #return the feature vector
        return featureVector
        #-------------------------------------------------------------------------------
    #create the training data based on the list of the text files to be loaded
    #and the labels corresponding for each text data
    def createTrainingData(dataFiles,nrows,ncols,filt=False):
        for k in range(len(dataFiles)):
            #get the filename
            filename = dataFiles[k]
            #load the data
            datafile = BrailleHandler.loadFile(filename)
            #convert to vector
            #datavector = BrailleHandler.oldconvert2vector(datafile,nrows,ncols)
            datavector = BrailleHandler.convert2vector(datafile)
            #if data should be filtered
            if filt == True:
                #for every taxel
                for i in range(np.size(datavector,0)):
                    mva = MovingAverage() #window size = 10, sampfreq = 100 Hz
                    #for every sample, get the moving average response
                    for z in range(np.size(datavector,1)):
                        datavector[i,z] = mva.getSample(datavector[i,z])
            #find the number of peaks
            peakTh = 0.05 #threshold for peak detection
            #create the feature vector
            featurevector = BrailleHandler.countPeaks(datavector,peakTh)
            #if it is the first iteration, create the training data
            if k != 0:
                trainingData = np.vstack((trainingData,featurevector))
            else:
                trainingData = featurevector
        return trainingData
#-------------------------------------------------------------------------------
#Braille Recognition Class
class Braille():
    def __init__(self):
        #labels for every class
        #dictionary to associate label names and values
        self.classes = dict()
        #SVM model
        self.modelSVM = None
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    #load a pre-trained SVM model from a file
    def load(self,filepath):
        #checks if the file exists
        if os.path.isfile(filepath):
            self.modelSVM = joblib.load(filepath) #loads the SVM model
            return True #load ok
        else:
            return False #file not found
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    #save a new SVM model
    def save(self,filename):
        #saving
        joblib.dump(self.modelSVM,filename+'.pkl')
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    #train a SVM model
    def train(self,trainingData,labels):
        #create a new SVM model
        self.modelSVM = SVC()
        #pass the training data and the labels for training
        self.modelSVM.fit(trainingData,labels)
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    #classification
    #features should be a feature vector following the same pattern
    #that was used for training
    def classify(self,features):
        #check if there is a SVM model to classify the data
        if self.modelSVM is not None:
            #classify based on the input features
            svmResp = self.modelSVM.predict(features)
            #return the output of the classifier
            return svmResp
        else:
            return False
    #---------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__=='__main__':
    #---------------------------------------------------------------------------
    import numpy as np #numpy
    import matplotlib.pyplot as plt #matplotlib
    NROWS = 4 #number of columns in the tactile array
    NCOLS = 4 #number of lines in the tactile array
    peakTh = 300 #threshold for detecting peaks
    #load the braille data from file
    #2D matrix
    datafile = np.loadtxt('NewData_BRC/BRC_B1.txt')
    #convert data to a 3D matrix
    tactileData = BrailleHandler.oldconvert2frames(datafile,NROWS,NCOLS)
    #feature vector containing the number of peaks for each taxel
    features = BrailleHandler.countPeaks(tactileData,peakTh)
    #---------------------------------------------------------------------------
    #feature extraction with 2D array
    #moving average of the 2D matrix
    #create a moving average object
    #default parameters, windowsize = 10, sampfreq = 100 Hz
    mva = MovingAverage()
    tactileVector = BrailleHandler.oldconvert2vector(datafile,NROWS,NCOLS)
    numsamples = np.size(tactileData,2) #total number of samples
    tactileMVA = np.zeros((NROWS*NCOLS,numsamples))
    counter = 0 #taxel counter
    for k in range(NROWS*NCOLS): #scan all the columns
        for z in range(numsamples): #filtering the signal sample by sample
            tactileMVA[counter,z] = mva.getSample(tactileVector[k,z])
        counter+=1 #increment the taxel counter
    #with the filtered data, count peaks again
    filtFeatures = BrailleHandler.countPeaks(tactileMVA,peakTh)
    #print the filtered feature vector
    print(filtFeatures)