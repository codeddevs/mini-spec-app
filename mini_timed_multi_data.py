# Copyright (c) 2025 Coded Devices Oy
# edit : 2025-1-17
# desc : Class for timeseries of multiple channel values.
import time
import matplotlib.pyplot as plt

class mini_timed_multi_data:

    # edit : 2024-3-28
    def __init__(self, channel_count=3):
        self.timed_data = []    # 2D array for all channel values and timestamps, 
                                # all values in a row are from the same spectrum --> same timestamp
                                # note ch_i is not the actual channel number (of the corresponding wavelength) but an index
                                # latest value (highest timestamp) will be added to the end of the array
        
        self.ChWavelength = [0] * channel_count  # array of wavelengths in order of corresponding channel index
        
        # set ch_count only once & only here (1...9)
        if channel_count > 0 and channel_count < 10:
            self.ch_count = channel_count   
        else:
            print(' ERROR, incorrect number of timed channels! Now set to 3.')
            self.ch_count = 3
                                        # affects the data array size
        self.ts_count = 0               # number of time stamps in memory, increase after adding a new timestamp (row)
        self.startTime = 0              # timestamp value of the first datarow

    # edit : 2024-3-20
    # desc : Set the wavelength of a channel.
    def AddChWavelength(self, ch_index, ch_wavelength):
        try:
            self.ChWavelength[ch_index] = ch_wavelength
                
        except:
            print(' ERROR in adding channel wavelength!')

    # edit : 2024-3-20
    def PrintWavelengths(self):
        print('')
        print(' Measuring selected channels...')
        print(' Wavelengths: ', end=' ')
        for i in range(len(self.ChWavelength)):
            print(str(self.ChWavelength[i]), end= ' ')
        print('nm')


    # edit : 2024-3-10
    # desc : Add one channel value with a timestamp to the array that contains all timed values and timestamps.
    #        
    def AddDataPoint(self, ch_i, ch_value, ch_timestamp):

        # time_stamp will have three decimals
        # this is universal constraint
        ch_timestamp = round(ch_timestamp, 3)
        
        # not the first row
        if self.ts_count > 0:
           
            # existing timestamp in the last row is older than one to be added
            if (self.timed_data[self.ts_count-1][self.ch_count] < ch_timestamp):
                new_row = [0] * (self.ch_count + 1)
                new_row[ch_i] = int(ch_value)
                new_row[self.ch_count] = ch_timestamp # last value of the row is timestamp
                self.timed_data.append(new_row)
                self.ts_count = self.ts_count + 1
                
            # timestamp in the last row is same as one to be added
            elif (self.timed_data[self.ts_count-1][self.ch_count] == ch_timestamp):
                self.timed_data[self.ts_count-1][ch_i] = int(ch_value)
                
            else:
                print(' ERROR in adding timed multi data in method AddDataPpoint')
        
        # is first row, save timestamp offset
        else:
            self.startTime = ch_timestamp
            ch_timestamp = ch_timestamp - self.startTime
            new_row = [0] * (self.ch_count + 1)
            new_row[ch_i] = int(ch_value)
            new_row[self.ch_count] = ch_timestamp # last value of the row is timestamp
            self.timed_data.append(new_row)
            self.ts_count = self.ts_count + 1

            
    # edit : 2024-3-28 
    def PrintLastDataRow(self):
        try:
            if self.ts_count > 0:
                if self.ts_count == 1:
                    print(' Intensities & time stamp (sec):')
                print(' # ' + str(self.ts_count) + ' : ' + str(self.timed_data[self.ts_count - 1]))
        except:
            print(' ERROR in printing the last row of the timed array!')

    # edit : 2024-2-11
    # desc : clear & reset timed data array
    def ClearTimedData(self):
        self.timed_data = []
        self.ts_count = 0
        self.startTime = 0

    # edit : 2025-2-16
    # desc : Input parameter b defines if the graph blocks the progress of the program.
    # todo : Check if there is any benefit of using interactive mode plt.ion() 
    def DrawTimedGraph(self, b=False):

        if self.ts_count == 1:
            self.PrintWavelengths()

        plot_styles = ['-*b', '-og', '-xr', '-+y', '-#m']

        plt.figure("TIME DOMAIN VALUES")
        plt.ion() # added 2025-2-16
        plt.grid(True)
        plt.xlabel("Time [s]")
        plt.ylabel("Intensity [bit]")

        legends = []
        
        time_data = [x[self.ch_count] for x in self.timed_data] #ch_count is same as the index of time_stamp value
        for i in range(self.ch_count):
            ch_data = [x[i] for x in self.timed_data]
            time_data = [x[self.ch_count] for x in self.timed_data]
            plt.plot(time_data, ch_data, plot_styles[i])
            legends.append(self.ChWavelength[i] + ' nm')
        plt.legend(legends)   
        plt.show(block=b)

    # edit : 2025-2-16
    def CloseTimedGraph(self):
        if plt.fignum_exists('TIME DOMAIN VALUES'):
            plt.close('TIME DOMAIN VALUES')


    # edit : 2024-2-9
    # desc : return the timestamp of the last row of the data array.
    def GetLatestTimestamp(self):
        row_index = len(self.timed_data) - 1
        ts_index = self.ch_count
        return self.timed_data[row_index][ts_index] 
        

    # edit : 2024-2-9
    # desc : Subtract the timestamp of first data row from the following rows
    def SubtractStartTime(self, time):
        if len(self.timed_data) > 0:
            start_time = self.timed_data[0][self.ch_count]
            return time-start_time
        else:
            print(' ERROR in calling SubtractStartTime method!')
            return time


# unit test
# edit: 2024-2-9
#
if __name__ == '__main__':
 
    myTimed = mini_timed_multi_data()
    start_time = time.time()

    value = int(input('Give a value, 0 to end!'))
    channel_i = int(input('Give a channel index!'))

    while value > 0:
        stamp = time.time() - start_time
        myTimed.AddDataPoint(channel_i, value, stamp)
        value = int(input('Give a value, 0 to end!'))
        channel_i = int(input('Give a channel index!'))

    print(myTimed.timed_data)
    print(myTimed.ch_count)
    print(myTimed.ts_count)

    print('last timestamp: %.3f' %myTimed.GetLatestTimestamp())
    





