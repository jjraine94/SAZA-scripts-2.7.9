def Sparklines_full():
    import os
    import shutil
    import re
    from matplotlib import pyplot as plt
    import pandas as pd
    import numpy as np
    from copy import copy
    # import Tkinter, tkFileDialog

    duration = 1440 # total experiment duration (s)
    pre = 180 # pre-stimulus duration (s)
    post = 180 # post-stimulus duration (s)
    cutoff = 1.5 # minimum cutoff for gray color (s)
    line_color = "black" # color for lines exceeding cutoff

    # root = Tkinter.Tk()
    # root.withdraw()
    # data_folder = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select folder containing fish data:')
    # data_folder = '%s/FishData' % data_folder
    data_folder = raw_input("Input name of folder containing LoadData output: ")
    data_folder = '%s/FishData' % data_folder
    save_folder=os.path.dirname(data_folder)

    Bin_Lengths = ['0-1', '1-1000', '1000-2000', '2000-3000', '3000-5000','5000-8000',
                       '8000-11000', '11000-15000', '15000-20000'] # in miliseconds

    if os.path.exists(save_folder+'/SparkFigures_Fuller'):
            shutil.rmtree(save_folder+'/SparkFigures_Fuller')
    os.makedirs(save_folder+'/SparkFigures_Fuller')

    _nsre = re.compile('([0-9]+)')
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(_nsre, s)]
    csvfiles = []
    for File in os.listdir(data_folder):
        if File.startswith('Fish {') and File.endswith('.csv'):
            csvfiles.append(os.path.join(data_folder, File))
    csvfiles.sort(key=natural_sort_key)
    iMax = len(csvfiles)

    # every fish whose data we have
    for i in range(0, iMax):
        print('Fish..' + str(i+1))
        df=pd.read_csv(csvfiles[i])
        cnames = df.columns.tolist()

        TMin = 0
        TMax = duration
        TMin1 = int(round(df['Sampling_Rate'][0]*TMin))
        TMax1 = int(round(df['Sampling_Rate'][0]*TMax))
        Seconds = int(round(df['Sampling_Rate'][0]*cutoff))

        # initialize x variable x_time
        time = df['T']
        x_time = []
        min_time = min(time)
        x_time[:] = [x - min_time for x in time]

        if csvfiles[i][-5] == 'L':
            stimcoords = np.array([ [0,50], [0,75], [15,50], [15,75] ])
            ctrlcoords = np.array([ [15,50], [15,75], [30,50], [30,75] ])
        else:
            stimcoords = np.array([ [15,50], [15,75], [30,50], [30,75] ])
            ctrlcoords = np.array([ [0,50], [0,75], [15,50], [15,75] ])

        stim = InROI(df, Coordinates=stimcoords, TMin = TMin1, TMax = TMax1)
        ctrl = InROI(df, Coordinates=ctrlcoords, TMin = TMin1, TMax = TMax1)
        ctrl = np.negative(ctrl)

        if stim[-1]!=0 or ctrl[-1]!=0:
           stim=np.append(stim, 0)
           ctrl=np.append(ctrl, 0)
           x_time.insert(0,0)

        stim_colors = check_exceeds(stim, Seconds, 1)
        ctrl_colors = check_exceeds(ctrl, Seconds, -1)
        stim_greater = stim>0
        stim_greater = stim_greater.astype(int)
        ctrl_greater = ctrl<0
        ctrl_greater = ctrl_greater.astype(int)
        stim_gray = [x and y for x,y in zip(stim_colors,stim_greater)]
        ctrl_gray = [x and y for x,y in zip(ctrl_colors,ctrl_greater)]
        stim_black = [y and not x for x,y in zip(stim_colors, stim_greater)]
        ctrl_black = [y and not x for x,y in zip(ctrl_colors, ctrl_greater)]


        # plot triggers
        fill1 = copy(pre)
        fill2 = duration - post
        fill3 = copy(duration)
        plt.figure(figsize=(5,1), dpi=80)
        plt.fill([0,fill1,fill1,0], [-1.05,-1.05,1,1], 'b', alpha=0.2)
        plt.fill([fill2,fill3,fill3,fill2], [-1.05,-1.05,1,1], 'b', alpha=0.2)
        plt.fill_between(x_time, 0, stim, where=stim_gray, color=line_color)
        plt.fill_between(x_time, 0, ctrl, where=ctrl_gray, color=line_color)
        plt.fill_between(x_time, 0, stim, where=stim_black, color="gray")
        plt.fill_between(x_time, 0, ctrl, where=ctrl_black, color="gray")
        plt.text(-100, 0.5, 'S', fontsize=12)
        plt.text(-100, -0.6, 'C',fontsize=12)
        plt.ylim(-1.1, 1.1)
        plt.axis('off')

        # save figure
        filename = save_folder+'/SparkFigures_Fuller/Sparklines_Fish'+str(i+1)+'.jpg'
        plt.savefig(filename)

def InROI(file, Coordinates, TMin, TMax):
    from matplotlib import path
    import numpy as np
    from scipy import spatial as sp
    import itertools

    K = sp.ConvexHull(Coordinates).vertices
    K = np.append(K, K[0])
    XVert = Coordinates[K,0]
    YVert = Coordinates[K,1]
    XY = np.stack((XVert, YVert), axis=1)

    data_in = [0]*len(file['T'].iloc[int(TMin):int(TMax)])
    X_dat = file['X'].iloc[int(TMin):int(TMax)]
    Y_dat = file['Y'].iloc[int(TMin):int(TMax)]
    p = path.Path(XY)

    for i, (x, y) in enumerate(itertools.izip(X_dat, Y_dat)):
        data_in[i] = int(p.contains_points([(x, y)]))
    return np.asarray(data_in)

def check_exceeds(a, seconds, number):
    import numpy as np
    start = None
    starts_and_ends = []
    colors = [0]*len(a)
    for i, x in enumerate(a):
        if x == number:
            if start is None:
                start = i
            if i == len(a)-1 and i - start >= seconds-1:
                starts_and_ends.append((start,i+1))
        else:
            if start is not None and i - start >= seconds-1:
                starts_and_ends.append((start,i))
            start = None
    for x,y in starts_and_ends:
        colors[x:y]=[number]*(y-x)
    return np.asarray(colors)