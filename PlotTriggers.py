def PlotTriggers():
    #     Plot triggers
    #
    #     Plots how many times fish triggered odors
    #     (Python equivalent of Matlab function plot_triggers)
    #
    #     Returns:
    #        folder containing .jpg plots for each fish

    import os
    import shutil
    import re
    from matplotlib import pyplot as plt
    import pandas as pd
    # import Tkinter, tkFileDialog

    # root = Tkinter.Tk()
    # root.withdraw()
    # data_folder = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select folder containing fish data:')
    # data_folder = '%s/FishData' % data_folder
    data_folder = raw_input("Input name of folder containing LoadData output: ")
    data_folder = '%s/FishData' % data_folder
    save_folder=os.path.dirname(data_folder)

    duration = 1440
    
    if os.path.exists(save_folder+'/Figures'):
            shutil.rmtree(save_folder+'/Figures')
    os.makedirs(save_folder+'/Figures')

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
        time = df['T']

        if csvfiles[i][-5] == 'L':
            stimulus = cnames[2]
            control = cnames[3]
        else:
            stimulus = cnames[3]
            control = cnames[2]

        # plot triggers
        x_time = []
        min_time = min(time)
        x_time[:] = [x - min_time for x in time]
        f, (fs1, fs2) = plt.subplots(2, 1, figsize=(7,7))
        fs1.plot(x_time, df[stimulus])
        fs1.set_ylim(0, 1.1)
        fs1.set_xlim(0, duration)
        fs1.set_title('Triggers within %s (Stimulus)' % stimulus)
        fs1.set_xlabel('Time (ms)')
        fs1.set_ylabel('Trigger on')
        plt.subplots_adjust(hspace=0.3)

        fs2.plot(x_time, df[control])
        fs2.set_ylim(0, 1.1)
        fs2.set_xlim(0, duration)
        fs2.set_title('Triggers within %s (Control)' % control)
        fs2.set_xlabel('Time (ms)')
        fs2.set_ylabel('Trigger on')

        # save figure
        name_file = save_folder+'/Figures/Triggers_ROI_Fish_'+str(i+1)+'.jpg'
        f.savefig(name_file)
