# Copyright (c) 2025 Coded Devices Oy

# file name : mini_data
# ver : 2025-2-15
# desc : mini_data class for data handling and presentation operations.
#		 
# TODO : * Complete drawPointValue method 

import matplotlib.pyplot as plt
import mini_settings
import mini_file_operations as fop
import copy
import mini_temp

class mini_data:
        
    # edit 2023-12-15
    def __init__ (self):
        self.data = []              # Warning! data array can contain modified data, ch numbers or wavelengths.
        self.background = []        # Refrence background signal that can be subtracted from measurement. 
        self.average = []
        self.ave_size = 0		    # this many spectras have been accumulated into average
        self.int_calib = []
        self.zero_reference = []    # spectrum with zero thickness absorption material
        self.absorption = []        # absorption spectrum = zero_reference - data through material
        self.rel_absorption = []    # relative absoprtion spectrum = (zero_reference - sample) / zero_reference * 100
        self.data_file_name = ""    # include in plots
        self.added_to_average = False   # result already added to average spectrum


    # method : channelToWavelength
	# ver : 29.4.2022
	# desc : Convert channel (pix) number 1...288 to wavelength using factory calibration data.
    #        In data[][] array overwrite channel values using wavelength values. 
    #        Factory calibration data is found in the sensor datasheet.
    #        Last addition of 0.5 is for correct rounding in float --> int conversion.
    #        Notice! channel = 0 gives nonsense.    
	#
    def channelToWavelength(self):
        for i in range(len(self.data)):
            x = self.data[i][0]
            self.data[i][0] = int(mini_settings.calib_a0 \
                                + x * mini_settings.calib_b1 \
                                + x**2 * mini_settings.calib_b2 \
                                + x**3 * mini_settings.calib_b3 \
                                + x**4 * mini_settings.calib_b4 \
                                + x**5 * mini_settings.calib_b5 \
                                + 0.5)

    # method : waveLengthToChannel
    # ver : 2025-2-8
    # desc : Convert a wave length to a channel number (1...288)
    #        Returns a channel number, not channel index!
    #        Returns channel number zero if wevelength is shorter than can be actually measured,
    #        channel number 0 does not exist!
    #        Returns channel number hw_channel_count + 1 (289) if wavelength is longer than can be 
    #        actually measured, that channel (289) does not exist!
    def waveLengthToChannel(self, any_wave_length):

        min_diff = 890 - 310
        min_diff_channel = 0
                 
        for i in range(1, mini_settings.hw_channel_count + 1):
            w = int(mini_settings.calib_a0 \
                + i * mini_settings.calib_b1 \
                + i**2 * mini_settings.calib_b2 \
                + i**3 * mini_settings.calib_b3 \
                + i**4 * mini_settings.calib_b4 \
                + i**5 * mini_settings.calib_b5
                + 0.5)

            diff = abs(any_wave_length - w)
            
            if diff < min_diff:
                min_diff = diff
                min_diff_channel = i

        # warn if incorrect channel number is about to be returned    
        #if min_diff_channel < 1 or min_diff_channel > mini_settings.hw_channel_count:
        #    print(" Incorrect value in wavelength !")             
            
        return min_diff_channel
    
	# method : removeDC
	# ver : 3.6.2022	
	# desc : Remove a constant DC level from the spectrum.
    def removeDC(self, dc):
        if(dc > 0):
            try:
                for i in range(len(self.data)):
                    self.data[i][1] = self.data[i][1] - dc
            except TypeError:
                print(" No valid data to be used in DC remove!")

    # method : remove_any_dc
    # ver : 3.6.2021
    # desc : Like removeDC but can be used for any spectrum (reference for example)
    def remove_any_dc(self, any_spectrum, dc):
        try:
            for i in range(len(any_spectrum)):
                any_spectrum[i][1] = any_spectrum[i][1] - dc
        except TypeError:
            print(" No valid data to be used in DC remove!")

    # method : estimate_dc
    # ver : 2023-9-2
    # desc : Simple estimate for dc-level: smallest positive.
    #
    def estimate_dc(self): 
        if(len(self.data) > 0):
            try:
                int_data = [x[1] for x in self.data]
                int_data.sort() # ascending order
                index = 0
                while int_data[index] < 1:
                    index = index + 1        
                return int_data[index]
            except TypeError:
                print(" Wrong data type found during dc-level estimate!")
                return -1
        else:
            print (" Error : No data!")
            return -1
        

    # method : estimate_any_dc
    # ver : 3.6.2022
    # desc: Like estimate_dc but can be used for any spectrum and not just
    #       for class members.
    def estimate_any_dc(self, any_spectrum):
               
        try:
            int_data = [x[1] for x in any_spectrum]
            int_data.sort() # ascending order
            index = 0
            while int_data[index] < 1:
                index = index + 1        
            return int_data[index]
        except TypeError:
            print(" Wrong data type found during dc-level estimate!")
            return 0 								

	# method : loadBackground
	# ver : 26.5.2022
	# desc : Load background data from the background file, -1 if error.
	#
    def loadBackground(self, file_name):
        self.background, unit = fop.read_file(file_name)
    
    # method : loadIntCalib
	# ver : 26.5.2022
	# desc : Load intensity response calibration data from the calibration file, -1 if error.
	#
    def loadIntCalib(self, file_name):
        self.int_calib, unit = fop.read_file(file_name)

    # method : loadZeroReference
    # ver : 26.5.2022
    # desc : Load spectrum measured with zero material thickness, use in absorption studies.
    #
    def loadZeroReference(self, file_name):
        self.zero_reference, unit = fop.read_file(file_name)
	
	# method : removeBackground
	# ver : 19.8.2022
	# desc : Remove background from a measured spectrum. Subtract by channel index, not by wavelength data.
	#
    def removeBackground(self, file_name):
        self.loadBackground(file_name)
        if(self.background == -1):
            print(" Error in background data! Background was not removed.")
            return None

        lenSpectrum = len(self.data)
        lenBackground  = len(self.background)
        if (lenSpectrum == lenBackground):
            for i in range(0, lenSpectrum):
                data_point = self.data[i]
                bck_point = self.background[i]
                self.data[i] = [data_point[0], data_point[1] - bck_point[1]]
            print(" Background removed.")
        else:
            print(" ERROR : length of the background data is incorrect!")

	# method : drawBarSpectrum
	# ver : 2.2.2019
	# desc : Simple bar graph
	#
    def drawBarSpectrum(self):
        int_data = [x[1] for x in self.data]
        ch_data = [x[0] for x in self.data]
        #plt.plot(ch_data, int_data)
        plt.bar(ch_data, int_data, width=2.67)
        plt.show()

	# method : drawLineSpectrum
	# ver : 2025-2-15
	# desc : Simple line spectrum
	#        Draw absolute spectrums into figure "ABSOLUTE GRAPH"
    #        This name identifies the graph instead of ID number.   
    def drawLineSpectrum(self):
        plt.figure("ABSOLUTE GRAPH")
        int_data = [x[1] for x in self.data]
        ch_data = [x[0] for x in self.data]
        plt.ion()   # interactive mode on
        plt.plot(ch_data, int_data)

        ax = plt.gca() # get axis object
        ymin, ymax = ax.get_ylim()
        xmin, xmax = ax.get_xlim()

        x_axis_range = xmax - xmin
        x_data_range = max(ch_data) - min(ch_data)

        # Following handles two special cases:
        # 1. Second spectrum is being drawn into the same plot but it has higher max value.
        # 2. If a plot becomes redrawn in its zoomed state, we want to maintain the zoom.
        try: 
            if(ymax < int(max(int_data) * 1.1) and x_axis_range > int(x_data_range * 1.1)):
                ax.set_ylim(0, int(max(int_data) * 1.1))
        except ValueError:
            print(" Error: Scaling of the plot failed!")

        plt.suptitle("" + self.data_file_name)
        plt.xlabel("wavelength [nm]")
        plt.ylabel("intensity [bit]")
        plt.grid(True)
        plt.show()

    # edit : 2025-2-15
    # desc : Returns true if the plot is currently zoomed.
    def isZoomed(self, y_default, x_default):
        #fig, ax = plt.figure("ABSOLUTE GRAPH")
        #if(y_default != ax.get_ylim()):
            print(' Zoomed Y')


    # method : ClearLineSpectrum
    # edit : 2023-12-15
    def ClearLineSpectrum(self):
        if plt.fignum_exists('ABSOLUTE GRAPH'):
            plt.clf() 
            plt.xlabel("wavelength [nm]")
            plt.ylabel("intensity [bit]")
            plt.grid(True)
            #plt.close('ABSOLUTE GRAPH')
            #print(' Absolute graph closed!')
        else:
            print(' No absolute graph to clear.')
        
    # method : drawPointValue
    # ver 2.6.2022
    # desc : Add a single point value to graph
    def drawPointValue(self, point_wl, point_int):
        plt.figure("ABSOLUTE GRAPH")
        plt.ion()
        plt.plot(point_wl, point_int)
        plt.ylim(0, 4100)
        plt.xlabel("wavelength [nm]")
        plt.ylabel("intensity [bit]")
        plt.grid(True)
        #plt.draw()
        plt.show()             

	# method : addToAverage
	# ver : 2023-12-15
	# desc : Add new spectrum to average.
    def addSpectrumToAverage(self):

        if (len(self.data) == 0):
            print(" Error: No data to add into average!")

        else:
            self.ave_size = self.ave_size + 1
        
            if self.ave_size == 1:
                self.average = copy.deepcopy(self.data)

            elif self.ave_size > 1:
                for i in range(0, len(self.data)):
                    self.average[i][1] = self.data[i][1] / self.ave_size + (self.ave_size - 1) / self.ave_size * self.average[i][1]
            self.added_to_average = True # set to false when new a reading is received

	# method : drawLineAverage
	# ver : 2023-9-8
	# desc : Draw average spectrum.
	#        Draw absolute spectrums into figure "ABSOLUTE GRAPH"
    def drawLineAverage(self):
        plt.figure("ABSOLUTE GRAPH")
        int_ave = [x[1] for x in self.average]
        ch_ave = [x[0] for x in self.average]
        plt.ion()
        plt.plot(ch_ave, int_ave)

        xmin, xmax, ymin, ymax = plt.axis() # get current axis values
        try:
            if(ymax < max(int_ave)*1.1):    
                plt.ylim(0, max(int_ave)*1.1)
        except ValueError:
            print(' Error: No average to draw!')
            plt.ylim(0, 1000)

        plt.xlabel("wavelength [nm]")
        plt.ylabel("intensity [bit]")
        plt.grid(True)
        #plt.draw()
        plt.show()

    # method : get_ch_intensity
    # ver : 10.5.2022
    # desc : get value of the a selected channel of full spectrum.
    # todo : Check if this method is obsolete.
    def get_ch_intensity(self, ch_no = -1):
        if ch_no == -1:
            ch_no = 100
        return self.data[ch_no][1]

    # method : intCorrect
    # ver : 11.5.2022
    # desc : Use calibration file to correct intensity response for each channel.
    #        Calculate intensity scale so that intensity at selected wavelength remains unchanged. 
    #        If no wavelength has been selected then highest intensity value remains unchanged.
    # 
    def intCorrect(self, ref_wavelength=0):

        # check calib data 
        if self.int_calib == -1:
            print(" No valid calibration data found! ")
            return -1        

        # check if calib data has been loaded        
        if len(self.int_calib) < 1:
            print("No calibration data! Trying to load from file...")
            self.loadIntCalib(mini_settings.my_spectra_folder + mini_settings.intensity_calib_file)

        # check calib data again
        if self.int_calib == -1:
            print(" No valid calibration data found! ")
            return -1        
        
        if ref_wavelength > 340 and ref_wavelength < 800:
            const_point = ref_wavelength
        else:
            max_point = self.get_max_intensity() # [index, wavelength, intensity]
            const_point = max_point[1]
  
        scale_coeff = 1.0 / self.get_int_value(const_point, self.int_calib) 
       
        for i in range(0, len(self.int_calib)):
            self.data[i][1] = self.data[i][1] * self.int_calib[i][1] * scale_coeff

    # function: get_int_value
    # ver : 1.11.2019
    # desc : Pick int value according to wave_length.
    #
    def get_int_value(self, wave_length, spectrum):
        ret_index = 0
        prev_diff = wave_length - spectrum[0][0]
        for i in range (1, len(spectrum)):
            new_diff = wave_length - spectrum[i][0]
            if abs(prev_diff) < abs(new_diff):
                break
            elif new_diff == 0:
                ret_index = i
                break
            else:
                prev_diff = new_diff
                ret_index = i
        return spectrum[ret_index][1]


    # method : get_absorption
    # ver : 19.8.2022
    # desc : Calculates absolute absorption spectrum using a zero absorption reference file.
    #        No dc-remove or intensity correction, just simple subtraction.
    #           
    def get_absorption(self):
        self.loadZeroReference(mini_settings.my_spectra_folder + mini_settings.zero_reference_file)
        self.absorption = []   
        for i in range(len(self.data)):
            self.absorption.append([self.data[i][0], self.zero_reference[i][1] - self.data[i][1]])

    # method : get_rel_abs
    # edit : 2023-9-22
    # desc : Calculates relative absorption spectrum using zero_reference file (mini_settings).
    #        Automatic DC-removal and filtration.
    # todo : Combine with method get_rel_abs_from_file.
    def get_rel_abs(self):

        MIN_LEVEL = 20 # limits calculation to meaningfull areas to avoid abs noise peaks
        
        # copies of reference & data to work with 
        self.loadZeroReference(mini_settings.my_spectra_folder + mini_settings.zero_reference_file)
        data_local_copy = copy.deepcopy(self.data)

        if(self.zero_reference == -1):
            print(" Error: No default reference file found!")
            return -1
        
        self.remove_any_dc(self.zero_reference, self.estimate_any_dc(self.zero_reference))
        self.remove_any_dc(data_local_copy, self.estimate_any_dc(data_local_copy))

        #filter, no effect to original spectrum
        f_reference = mini_temp.lowpass_filter(self.zero_reference)
        f_data = mini_temp.lowpass_filter(data_local_copy)

        if False:
            print("i=10...13")
            print(f_data[10])
            print(f_data[11])
            print(f_data[12])
            print(f_data[13])

        try:

            self.rel_absorption = []    # delete previous content

            for i in range(len(f_data)):
                ref_int = f_reference[i][1]
                data_int = f_data[i][1]
                                               
                if ref_int < MIN_LEVEL: 
                    ref_int = MIN_LEVEL

                if data_int < MIN_LEVEL: 
                    data_int = MIN_LEVEL

                temp = ref_int - data_int

                if temp < 0:    
                    temp = 0
                
                temp = temp / ref_int * 100
              
                self.rel_absorption.append([f_data[i][0], temp])
        except Exception as x:
            print(x)
        
        return 1

    # method : get_rel_abs_from_file
    # edit : 2023-9-22
    # desc : Calculates relative absorption spectrum using given reference file.
    #        Automatic DC-removal and filtration.
    # todo : Verify that this method does not alter the original spectrum data.
    #        Combine with get_rel_abs method.
    
    def get_rel_abs_from_file(self, zero_ref_file):

        MIN_LEVEL = 20 # limits calculation to meaningfull areas to avoid abs noise peaks
        
        # copies of reference & data to work with 
        self.loadZeroReference(zero_ref_file)
        data_local_copy = copy.deepcopy(self.data)

        self.remove_any_dc(self.zero_reference, self.estimate_any_dc(self.zero_reference))
        #self.removeDC(self.estimate_dc())
        self.remove_any_dc(data_local_copy, self.estimate_any_dc(data_local_copy))


        #filter, no effect to original spectrum
        f_reference = mini_temp.lowpass_filter(self.zero_reference)
        #f_data = mini_temp.lowpass_filter(self.data)
        f_data = mini_temp.lowpass_filter(data_local_copy)

        if False:
            print("i=10...13")
            print(f_data[10])
            print(f_data[11])
            print(f_data[12])
            print(f_data[13])

        try:

            self.rel_absorption = []    # delete previous content

            for i in range(len(f_data)):
                ref_int = f_reference[i][1]
                data_int = f_data[i][1]
                                               
                if ref_int < MIN_LEVEL: 
                    ref_int = MIN_LEVEL

                if data_int < MIN_LEVEL: 
                    data_int = MIN_LEVEL

                temp = ref_int - data_int

                if temp < 0:    
                    temp = 0
                
                temp = temp / ref_int * 100
              
                self.rel_absorption.append([f_data[i][0], temp])
        except Exception as x:
            print(x)       
 
    # method : drawLineAbsorption
	# ver : 19.8.2022
	# desc : Draw absorption spectrum.
	#
    def drawLineAbsorption(self):
        plt.figure("ABSOLUTE GRAPH")
        int_abs = [x[1] for x in self.absorption]
        ch_abs = [x[0] for x in self.absorption]
        plt.clf()
        plt.ion()
        plt.plot(ch_abs, int_abs)

        xmin, xmax, ymin, ymax = plt.axis() # get current axis values
        if(ymax < max(int_abs)*1.1):    
            plt.ylim(0, max(int_abs)*1.1)

        #plt.ylim(0, max(int_abs)*1.1)
        plt.grid(True)
        plt.xlabel("wavelength [nm]")
        plt.ylabel("intensity [bit]")
        #plt.draw()
        plt.show()    
        
    # method : draw_rel_absorption
    # ver : 19.8.2022
    # desc : draw relative values with %-unit into "RELATIVE GRAPH"
    def draw_rel_absorption(self, any_spectrum):
        plt.figure("RELATIVE GRAPH")
        int_abs = [x[1] for x in any_spectrum]
        ch_abs = [x[0] for x in any_spectrum]
        plt.ion()
        plt.plot(ch_abs, int_abs)
        try:
            xmin, xmax, ymin, ymax = plt.axis() # get current axis values
            if(ymax < max(int_abs)*1.1):    
                plt.ylim(0, max(int_abs)*1.1)
            #plt.ylim(0, max(int_abs)*1.1)
        except ValueError:
            print(" Wrong data type in draw!")
            plt.ylim(0, 100)
        plt.grid(True)
        plt.suptitle("" + self.data_file_name)
        plt.xlabel("wavelength [nm]")
        plt.ylabel("relative absorption [%]")
        plt.show()

    # method : init_rel_graph
    # edit : 2023-8-27
    # desc : Init empty relative graph. Selected x-axis stays unchanged. Y-axis may be enlarged
    #        if high datavalues are drawn. 
    def init_rel_graph(self):
        plt.figure("RELATIVE GRAPH")
        plt.xlim(285, 910)
        plt.ylim(0, 50)
        plt.xlabel("wavelength [nm]")
        plt.ylabel("relative absorption [%]")
        plt.grid(True)
        plt.show()

    # method : ClearRelAbsSpectrum
    # edit : 2023-9-22
    def ClearRelAbsSpectrum(self):
        if plt.fignum_exists('RELATIVE GRAPH'):
            plt.close('RELATIVE GRAPH')
            print('Done!')
        else:
            print('Nothing to clear.')

    # method : get_max_intensity
    # ver : 1.11.2020
    # desc : Return [index, wavelength, intensity] of highest instensity point.
    #
    def get_max_intensity(self):
        int_data = [x[1] for x in self.data]
        max_int_int = max(int_data)
        max_int_index = int_data.index(max_int_int)
        max_int_wl = self.data[max_int_index][0]
        return [max_int_index, max_int_wl, max_int_int]

    # method : multiply
    # ver : 7.1.2021
    # desc : Multiply intensity values by gain value.
    def multiply(self, gain):
        for i in range(0, len(self.data)):
            self.data[i][1] = self.data[i][1] * gain

    # edit : 2024-1-19
    def CloseGraphs(self):

        if plt.fignum_exists('RELATIVE GRAPH'):
            plt.close('RELATIVE GRAPH')

        if plt.fignum_exists('ABSOLUTE GRAPH'):
            plt.close('ABSOLUTE GRAPH')
        

# unit test main
# ver 2025-2-8
#
if __name__ == '__main__':

    myData = mini_data()

    # TEST WAVE LENGTH <--> CHANNEL CONVERSION
    if True:

        print("channels:")    
        print(myData.waveLengthToChannel(313)) #  1
        print(myData.waveLengthToChannel(316)) #  2
        print(myData.waveLengthToChannel(882)) #  288
                
        myData.data.append([myData.waveLengthToChannel(313), 721])
        myData.data.append([myData.waveLengthToChannel(316), 711])
        myData.data.append([myData.waveLengthToChannel(882), 650])

        myData.channelToWavelength()

        print("wavelengths:")    
        print(myData.data[0][0])
        print(myData.data[1][0])
        print(myData.data[2][0])
       
    # TEST RELATIVE ABSORPTION
    if False:

        print("Load from file")
        file_name = input("File name in folder " + mini_settings.my_spectra_folder + " ?: ")
        tempData = []
        tempData, unit = fop.read_file(mini_settings.my_spectra_folder + file_name)
        #myData.data_file_name = file_name
        if tempData != -1: # error in reading file       
            try:
                myData.data_file_name = file_name

                # % 
                if unit == '%':
                    myData.rel_absorption = tempData
                    myData.draw_rel_absorption(myData.rel_absorption)
                # bits or coeff
                else:
                    myData.data = tempData
                    myData.drawLineSpectrum()
                
            except TypeError: 
                print(" Wrong file name or file type!")
        # ABSOLUTE ABSORPTION        
        #myData.get_absorption()
        #myData.drawLineAbsorption()
        
        # RELATIVE ABSORPTION
        myData.get_rel_abs()
        myData.draw_rel_absorption(myData.rel_absorption)
        input("second")
        myData.get_rel_abs()
        myData.draw_rel_absorption(myData.rel_absorption)

    input("bye")

            

        
        


        

        

        
                        
                                
                                
                        
                        



