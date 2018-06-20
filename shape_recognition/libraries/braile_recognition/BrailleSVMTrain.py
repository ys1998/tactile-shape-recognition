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
from __future__ import division, print_function
import numpy as np
import glob
#import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.externals import joblib

#from __future__ import division, print_function

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

def sensorData3DMat(data,nrows,ncols):
        datamat = np.zeros((nrows,ncols,np.int(np.floor(np.divide(np.size(data,0),nrows)))),dtype=int)
        c = 0
        for ii in range(0,(np.size(data,0)-nrows),nrows):

            datamat[:,:,c] = data[ii:ii+nrows,:]
            c = c+1

        return datamat

#from detect_peaks import detect_peaks

def BrailleSVMTrain(traindatapath,fnameG,fnameY,fnameB,fnameR,fnameW,fext):

    fpath = traindatapath
    fname1 = fnameG
    fname2 = fnameY
    fname3 = fnameB
    fname4 = fnameR
    fname5 = fnameW

#    fpath = "C:\Users\\anupa\Desktop\ShapeRecognition\BrailleDataNewLego";
#    fname1 = "Braille_G";
#    fname2 = "Braille_Y";
#    fname3 = "Braille_B";
#    fname4 = "Braille_R";
#    fname5 = "Braille_W";
#    fext = ".txt";

    ### Read text files for each Braille character
    ### G
    filesG = glob.glob("%s\%s*%s"%(fpath,fname1,fext))
    nrows = 4;
    ncols = 4;
    dataGMat = [];

    for iG in range(0,np.size(filesG)):
        fnameG = filesG[iG]
        dataG = np.loadtxt(fnameG)
        tmpdataG = sensorData3DMat(dataG,nrows,ncols)
        dataGMat.append(tmpdataG)

    ### Y
    filesY = glob.glob("%s\%s*%s"%(fpath,fname2,fext))
    nrows = 4;
    ncols = 4;
    dataYMat = [];

    for iY in range(0,np.size(filesY)):
        fnameY = filesY[iY]
        dataY = np.loadtxt(fnameY)
        tmpdataY = sensorData3DMat(dataY,nrows,ncols)
        dataYMat.append(tmpdataY)


    ### B
    filesB = glob.glob("%s\%s*%s"%(fpath,fname3,fext))
    nrows = 4;
    ncols = 4;
    dataBMat = [];

    for iB in range(0,np.size(filesB)):
        fnameB = filesB[iB]
        dataB = np.loadtxt(fnameB)
        tmpdataB = sensorData3DMat(dataB,nrows,ncols)
        dataBMat.append(tmpdataB)


    ### R
    filesR = glob.glob("%s\%s*%s"%(fpath,fname4,fext))
    nrows = 4;
    ncols = 4;
    dataRMat = [];

    for iR in range(0,np.size(filesR)):
        fnameR = filesR[iR]
        dataR = np.loadtxt(fnameR)
        tmpdataR = sensorData3DMat(dataR,nrows,ncols)
        dataRMat.append(tmpdataR)


    ### W
    filesW = glob.glob("%s\%s*%s"%(fpath,fname5,fext))
    nrows = 4;
    ncols = 4;
    dataWMat = [];

    for iW in range(0,np.size(filesW)):
        fnameW = filesW[iW]
        dataW = np.loadtxt(fnameW)
        tmpdataW = sensorData3DMat(dataW,nrows,ncols)
        dataWMat.append(tmpdataW)


    ###########################################################################

    #### Smooth data and find peaks and store in a vector
    ### G
    MovAvgWin = 10
    peakcountG = np.zeros((len(dataGMat),nrows*ncols))
    for gg in range(0,len(dataGMat)):

        tmpdata = dataGMat[gg]
        a = 0
        tmpdata1 = np.zeros((np.size(tmpdata,2),nrows*ncols))
        for nrw in range(0,nrows):
            for ncl in range(0,ncols):
                tmpdata1[:,a] = np.squeeze(tmpdata[nrw,ncl,:])
                a = a+1

        for ncl1 in range(0,np.size(tmpdata1,1)):
            tmpdata2 = tmpdata1[:,ncl1]
            tmpdata3 = np.convolve(tmpdata2,np.ones(MovAvgWin)/10)
    #        plt.plot(tmpdata3)
    #        pause(2)
            tmppeaks = detect_peaks(tmpdata3,mph=300,mpd=20,show=False)
            peakcountG[gg,ncl1] = len(tmppeaks)

    peakcountG = np.append(peakcountG,np.ones((np.size(peakcountG,0),1)),axis=1)


    ### Y
    MovAvgWin = 10
    peakcountY = np.zeros((len(dataYMat),nrows*ncols))
    for yy in range(0,len(dataYMat)):

        tmpdata = dataYMat[yy]
        a = 0
        tmpdata1 = np.zeros((np.size(tmpdata,2),nrows*ncols))
        for nrw in range(0,nrows):
            for ncl in range(0,ncols):
                tmpdata1[:,a] = np.squeeze(tmpdata[nrw,ncl,:])
                a = a+1

        for ncl1 in range(0,np.size(tmpdata1,1)):
            tmpdata2 = tmpdata1[:,ncl1]
            tmpdata3 = np.convolve(tmpdata2,np.ones(MovAvgWin)/10)
    #        plt.plot(tmpdata3)
    #        pause(2)
            tmppeaks = detect_peaks(tmpdata3,mph=300,mpd=20,show=False)
            peakcountY[yy,ncl1] = len(tmppeaks)

    peakcountY = np.append(peakcountY,2*np.ones((np.size(peakcountY,0),1)),axis=1)


    ### B
    MovAvgWin = 10
    peakcountB = np.zeros((len(dataBMat),nrows*ncols))
    for bb in range(0,len(dataBMat)):

        tmpdata = dataBMat[bb]
        a = 0
        tmpdata1 = np.zeros((np.size(tmpdata,2),nrows*ncols))
        for nrw in range(0,nrows):
            for ncl in range(0,ncols):
                tmpdata1[:,a] = np.squeeze(tmpdata[nrw,ncl,:])
                a = a+1

        for ncl1 in range(0,np.size(tmpdata1,1)):
            tmpdata2 = tmpdata1[:,ncl1]
            tmpdata3 = np.convolve(tmpdata2,np.ones(MovAvgWin)/10)
    #        plt.plot(tmpdata3)
    #        pause(2)
            tmppeaks = detect_peaks(tmpdata3,mph=300,mpd=20,show=False)
            peakcountB[bb,ncl1] = len(tmppeaks)

    peakcountB = np.append(peakcountB,3*np.ones((np.size(peakcountB,0),1)),axis=1)


    ### R
    MovAvgWin = 10
    peakcountR = np.zeros((len(dataRMat),nrows*ncols))
    for rr in range(0,len(dataRMat)):

        tmpdata = dataRMat[rr]
        a = 0
        tmpdata1 = np.zeros((np.size(tmpdata,2),nrows*ncols))
        for nrw in range(0,nrows):
            for ncl in range(0,ncols):
                tmpdata1[:,a] = np.squeeze(tmpdata[nrw,ncl,:])
                a = a+1

        for ncl1 in range(0,np.size(tmpdata1,1)):
            tmpdata2 = tmpdata1[:,ncl1]
            tmpdata3 = np.convolve(tmpdata2,np.ones(MovAvgWin)/10)
    #        plt.plot(tmpdata3)
    #        pause(2)
            tmppeaks = detect_peaks(tmpdata3,mph=300,mpd=20,show=False)
            peakcountR[rr,ncl1] = len(tmppeaks)

    peakcountR = np.append(peakcountR,4*np.ones((np.size(peakcountR,0),1)),axis=1)


    ### W
    MovAvgWin = 10
    peakcountW = np.zeros((len(dataWMat),nrows*ncols))
    for ww in range(0,len(dataWMat)):

        tmpdata = dataWMat[ww]
        a = 0
        tmpdata1 = np.zeros((np.size(tmpdata,2),nrows*ncols))
        for nrw in range(0,nrows):
            for ncl in range(0,ncols):
                tmpdata1[:,a] = np.squeeze(tmpdata[nrw,ncl,:])
                a = a+1

        for ncl1 in range(0,np.size(tmpdata1,1)):
            tmpdata2 = tmpdata1[:,ncl1]
            tmpdata3 = np.convolve(tmpdata2,np.ones(MovAvgWin)/10)
    #        plt.plot(tmpdata3)
    #        pause(2)
            tmppeaks = detect_peaks(tmpdata3,mph=300,mpd=20,show=False)
            peakcountW[ww,ncl1] = len(tmppeaks)

    peakcountW = np.append(peakcountW,5*np.ones((np.size(peakcountW,0),1)),axis=1)


    ### SVM Training
    trainExNo = np.size(peakcountG,0)
#    testExNo = 3
    featureNo = 16;
    trainingdata = np.vstack((peakcountG[0:trainExNo,0:featureNo],peakcountY[0:trainExNo,0:featureNo],peakcountB[0:trainExNo,0:featureNo],peakcountR[0:trainExNo,0:featureNo],peakcountW[0:trainExNo,0:featureNo]))
#    testdata = np.vstack((peakcountG[trainExNo:trainExNo+testExNo,0:featureNo],peakcountY[trainExNo:trainExNo+testExNo,0:featureNo],peakcountB[trainExNo:trainExNo+testExNo,0:featureNo],peakcountR[trainExNo:trainExNo+testExNo,0:featureNo],peakcountW[trainExNo:trainExNo+testExNo,0:featureNo]))
    trainlabels = np.vstack((peakcountG[0:trainExNo,featureNo],peakcountY[0:trainExNo,featureNo],peakcountB[0:trainExNo,featureNo],peakcountR[0:trainExNo,featureNo],peakcountW[0:trainExNo,featureNo]))
    trainlabels = np.reshape(trainlabels,[np.size(trainingdata,0),1])
#    testlabels = np.vstack((peakcountG[trainExNo:trainExNo+testExNo,featureNo],peakcountY[trainExNo:trainExNo+testExNo,featureNo],peakcountB[trainExNo:trainExNo+testExNo,featureNo],peakcountR[trainExNo:trainExNo+testExNo,featureNo],peakcountW[trainExNo:trainExNo+testExNo,featureNo]))
#    testlabels = np.reshape(testlabels,[np.size(testdata,0),1])

    ### Train SVM
    SVMModelBraille = SVC()
    SVMModelBraille.fit(trainingdata,np.ravel(trainlabels))

    #### Save Trained SVM Model
    mdlfname = "%s\%s%s"%(fpath,"SVMModelBraille",".pkl")
    joblib.dump(SVMModelBraille,mdlfname)

#    ### Test SVM
#    svmclassifyBraille = SVMModelBraille.predict([testdata[10,:]])
    return ()
