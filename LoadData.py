def LoadData():
    #    What script does
    #
    #     Sentence about what it does
    #     (Python equivalent of Matlab function LoadData)
    #
    #     Returns:
    #         What it returns

    import os, shutil
    import pandas as pd
    from GetFishTrace import GetFishTrace
    import re
    # import Tkinter, tkFileDialog
    #
    # root = Tkinter.Tk()
    # root.withdraw()
    # data_folder = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select folder containing fish data:')
    data_folder = raw_input("Input name of folder containing LoadData output: ")

    _nsre = re.compile('([0-9]+)')
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(_nsre, s)]

    csvfiles = [os.path.join(root, name)
                for root, dirs, files in os.walk(data_folder)
                for name in files
                if name == 'Tracker.csv']
    csvfiles.sort(key=natural_sort_key)
    iMax = len(csvfiles)
    count = 1

    locationfiles = [os.path.join(root, name)
                 for root, dirs, files in os.walk(data_folder)
                 for name in files
                 if name == 'ExperimentInfo.csv']
    locationfiles.sort(key=natural_sort_key)

    if os.path.exists(data_folder+'/FishData'):
            shutil.rmtree(data_folder+'/FishData')
    os.makedirs(data_folder+'/FishData')

    for i in range(0, iMax):
        # read csv file
        File=pd.read_csv(csvfiles[i])
        filename = re.search('\\\\(LOG.*?)\\\\', csvfiles[i])
        Fish1 = GetFishTrace(File, 1)
        F1 = str(2*count-1)
        Fish2 = GetFishTrace(File, 2)
        F2 = str(2*count)
        print('Fish {%s} = Fish 001: %s' % (F1, filename.group(1)))
        print('Fish {%s} = Fish 002: %s' % (F2, filename.group(1)))

        # find location of stimulus
        locfile = pd.read_csv(locationfiles[i])
        stimLoc = locfile['Stimulus Location'][0][0]


        # Save fish numbers
        if i ==0:
            idfile = data_folder + '/FishData/Fish_number.txt'
            fid = open(idfile, 'w')
        else:
            idfile = data_folder + '/FishData/Fish_number.txt'
            fid = open(idfile, 'a')

        fid.write('%s' % ('Fish {'+F1+'} = Fish 001: '+filename.group(1)))
        fid.write('\n')
        fid.write('%s' % ('Fish {'+F2+'} = Fish 002: '+filename.group(1)))
        fid.write('\n')
        fid.close()

        # Save data for both fish
        df1 = pd.DataFrame(Fish1)
        df2 = pd.DataFrame(Fish2)
        df1.to_csv('%s/FishData/Fish {%s}_001_%s.csv' % (data_folder, F1, stimLoc), float_format= '%.12f',index=False)
        df2.to_csv('%s/FishData/Fish {%s}_002_%s.csv' % (data_folder, F2, stimLoc), float_format= '%.12f',index=False)

        count += 1
