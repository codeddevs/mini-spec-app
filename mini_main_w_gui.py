# Copyright (c) 2023 Coded Devices Oy

# file : mini_main_w_gui.py
# ver  : 2023-9-15
# desc : Main file of the Mini Spectormeter Python3 application.
#	 	 Communication with the hardware via FTDI VCP drivers.
# TODO : - Correct intensity calibration so that highest point of the spectrum
#        maintains its value.
#        - Change command 'one' to ask a wavelength instead of channel nr.
#        - Check if port is open before further action.
#        
#
#       
#
import matplotlib.pyplot as plt
import mini_file_operations as fop
import mini_temp
from mini_data import mini_data
from mini_instrument import mini_instrument
import mini_settings as settings
import mini_color as color
import mini_gui
from datetime import datetime
import time
import tkinter as tk


# edit 2023-9-15
class MainApp:
    #def __init__(self, root):
    def __init__(self):
        #self.root = root
        self.myData = mini_data()
        self.myInstrument = mini_instrument()
        self.data = []

        # Connect to the instrument
        connected = self.myInstrument.openPort()
        if connected is True:
            self.myInstrument.blink(2)
            self.myInstrument.printFirmwareVersion()
            self.myInstrument.setSourceIntensity(settings.hw_source_intensity)
            print(" Source intensity : " + str(settings.hw_source_intensity))    

        # init
        fop.create_spectra_folder(settings.my_spectra_folder)

        # Start GUI
        self.root = tk.Tk()
        self.gui = mini_gui.GUI(self.root, self.GUI_callback)   
        self.root.mainloop() 

    # Callback message from GUI
    # edit : 2023-8-25
    # desc : Read command from inputCommand and possible keyword argument in kwargs
    def GUI_callback(self, inputCommand, **kwargs):
            
        if inputCommand == 'h':
            print("i : increase integration time")
            print("r : measure new spectrum")
            print("l : load saved spectrum")
            print("s : save spectrum") 
            print("b : remove background (" + settings.my_spectra_folder + settings.background_file_name + ")")
            print("a : add to average")
            print("sa : save average")
            print("ca : clear average")
            print("c : CIE coordinates")
            print("d : remove dc")
            print("m : find max")
            print("f : filter")
            print("p : point to source (continuous)")
            print("n : intensity correction (" + settings.my_spectra_folder + settings.intensity_calib_file + ")")
            print("o : get absorption using reference (" + settings.my_spectra_folder + settings.zero_reference_file + ")")
            print("g : gain")
            print("cab : calculate relative absorption")
            print("sab : save relative absorption")
            print("one : read one channel")
            print("int : change source intensity 0...31")

            print("ds : draw spectrum in memory")
            print("da : draw average in memory")
            print("dab : draw absorption in memory")
            print("clg : clear absolute graph")
            print("clr : clear relative (absorption) graph")       
            # for gui only 'ask_gui'
            # for gui only 'gui_int'
            # for gui only 'gui_sab' instead of 'sab'
            print("q : quit")

        # INTEGRATION TIME
        # ver 30.10.2020
        elif inputCommand == 'i':
            print("Increase integration time")
            try:
                newTime = self.myInstrument.setIntegrationTime()
                print('new integration time: %i' %newTime)
            except Exception as x:
                print(x)

        # READ FULL SPECTRUM (ALL CHANNELS)
        # edit : 2023-9-1
        elif inputCommand == 'r':
            if(self.myInstrument.getSpectrum(self.myData.data) == 1):
                self.myData.channelToWavelength()
                self.myData.data_file_name = ""                      # data in memory
                self.myData.drawLineSpectrum()
        
        # SAVE DATA FROM MEMORY TO FILE
        # edit : 2023-9-22
        # desc : Get necessary input arguments in **kwargs
        elif inputCommand == 's':
            if 'filename' in kwargs:
                file_name = kwargs['filename']
            else:
                file_name = ''
            
            if 'comment' in kwargs:
                file_comment = kwargs['comment']
            else:
                file_comment = ''
            
            ret_val = fop.write_file(self.myData.data, file_name, file_comment)
            
            # check if successful and return accordingly       
            if(ret_val == 1):
                print(" spectrum saved in " + file_name)
                self.myData.data_file_name = file_name
                return file_name
            else:
                return ''

        # LOAD FROM FILE
        # ver 2023-9-1
        # desc : Use unit info to choose proper draw method. 
        #        Note! Does not work in VSCode environment.
        # todo : Select proper data type for returned spectrum (data or rel_absoption).
        #        Test if deepcopy is required.
        #        
        elif inputCommand == 'l':
            print("Load from file")
            file_name = kwargs['filename']
            print(file_name)
            #file_name = input("File name in folder " + settings.my_spectra_folder + " ?: ")
            tempData = []
            tempData, unit = fop.read_file(file_name)
            #myData.data_file_name = file_name
            if tempData != -1: # error in reading file       
                try:
                    self.myData.data_file_name = file_name
                    # % 
                    if unit == '%':
                        self.myData.rel_absorption = tempData
                        self.myData.draw_rel_absorption(self.myData.rel_absorption)
                    # bits 
                    else:
                        self.myData.data = tempData
                        self.myData.drawLineSpectrum()
                    
                except TypeError: 
                    print(" Wrong file name or file type!")
            
        # REMOVE BACKGROUND
        # ver 19.8.2022
        elif inputCommand == 'b':
            self.myData.removeBackground(settings.my_spectra_folder + settings.background_file_name)
            self.myData.drawLineSpectrum()

        # ADD A SPECTRUM INTO AVERAGE
        # ver 29.5.2022
        elif inputCommand == 'a':
            print("Add to average")
            self.myData.addSpectrumToAverage()
            print(" Average contains now " + str(self.myData.ave_size) + " spectrums.")
            self.myData.drawLineAverage()

        # SAVE AVERAGE
        # edit : 2023-9-29
        # desc : This version is to be used with GUI
        #        The filename is delivered in arguments instead of terminal input.
        elif inputCommand == 'sa':
            print("Saving average of " + str(self.myData.ave_size) + ":")
            #file_name = input("file name (empty for date-time name)?:")
            file_name = kwargs['filename']
            # if(len(file_name) != 0):
            #     file_name = settings.my_spectra_folder + file_name
            # else:
            #     time_stamp = datetime.now()
            #     file_name = settings.my_spectra_folder + time_stamp.strftime("%Y-%m-%d %H.%M.%S.txt")
            # file_comment = input("add comment ?: ")
            # if len(file_comment) == 0:
            #     file_comment = 'average'

            file_comment = 'This is average!'
            ret_val = fop.write_file(self.myData.average, file_name, file_comment)
            
            # check if successful        
            if(ret_val == 1):
                print(" average spectrum saved in " + file_name)
    
        # CLEAR AVERAGE - remove spectrums from average array and reset average counter
        # ver 2023-9-22
        elif inputCommand == 'ca':
            #print("Clear average, contains " + str(self.myData.ave_size) + " spectrums?")
            #answer = input("Y/N:")
            #if(answer == "Y" or answer == 'y'):
                self.myData.average = []
                self.myData.ave_size = 0
                print(" Average cleared!")
        
        # CALCULATE CIE TRISTIMULUS VALUES X, Y AND Z
        elif inputCommand == 'c':

            # NEW METHOD 9.10.2020
            XYZ = color.calc_XYZ_coords(self.myData.data)
            print(" TRISTIMULUS VALUES :")
            print(" X = %.2f" %XYZ[0])
            print(" Y = %.2f" %XYZ[1])
            print(" Z = %.2f" %XYZ[2])

        # REMOVE DC
        # ver 31.3.2021
        elif inputCommand == 'd':
            self.myData.removeDC(self.myData.estimate_dc())
            #myData.remove_any_dc(myData.data, myData.estimate_any_dc(myData.data))
            self.myData.drawLineSpectrum()

        elif inputCommand == 'm':
            print(' Max intensity at wavelength : %.2i nm' %mini_temp.find_maximum_l(self.myData.data))
            print(' Temp = %.3f K' %mini_temp.get_bb_temp(self.myData.data))

        elif inputCommand == 'f':
            print(' low-pass filtration done')
            self.myData.data = mini_temp.lowpass_filter(self.myData.data)
            self.myData.drawLineSpectrum()

        # CONTINUOUSLY ONE CHANNEL ONCE PER SEC
        # edit : 2023-5-5
        # TODO : Better output with time stamp and graph!
        elif inputCommand == 'p':
            wave_length = input('Give a wave length:')
            ch_number = self.myData.waveLengthToChannel(int(wave_length))
            
            if(ch_number < 1):
                print(' ' + wave_length + ' nm is too SHORT a wave length for the hardware.')

            elif (ch_number > settings.hw_channel_count):
                print(' ' + wave_length + ' nm is too LONG a wave length for the hardware.')
            
            else:
                print(' Starting continuous mode. Press Ctrl+C to end. ')
                try:
                    while True:
                        self.myInstrument.getOneChannel(self.myData.waveLengthToChannel(int(wave_length)))
                        time.sleep(0.8)
                except KeyboardInterrupt:
                    print("Stopped!")
                self.myInstrument.clearInputBuffer()


        # INTENSITY CORRECTION
        # ver 11.5.2022
        # TODO : Use estimate_dc to check if there is a significant dc-value,
        #        then remove it automatically before int_calibration and
        #        return it afterwards, info user.
        #

        elif inputCommand == 'n':
            calib_file = settings.my_spectra_folder + settings.intensity_calib_file

            ref_wavelength = (int)(input("Give the reference wavelength (nm)!"))
            if ref_wavelength < 320 or ref_wavelength > 880:
                print("That is outside of the range, let's use the HIGHEST POINT.")
                ref_wavelength = 0
        
            try:
                self.myData.loadIntCalib(calib_file)
                self.myData.intCorrect(ref_wavelength)
                self.myData.drawLineSpectrum()
            except FileNotFoundError:
                print("File " + calib_file + " was not found!")

        # ABSORPTION SPECTRUM
        # ver 10.9.2020
        # 
        elif inputCommand == 'o':
            print("Reading zero reference file...")
            self.myData.get_absorption() 
            self.myData.drawLineAbsorption()
        
        # CALC RELATIVE ABSORPTION
        # edit : 2023-8-27
        # Compare to zero_reference data
        elif inputCommand == 'cab':
            print(" Calculating relative absorption... ")
            if 'filename' in kwargs:
                file_name = kwargs['filename']
                print(" Zero reference file: " + file_name)
                self.myData.get_rel_abs_from_file(file_name)
                self.myData.draw_rel_absorption(self.myData.rel_absorption)
            else:
                print(" Default zero reference file (see mini_settings.py)")
                if(self.myData.get_rel_abs() != -1): # default file found
                    self.myData.draw_rel_absorption(self.myData.rel_absorption)

        # SAVE RELATIVE ABSORPTION
        # ver 20.5.2022
        elif inputCommand == 'sab':
            file_name = input("file name (empty for date-time name)?:")
            if(len(file_name) != 0):
                file_name = settings.my_spectra_folder + file_name
            else:
                time_stamp = datetime.now()
                file_name = settings.my_spectra_folder + time_stamp.strftime("%Y-%m-%d %H.%M.%S.txt")
            file_comment = input("add comment ?: ")
            if len(file_comment) == 0:
                file_comment = 'Relative absorption'
            if(len(self.myData.rel_absorption) > 1):
                ret_val = fop.write_file(self.myData.rel_absorption, file_name, file_comment, '[%]')
            
            # check if successful        
            if(ret_val == 1):
                print(" absorption saved in " + file_name)

        # SAVE RELATIVE ABSORPTION - GUI VERSION
        # edit 2023-10-6
        # desc : give file name in input parameters ('gui_sab', filename='xxxx')
        elif inputCommand == 'gui_sab':
            file_name = kwargs['filename']
            file_comment = 'Relative absorption'
            if(len(self.myData.rel_absorption) > 1):
                ret_val = fop.write_file(self.myData.rel_absorption, file_name, file_comment, '[%]')
            else:
                print(' Error: No absorption data to save!')

            # check if successful        
            if(ret_val == 1):
                print(" absorption saved in " + file_name)

        # READ ONE CHANNEL
        # ver 5.5.2023
        # TODO : Instead of channel number ask wave length
        elif inputCommand == 'one':
            #channel_nr = input(" Give a channel (1...288): ")
            #myInstrument.getOneChannel(channel_nr)
            wave_length = input(" Give a wave length (313...882)")
            ch_number = self.myData.waveLengthToChannel(int(wave_length))
            if(ch_number < 1):
                print(' ' + wave_length + ' nm is too SHORT a wave length for the hardware.')
            elif (ch_number > settings.hw_channel_count):
                print(' ' + wave_length + ' nm is too LONG a wave length for the hardware.')
            else:
                self.myInstrument.getOneChannel(self.myData.waveLengthToChannel(int(wave_length)))

        # CHANGE SOURCE INTENSITY VIA GUI
        # edit : 2023-9-15
        elif inputCommand == 'gui_int':
            print(' Change LED intensity')
            if 'led_intensity' in kwargs:
                LED_int = kwargs['led_intensity']
                print(' New LED intensity = ' + str(LED_int))
                try:
                    self.myInstrument.setSourceIntensity(LED_int)
                except ValueError:
                    print(" Error : Incorrect intensity value!")
            else:
                print(" Error : No LED instensity value!")
            
        # CHANGE SOURCE INTENSITY
        # ver 29.4.2022
        elif inputCommand == 'int':
            print("Change source intensity")
            if self.connected is True:
                LED_int = input(" Give intensity (0...31): ")
                try:
                    self.myInstrument.setSourceIntensity(LED_int)
                except ValueError:
                    print(" Incorrect intensity value!")
            else:
                print(" No connection to hardware. ")   

        # GAIN
        # ver 7.1.2021
        #
        elif inputCommand == 'g':
            gain = (float)(input("Give gain coefficient"))
            self.myData.multiply(gain)
            self.myData.drawLineSpectrum()

        # DRAW SPECTRUM IN MEMORY
        # ver 29.5.2022
        elif inputCommand == 'ds':
            print("Draw spectrum in memory")
            if(len(self.myData.data) > 1):
                self.myData.drawLineSpectrum()
            else:
                print(" No spectrum in memory!")

        # DRAW AVERAGE IN MEMORY
        # ver 29.5.2022
        elif inputCommand == 'da':
            print("Draw average in memory")
            if(len(self.myData.average) > 1):
                self.myData.drawLineAverage()
            else:
                print(" No average in memory!")
        
        # CLEAR ABSOLUTE GRAPH
        # edit : 2023-8-25
        elif inputCommand == 'clg':
            print("Clearing the absolute graph...")
            self.myData.ClearLineSpectrum()

        # CLEAR RELATIVE (ABSORPTION) GRAPH
        # edit : 2023-8-27
        elif inputCommand == 'clr':
            print("Clearing the relative (absorption) grap...")
            self.myData.ClearRelAbsSpectrum()
            #self.myData.init_rel_graph()

        # ASK MEAS SOURCE
        # edit : 2023-9-1
        elif inputCommand == 'ask_meas_file':
            print("send to gui : " + self.myData.data_file_name)
            return self.myData.data_file_name
        
        # ASK AVE COUNT
        # edit : 2023-9-8
        elif inputCommand == 'ask_ave_count':
            print(" Average contains " + str(self.myData.ave_size) + " measurements." )
            return self.myData.ave_size

        # QUIT
        elif inputCommand == 'q':
            print("Quit")
            if self.connected is True:
                self.myInstrument.setSourceIntensity(0) # turn LED off
            print('Bye!')
            exit()


        else:
            print('Unknown command!') 


# edit 2023-10-6
if __name__ == "__main__":
    
    print("")
    print(" *** Mini Spec *** ")
    print(" Copyright (c) 2023 Coded Devices Oy")
    print(" PC Software version 2023-10-6")
    print(" Connecting to hardware...")
    print("")
  
    app = MainApp()
    



	
