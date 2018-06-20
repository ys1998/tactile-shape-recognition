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
from BrailleSVMTrain import BrailleSVMTrain
from BrailleSVMPredict import BrailleSVMPredict
from sklearn.externals import joblib
import os, sys
sys.path.append('/NewData_BRC')
### Test SVM functions
#-------------------------------------------------------------------------------
fpath = "./NewData_BRC/";
fname1 = "BRC_G";
fname2 = "BRC_Y";
fname3 = "BRC_B";
fname4 = "BRC_R";
fname5 = "BRC_W";
fext = ".txt";

BrailleSVMTrain(fpath,fname1,fname2,fname3,fname4,fname5,fext)

    ### Load Trained SVM Model
mdlfname = "%s\%s%s"%(fpath,"SVMModelBraille",".pkl")
SVMModelBraille = joblib.load(mdlfname)
print(SVMModelBraille)
#svmclassify = BrailleSVMPredict(testdata,SVMModelBraille)
