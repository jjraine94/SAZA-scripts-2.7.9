def TdmsToCSV():
    #   Extracts data from all .tdms files in a folder and saves as .csv files.
    #
    #   Saves groups in a .tdms file as individual .csv files in one folder.
    #   (Python equivalent of Matlab function convert_tdms_to_mat)
    #
    #   Returns:
    #       For every .tdms file, a folder containing the file's contents in .csv form,
    #       with an individual .csv file for each group in the original .tdms.

    from nptdms import TdmsFile
    import os, shutil
    import pandas as pd
    import re
    # import Tkinter, tkFileDialog
    #
    # root = Tkinter.Tk()
    # root.withdraw()
    # data_folder = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select folder containing .tdms files:')
    data_folder = raw_input("Input name of folder containing .tdms files: ")

    # get list of tdms files in folder
    tdmsfiles = []
    for File in os.listdir(data_folder):
        if File.endswith('.tdms'):
            tdmsfiles.append(os.path.join(data_folder, File))

    tdmsfiles.sort()

    for i in range(0, len(tdmsfiles)):
        filename = os.path.basename(tdmsfiles[i])
        filename = os.path.splitext(filename)[0]
        print(filename)

        # create new folder for each tdms file
        # if the folder already exists, remove all subdirectories and write again
        if os.path.exists('%s/%s' % (data_folder, filename)):
            shutil.rmtree('%s/%s' % (data_folder, filename))
        os.makedirs('%s/%s' % (data_folder, filename))

        # read a tdms file
        tdms_file=TdmsFile(tdmsfiles[i])
        tdms_groups = tdms_file.groups()

        # get channels in group
        for j in range(0, len(tdms_groups)):
            data={}
            group=str(tdms_groups[j])
            channels = tdms_file.group_channels(group)
            ch_names = []

            # save channel as column in dictionary 'data'
            for k in range(0, len(channels)):
                channel = re.split('\W+', str(channels[k]))[-2]
                if channel == 'duration' or channel == 'type' or channel == 'Number' \
                        or channel == 'ms' or channel == 'time':
                    continue
                if channel == 'Location':
                    channel = 'Stimulus Location'
                ch_names.append(channel)
                channel_object=tdms_file.object(group,channel)
                channel_object_data=channel_object.data
                data[k] = channel_object_data

            # save data as one csv file
            df= pd.DataFrame(data)
            df.to_csv('%s/%s/%s.csv' % (data_folder, filename, group), header=ch_names, float_format= '%.12f',index=False)

