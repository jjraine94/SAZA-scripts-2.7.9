def DistanceFromSource(TMin, TMax):

    import Tkinter, tkFileDialog
    import math
    import numpy as np
    from scipy import stats
    import pandas as pd
    import os
    import re

    # root = Tkinter.Tk()
    # root.withdraw()
    # data_folder = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select folder containing fish data:')
    # data_folder = '%s/FishData' % data_folder
    data_folder = raw_input("Input name of folder containing LoadData output: ")
    data_folder = '%s/FishData' % data_folder
    save_folder = os.path.dirname(data_folder)

    # Get distance for probability distribution
    X_mm = 30
    Y_mm = 75
    Diag_mm = math.sqrt(X_mm**2 + Y_mm**2)
    # Create list of values from 1 to Diag_mm
    pts = list(range(1,int(Diag_mm)+1))

    # Write helper function to import csv files in correct order
    _nsre = re.compile('([0-9]+)')
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(_nsre, s)]

    # Get (and sort) all csv files in folder
    csvfiles = []
    for File in os.listdir(data_folder):
        if File.endswith('.csv'):
            csvfiles.append(os.path.join(data_folder, File))
    csvfiles.sort(key=natural_sort_key)

    data = pd.DataFrame(columns = ['Fish Number', 'Mean dist','Median dist','SD dist','Max time spent dist',
                                   'Area 25','Area 50','Area 75'])
    mean_dist = []
    median_dist = []
    std_dist = []
    max_time_spent_dist = []
    area25 = []
    area50 = []
    area75 = []
    area100 = []
    for i in range(1, len(csvfiles)+1):
        print('Fish %s' % i)
        File = pd.read_csv(csvfiles[i-1])

        # Convert time to frames
        TMin1 = int(round(File['Sampling_Rate'][0]*TMin))
        TMax1 = int(round(File['Sampling_Rate'][0]*TMax))

        X = File['X'][TMin1:TMax1]
        X = X.tolist()
        if csvfiles[i-1][-5] == 'R':
            X = [30 - x for x in X]
        Y = File['Y'][TMin1:TMax1]
        Y = [75 - y for y in Y]
        XY = [X, Y] # make this a 3D structure
        Dist_from_source = []

        # Find distance from source as hypotenuse
        for j in range(len(X)):
            Dist_from_source.append(math.sqrt(XY[0][j]**2 + XY[1][j]**2))

        kde = stats.gaussian_kde(Dist_from_source)
        p = kde(pts)
        data = data.append({'Fish Number': int(i), 'Mean dist': np.mean(Dist_from_source), 'Median dist': np.median(Dist_from_source),
                            'SD dist': np.std(Dist_from_source), 'Max time spent dist': np.argmax(p)+1,
                            'Area 25': np.trapz(p[:19]), 'Area 50':np.trapz(p[20:38]),
                            'Area 75': np.trapz(p[39:57]), 'Area 100': np.trapz(p[58:])}, ignore_index=True)

    # save file
    filename = raw_input('Enter file name for saving:')
    data.to_csv('%s/%s.csv' % (save_folder, filename), float_format= '%.12f',index=False)
