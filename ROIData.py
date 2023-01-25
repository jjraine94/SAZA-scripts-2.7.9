def ROIData(Coordinates, TMin, TMax):
#    What script does
#
#     Sentence about what it does
#     (Python equivalent of Matlab function LoadData)
#
#     Returns:
#         What it returns

    import numpy as np
    import os
    import pandas as pd
    import re
    from itertools import compress
    from InROI import InROI
    import Tkinter, tkFileDialog

    # root = Tkinter.Tk()
    # root.withdraw()
    # data_folder = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select folder containing fish data:')
    # data_folder = '%s/FishData' % data_folder
    data_folder = raw_input("Input name of folder containing LoadData output: ")
    data_folder = '%s/FishData' % data_folder

    # Define function to sort .csv files in order
    _nsre = re.compile('([0-9]+)')
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(_nsre, s)]

    csvfiles = []
    for File in os.listdir(data_folder):
        if File.endswith('.csv'):
            csvfiles.append(os.path.join(data_folder, File))
    csvfiles.sort(key=natural_sort_key)
    data = pd.DataFrame(columns = ['Fish Number', 'TIn','TOut','BoundaryCrossings',\
                                   'MeanVIn','MeanVOut','StdVIn','StdVOut'])

    for i in range(1, len(csvfiles)+1):
        print('Fish..'+str(i))
        # Extract time spent
        File = pd.read_csv(csvfiles[i-1])
        cnames = File.columns.tolist()
        time = File['T']
        index = 'Fish %s' % i

        TMin1 = round(File['Sampling_Rate'][0]*TMin)
        TMax1 = round(File['Sampling_Rate'][0]*TMax)
        data_in, data_out = InROI(File, Coordinates, TMin1, TMax1)

        TIn = 0
        TOut = 0
        Changes = 0
        for j in range(1, len(data_in)):
            if data_in[j-1] != data_in[j]:
                Changes += 1
        VIn=list(compress(File['V'],data_in[:-1]))
        VOut=list(compress(File['V'],data_out[:-1]))
        if VIn:
            if np.isnan(VIn[0]):
                del VIn[0]
        if VOut:
            if np.isnan(VOut[0]):
                del VOut[0]
        dT = File['dT'][1:]
        TIn += sum(list(compress(dT,data_in[:-1])))
        TOut += sum(list(compress(dT,data_out[:-1])))

        # convert to python 3.4: both mean and sd functions exist in statistics module
        data = data.append({'Fish Number': index, 'TIn':TIn, 'TOut':TOut, 'BoundaryCrossings':Changes,\
                'MeanVIn':np.mean(VIn), 'MeanVOut':np.mean(VOut),\
                'StdVIn':np.std(VIn), 'StdVOut':np.std(VOut)}, ignore_index=True)

    # Filename
    filename = raw_input("Enter file name for saving: ")

    # Save data
    save_folder=os.path.dirname(data_folder)
    filepath = '%s/%s.csv' % (save_folder, filename)
    data.to_csv(filepath, float_format= '%.12f', header = list(data), index=False)






