def SaveTriggers(TMin, TMax, Bin_Lengths):
    #     Saves ROI trigger duration for each fish.
    #
    #     (Python equivalent of Matlab function save_triggers_in_excel)
    #
    #     Accepts:
    #          TMin - start time (in seconds)
    #          TMax - end time (in seconds)
    #          Bin_Lengths - bins for sorting triggers (in miliseconds)
    #
    #     Returns:
    #         .csv file containing containing trigger information for each fish.
    #         Data for stimulus ROI is stored on the Left and data for control ROI
    #         is stored on the Right.

    import re
    import numpy as np
    import os
    import pandas as pd
    import collections
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

    # Define function to sort bins
    def binstore(File, trigger, df, i, ROI):
        trigger_time = len(np.nonzero(trigger)[0]) * 1/(File['Sampling_Rate'][1])
        # Save only consecutive 1s in trigger
        trigger = trigger.tolist()
        trigger = ''.join([str(x) for x in trigger])
        num_consec = trigger.split("0")
        num_consec = list(filter(None, num_consec))

        if not num_consec:
            result = [0] * len(Start)
        else:
            length_num_consec = []
            length_num_consec_ms = []
            for k, num in enumerate(num_consec):
                length_num_consec.append(len(num))
                length_num_consec_ms.append(len(num)*(1/File['Sampling_Rate'][1])*1000)

            # Sort into bins
            result = np.digitize(length_num_consec_ms, Bins_for_sorting)
            result = np.bincount(result, minlength=len(Bin_Lengths)+1)
            result = np.delete(result, 0)
            result = result.astype('S15')
            result = np.insert(result, 0, "Fish %s %s" % (i, ROI))
            result = np.append(result, trigger_time)
            df.loc[len(df)] = result
        return result


    # Save data in folder below data_folder
    save_folder=os.path.dirname(data_folder)

    Start = []
    End = []
    # Save upper and lower limits of each bin to lists Start and End
    for i, Bin in enumerate(Bin_Lengths):
        indices = re.split('-', Bin)
        Start.append(int(indices[0]))
        End.append(int(indices[1]))

    # Add one more bin for data after last bin
    Start.append(End[-1])
    Bin_Lengths.append('> than ' + str(End[-1]))

    if TMax < End[-1]/1000:
        ValueError('Bin Lengths requested are greater than TMax')

    # Load Data
    # Get all csv files in the specified folder
    csvfiles = []
    for File in os.listdir(data_folder):
        if File.endswith('.csv'):
            csvfiles.append(os.path.join(data_folder, File))
    csvfiles.sort(key=natural_sort_key)

    File = pd.read_csv(csvfiles[0])
    TMin1 = int(round(File['Sampling_Rate'][0]*TMin))
    TMax1 = int(round(File['Sampling_Rate'][0]*TMax))

    # Initialize variables before loop
    count = 1
    stim_triggers = []
    ctrl_triggers = []
    stimbins = {}
    ctrlbins = {}
    stimlab = []
    ctrllab = []
    columns1 = Bin_Lengths[:]
    columns1.append('Total trigger time (s)')
    columns2 = columns1[:]
    columns1.insert(0, 'Fish ID (Stimulus)')
    columns2.insert(0, 'Fish ID (Control)')
    df1 = pd.DataFrame(columns = columns1)
    df2 = pd.DataFrame(columns= columns2)

    # get csv files for each fish
    for i in range(1, len(csvfiles)+1):
        print('Fish..'+str(i))
        File = pd.read_csv(csvfiles[i-1])
        cnames = File.columns.tolist()

        if TMax1 > len(File[cnames[0]]):
            ValueError('Time bin specified is greater than recording time')

        Bins_for_sorting = Start[:]
        Bins_for_sorting.append(TMax*1000)

        # Get time taken for different triggers

        for k, j in enumerate(cnames[2:4]):
            ROI = j
            trigger = File[ROI].iloc[TMin1:TMax1]

            # Pass to helper function
            if csvfiles[i-1][-5] == 'L' and k == 0 or csvfiles[i-1][-5] == 'R' and k == 1:
                stimbins['Fish %s' % str(i)] = binstore(File, trigger, df1, i, ROI)
                # stimlab.append('Fish %s %s' % (str(i), ROI))
            else:
                ctrlbins['Fish %s' % str(i)] = binstore(File, trigger, df2, i, ROI)
                # ctrllab.append('Fish %s %s' % (str(i), ROI))
            count += 1

    df = pd.concat([df1, df2], axis=1)
    colnames = list(df)
    filename = raw_input('Enter file name for saving: ')

    # export as csv
    df.to_csv('%s/%s.csv' % (save_folder, filename), float_format= '%.12f', index=False, header=colnames)
