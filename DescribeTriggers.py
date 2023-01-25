def DescribeTriggers():
    #     Python equivalent of Matlab function save_triggers_in_excel
    #
    #     Args:
    #         data_folder: definition
    #
    #     Returns:
    #         .csv file containing...

    import re
    import numpy as np
    import os
    import pandas as pd
    from matplotlib import pyplot as plt
    from scipy.stats.kde import gaussian_kde
    from scipy.stats import ks_2samp
    from numpy import linspace
    import Tkinter, tkFileDialog

    # root = Tkinter.Tk()
    # root.withdraw()
    # data_folder = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select folder containing fish data:')
    # data_folder = '%s/FishData' % data_folder
    data_folder = raw_input("Input name of folder containing LoadData output: ")
    data_folder = '%s/FishData' % data_folder
    save_folder = os.path.dirname(data_folder)

    # Define function to sort .csv files in order
    _nsre = re.compile('([0-9]+)')
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(_nsre, s)]

    # Define function to sort bins
    def binstore(File, trigger, num_triggers):
        num_triggers.append(len(np.nonzero(trigger)[0]) * 1/(File['Sampling_Rate'][1]))

        # Save only consecutive 1s in trigger
        trigger = trigger.tolist()
        trigger = ''.join([str(x) for x in trigger])
        num_consec = trigger.split("0")
        num_consec = list(filter(None, num_consec))

        if not num_consec:
            length_num_consec_ms = 0
        else:
            length_num_consec = []
            length_num_consec_ms = []
            for k, num in enumerate(num_consec):
                length_num_consec.append(len(num))
                length_num_consec_ms.append(len(num)*(1/File['Sampling_Rate'][1])*1000)
        return length_num_consec_ms


    # Save data in folder below data_folder
    save_folder=os.path.dirname(data_folder)

    Tmin = 10 # in seconds
    Tmax = 1000 # in seconds

    # Load Data
    # Get all csv files in the specified folder
    csvfiles = []
    for File in os.listdir(data_folder):
        if File.endswith('.csv'):
            csvfiles.append(os.path.join(data_folder, File))
    csvfiles.sort(key=natural_sort_key)

    File = pd.read_csv(csvfiles[0])
    Tmin1 = int(round(File['Sampling_Rate'][0]*Tmin))
    Tmax1 = int(round(File['Sampling_Rate'][0]*Tmax))

    # Initialize variables before loop
    count = 1
    stim_triggers = []
    ctrl_triggers = []
    stimcount = []
    ctrlcount = []


    # get csv files for each fish
    for i in range(1, len(csvfiles)+1):
        print('Fish..'+str(i))
        File = pd.read_csv(csvfiles[i-1])
        cnames = File.columns.tolist()

        if Tmax1 > len(File[cnames[0]]):
            ValueError('Time bin specified is greater than recording time')

        # Bins_for_sorting = Start[:]
        # Bins_for_sorting.append(Tmax*1000)

        # Get time taken for different triggers

        for k, j in enumerate(cnames[2:4]):
            ROI = j
            trigger = File[ROI].iloc[Tmin1:Tmax1]

            # Pass to helper function
            if csvfiles[i-1][-5] == 'L' and k == 0 or csvfiles[i-1][-5] == 'R' and k == 1:
                stimcount.extend(binstore(File, trigger, stim_triggers))
            else:
                ctrlcount.extend(binstore(File, trigger, ctrl_triggers))
            count += 1

    # histogram
    plt.hist(ctrlcount, bins='auto', alpha=0.5, label='control')
    plt.hist(stimcount, bins='auto', alpha=0.5, label='stimulus')
    plt.legend()
    plt.title('Frequency of Trigger Duration')
    plt.xlabel('Duration (ms)')
    plt.ylabel('Frequency')
    name_file = save_folder+'/Trigger_Histogram.jpg'
    plt.tight_layout()
    plt.savefig(name_file)
    plt.show()

    # probability density curve
    kde1 = gaussian_kde(ctrlcount)
    dist_space1 = linspace(min(ctrlcount), max(ctrlcount), 200)
    line1, = plt.plot(dist_space1, kde1(dist_space1))
    kde2 = gaussian_kde(stimcount)
    dist_space2 = linspace(min(stimcount), max(stimcount), 200)
    line2, = plt.plot(dist_space2, kde2(dist_space2))
    plt.legend((line1, line2), ('control', 'stimulus'))
    plt.title('Frequency of Trigger Duration')
    plt.xlabel('Duration (ms)')
    plt.ylabel('Frequency')
    name_file = save_folder+'/Trigger_Curve.jpg'
    plt.tight_layout()
    plt.savefig(name_file)
    plt.show()

    ctrl = pd.DataFrame(ctrlcount)
    c_stats = ctrl.describe()

    stim = pd.DataFrame(stimcount)
    s_stats = stim.describe()

    ks, pval = ks_2samp(ctrlcount, stimcount)
    print("K-S two-sample test: D = %06.3f, p = %06.3f" % (ks, pval))

    stats = pd.concat([c_stats, s_stats], axis=1)
    index = ['Total triggers', 'Mean trigger duration (ms)', 'Std of duration', 'Min duration',
             'Lower quartile', 'Median', 'Upper quartile', 'Max duration']
    stats['index'] = index
    stats=stats.set_index('index')

    stats.to_csv(save_folder + '/Descriptive.csv', float_format= '%.2f', index=True, header=['control','stimulus'])
