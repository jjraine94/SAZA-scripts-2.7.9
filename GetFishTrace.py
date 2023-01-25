def GetFishTrace(file, num):
    """Hard to explain what this does

    Sentence about what it does
    (Python equivalent of Matlab function Get_FishTrace)

    Args:
        file: definition
        num: definition

    Returns:
        What it returns
    """

    # import csv, math
    import numpy as np
    # import pandas as pd

    data = {}

    if num == 1:
        X = file['cXmm001']
        Y = file['cYmm001']
        data['ROI_1'] = file['FBSA001']
        data['ROI_3'] = file['FBSA003']
        data['ROI_4'] = file['FBSA005']
    elif num == 2:
        X = file['cXmm002']
        Y = file['cYmm002']
        data['ROI_2'] = file['FBSA002']
        data['ROI_5'] = file['FBSA004']
        data['ROI_6'] = file['FBSA006']

    Diff_Time = (file['Timestamp'].iloc[-1] - min(file['Timestamp']))/1000
    data['Sampling_Rate'] = 1/(float(Diff_Time)/file['Timestamp'].size)

    data['T'] = file['Timestamp']/1000
    data['X'] = X
    data['Y'] = Y
    data['xmax'] = max(X)
    data['ymax'] = max(Y)

    data['dX'] = X.iloc[1:] - X.iloc[0:-1].values
    data['dY'] = Y[1:] - Y[0:-1].values
    data['dT'] = data['T'][1:] - data['T'][0:-1].values

    VX = data['dX']/data['dT']
    VY = data['dY']/data['dT']
    data['V'] = np.sqrt(VX.pow(2)+VY.pow(2))

    data['NFish'] =1
    return(data)
