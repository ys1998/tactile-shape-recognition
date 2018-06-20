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
# For handling data, the class 'FeatureExtraction' should be used instead
#-------------------------------------------------------------------------------
'''
#-------------------------------------------------------------------------------
#LIBRARIES
import os, os.path
import numpy as np
import matplotlib.pyplot as plt
from sklearn.externals import joblib
#-------------------------------------------------------------------------------
class FeatureExtraction():
    #convert data from the file that are arranged
    #in a 2D array (every line contains reading from all rows for one column)
    #into a 3D array (row,col,frame)
    def convert2frames(data,nrows,ncols):
        datamat = np.zeros((nrows,ncols,np.int(np.floor(np.divide(np.size(data,0),nrows)))),dtype=int)
        c = 0
        for ii in range(0,(np.size(data,0)-nrows),nrows):

            datamat[:,:,c] = data[ii:ii+nrows,:]
            c = c+1

        return datamat

    #detect peaks
    def detect_peaks(x, mph=None, mpd=1, threshold=0, edge='rising',
                 kpsh=False, valley=False, show=False, ax=None):

        """Detect peaks in data based on their amplitude and other features.

        Parameters
        ----------
        x : 1D array_like
            data.
        mph : {None, number}, optional (default = None)
            detect peaks that are greater than minimum peak height.
        mpd : positive integer, optional (default = 1)
            detect peaks that are at least separated by minimum peak distance (in
            number of data).
        threshold : positive number, optional (default = 0)
            detect peaks (valleys) that are greater (smaller) than `threshold`
            in relation to their immediate neighbors.
        edge : {None, 'rising', 'falling', 'both'}, optional (default = 'rising')
            for a flat peak, keep only the rising edge ('rising'), only the
            falling edge ('falling'), both edges ('both'), or don't detect a
            flat peak (None).
        kpsh : bool, optional (default = False)
            keep peaks with same height even if they are closer than `mpd`.
        valley : bool, optional (default = False)
            if True (1), detect valleys (local minima) instead of peaks.
        show : bool, optional (default = False)
            if True (1), plot data in matplotlib figure.
        ax : a matplotlib.axes.Axes instance, optional (default = None).

        Returns
        -------
        ind : 1D array_like
            indeces of the peaks in `x`.

        Notes
        -----
        The detection of valleys instead of peaks is performed internally by simply
        negating the data: `ind_valleys = detect_peaks(-x)`

        The function can handle NaN's

        See this IPython Notebook [1]_.

        References
        ----------
        .. [1] http://nbviewer.ipython.org/github/demotu/BMC/blob/master/notebooks/DetectPeaks.ipynb

        Examples
        --------
        >>> from detect_peaks import detect_peaks
        >>> x = np.random.randn(100)
        >>> x[60:81] = np.nan
        >>> # detect all peaks and plot data
        >>> ind = detect_peaks(x, show=True)
        >>> print(ind)

        >>> x = np.sin(2*np.pi*5*np.linspace(0, 1, 200)) + np.random.randn(200)/5
        >>> # set minimum peak height = 0 and minimum peak distance = 20
        >>> detect_peaks(x, mph=0, mpd=20, show=True)

        >>> x = [0, 1, 0, 2, 0, 3, 0, 2, 0, 1, 0]
        >>> # set minimum peak distance = 2
        >>> detect_peaks(x, mpd=2, show=True)

        >>> x = np.sin(2*np.pi*5*np.linspace(0, 1, 200)) + np.random.randn(200)/5
        >>> # detection of valleys instead of peaks
        >>> detect_peaks(x, mph=0, mpd=20, valley=True, show=True)

        >>> x = [0, 1, 1, 0, 1, 1, 0]
        >>> # detect both edges
        >>> detect_peaks(x, edge='both', show=True)

        >>> x = [-2, 1, -2, 2, 1, 1, 3, 0]
        >>> # set threshold = 2
        >>> detect_peaks(x, threshold = 2, show=True)
        """

        x = np.atleast_1d(x).astype('float64')
        if x.size < 3:
            return np.array([], dtype=int)
        if valley:
            x = -x
        # find indices of all peaks
        dx = x[1:] - x[:-1]
        # handle NaN's
        indnan = np.where(np.isnan(x))[0]
        if indnan.size:
            x[indnan] = np.inf
            dx[np.where(np.isnan(dx))[0]] = np.inf
        ine, ire, ife = np.array([[], [], []], dtype=int)
        if not edge:
            ine = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) > 0))[0]
        else:
            if edge.lower() in ['rising', 'both']:
                ire = np.where((np.hstack((dx, 0)) <= 0) & (np.hstack((0, dx)) > 0))[0]
            if edge.lower() in ['falling', 'both']:
                ife = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) >= 0))[0]
        ind = np.unique(np.hstack((ine, ire, ife)))
        # handle NaN's
        if ind.size and indnan.size:
            # NaN's and values close to NaN's cannot be peaks
            ind = ind[np.in1d(ind, np.unique(np.hstack((indnan, indnan-1, indnan+1))), invert=True)]
        # first and last values of x cannot be peaks
        if ind.size and ind[0] == 0:
            ind = ind[1:]
        if ind.size and ind[-1] == x.size-1:
            ind = ind[:-1]
        # remove peaks < minimum peak height
        if ind.size and mph is not None:
            ind = ind[x[ind] >= mph]
        # remove peaks - neighbors < threshold
        if ind.size and threshold > 0:
            dx = np.min(np.vstack([x[ind]-x[ind-1], x[ind]-x[ind+1]]), axis=0)
            ind = np.delete(ind, np.where(dx < threshold)[0])
        # detect small peaks closer than minimum peak distance
        if ind.size and mpd > 1:
            ind = ind[np.argsort(x[ind])][::-1]  # sort ind by peak height
            idel = np.zeros(ind.size, dtype=bool)
            for i in range(ind.size):
                if not idel[i]:
                    # keep peaks with the same height if kpsh is True
                    idel = idel | (ind >= ind[i] - mpd) & (ind <= ind[i] + mpd) \
                        & (x[ind[i]] > x[ind] if kpsh else True)
                    idel[i] = 0  # Keep current peak
            # remove the small peaks and sort back the indices by their occurrence
            ind = np.sort(ind[~idel])

        if show:
            if indnan.size:
                x[indnan] = np.nan
            if valley:
                x = -x
            _plot(x, mph, mpd, threshold, edge, valley, ax, ind)

        return ind

    def _plot(x, mph, mpd, threshold, edge, valley, ax, ind):
        """Plot results of the detect_peaks function, see its help."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print('matplotlib is not available.')
        else:
            if ax is None:
                _, ax = plt.subplots(1, 1, figsize=(8, 4))

            ax.plot(x, 'b', lw=1)
            if ind.size:
                label = 'valley' if valley else 'peak'
                label = label + 's' if ind.size > 1 else label
                ax.plot(ind, x[ind], '+', mfc=None, mec='r', mew=2, ms=8,
                        label='%d %s' % (ind.size, label))
                ax.legend(loc='best', framealpha=.5, numpoints=1)
            ax.set_xlim(-.02*x.size, x.size*1.02-1)
            ymin, ymax = x[np.isfinite(x)].min(), x[np.isfinite(x)].max()
            yrange = ymax - ymin if ymax > ymin else 1
            ax.set_ylim(ymin - 0.1*yrange, ymax + 0.1*yrange)
            ax.set_xlabel('Data #', fontsize=14)
            ax.set_ylabel('Amplitude', fontsize=14)
            mode = 'Valley detection' if valley else 'Peak detection'
            ax.set_title("%s (mph=%s, mpd=%d, threshold=%s, edge='%s')"
                         % (mode, str(mph), mpd, str(threshold), edge))
            # plt.grid()
            plt.show()
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
class Braille():
    #constant -> points to the folder containing the palpation data
    dataFolderPath = './NewData_BRC/'
    def __init__(self):
        #pre-loads an SVM model
        #the model should be stored inside the folder containing experimental data
        mdlfname = Braille.dataFolderPath+'SVMModelBraille.pkl'
        #check if the file exists
        if os.path.isfile(mdlfname):
            #if the file exists, load it to the internal SVM model
            self.SVMmodel = joblib.load(mdlfname)
        else: #otherwise, print an error message and let the SVM model be None
            print('could not find a pre-loaded SVM model')
            self.SVMmodel = None

    #loads a file containing tactile data for braille recognition
    def loadDataFile(self,filepath):
        if os.path.isfile(filepath):
            return np.loadtxt(filepath)
        else:
            return False

    #load a different SVM model
    def loadModelSVM(self,filepath):
        if os.path.isfile(filepath):
            self.SVMmodel = joblib.load(filepath) #loads the SVM model
        else:
            return False #could not find the file

    #train a novel SVM model
    def trainSVM(self):
        print('ok')

    #classify a new input pattern
    def classify(self,testdata):
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
            tmppeaks = FeatureExtraction.detect_peaks(tmpdata3,mph=300,mpd=20,show=False)
            peakcount[0,ncl1] = len(tmppeaks)
        print(peakcount,peakcount.shape)

        #corrected, it is already the feature vector, no need to use [peakcount]
        svmclassifyBraille = self.SVMmodel.predict(peakcount)

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
