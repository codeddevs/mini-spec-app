# Copyright (c) 2025 Coded Devices Oy
#
# file : mini_main.py
# ver  : 2025-2-14
# desc : Main file of the Mini Spectormeter Python3 application.
#	 	 Communication with the hardware via FTDI VCP drivers.
# TODO : - Correct intensity calibration so that highest point of the spectrum
#        maintains its value.
#        - Change command 'one' to ask a wavelength instead of channel nr.
#        - Check if port is open before further action.
#        
#
import matplotlib.pyplot as plt
import mini_file_operations as fop
import mini_temp
from mini_data import mini_data
#from mini_timed_data import mini_timed_data
from mini_instrument import mini_instrument
from mini_timed_multi_data import mini_timed_multi_data
import mini_settings as settings
#import mini_color as color
import mini_gui
from datetime import datetime
import time
import threading
import tkinter as tk

# VERSION
# UPDATE THE VERSION NUMBER/DATE ONLY HERE
app_version = "2025-2-16"

class MainApp:
    
    # edit 2025-2-16
    def __init__(self):
        
        self.myData = mini_data()               # spectrum data
        self.myMultiTimedData = mini_timed_multi_data() # timed data points for default number of channels
        self.myInstrument = mini_instrument()
        self.data = []
        self.continuousActivated = False        # boolean for state of continuous measuring
        self.continuousInterval = 1             # interval of continuous readings in sec

        # Print Start info
        print("")
        print(" *** Mini Spec *** ")
        print(" Copyright (c) 2025 Coded Devices Oy")
        print(" PC Software version " + app_version)
        print(" Connecting to hardware...")
        print("")

        # Connect to the instrument
        # edit : 2025-2-16
        # desc : Connect to the instrument. Then 
        #        1) read back firmware version,
        #        2) read LED intensity from the settings file and send it to the instrument,
        #        3) read integration time from the settings file and send it to the instrument.  
        # todo : Separate error in returned LED value from old firmware not returning it.
        connected = self.myInstrument.openPort()
        if connected is True:

            # BLINK LED
            self.myInstrument.blink(2)
            
            # INIT FIRMWARE VERSION
            fw_version = self.myInstrument.getFirmwareVersion()
            print(" Firmware version : " + fw_version)

            # INIT LED INTENSITY
            LEDi = fop.read_LED_intensity()
            if (LEDi < 0 or LEDi > 31):
                LEDi = settings.hw_source_intensity
            new_LEDi = self.myInstrument.setSourceIntensity(LEDi)
            # requested LED intensity (but not returned because of old fw version or error)
            if (new_LEDi == -1):
                print(f' LED intensity : {LEDi}')
            # returned LED intensity
            else:
                print(f' LED intensity : {new_LEDi}')

            # INIT INTEGRATION TIME
            iTime = fop.read_integ_time()
            if (iTime < 10 or iTime > 500):
                iTime = settings.hw_integration_time
            new_iTime = self.myInstrument.setIntegrationTime(iTime)
            if(new_iTime != iTime):
                print(f' ERROR in setting integration time!')
            else:
                print(f' Integration time : {new_iTime} ms')

        else:
            fw_version = 'N.A.'

        # init
        fop.create_spectra_folder(settings.my_spectra_folder)

        # Start GUI
        self.root = tk.Tk()
        self.gui = mini_gui.GUI(self.root, self.GUI_callback)
        self.gui.update_version(app_version, fw_version)
        self.root.protocol('WM_DELETE_WINDOW', self.exit_app)
        print(f" Ready!")
        print('')
        self.root.mainloop()

       
    
    # CLOSE APP
    # edit : 2024-3-28
    def exit_app(self):
        print(' Closing the App, bye!')
        self.root.destroy()

        #close graphs
        self.myMultiTimedData.CloseTimedGraph()
        self.myData.CloseGraphs()


    # Callback message from GUI
    # edit : 2024-3-27
    # desc : Read command from inputCommand and possible keyword argument in kwargs
    def GUI_callback(self, inputCommand, **kwargs):
            
        if inputCommand == 'h':
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
            # for gui only 'gui_itime'
            # for gui only 'gui_sab' instead of 'sab'
            # for gui only 'gui_first_ch'
            # for gui only 'gui_another_ch'
            # for gui only 'gui_one_reset'
            # for gui only 'gui_timed_ch_count'
            # for gui only 'gui_draw_timed_graph'
            # for gui only 'gui_save_timed'
            # for gui only 'gui_start_timer'
            # for gui only 'gui_stop_timer'
            # 'gui_input_state'
            print("q : quit")
        
        # INTEGRATION TIME W GUI
        # edit : 2025-2-16
        elif inputCommand == 'gui_itime':
            print(' Change integration time')
            if 'time' in kwargs:
                itime = kwargs['time']

                # save to file
                try:
                    fop.save_integ_time(itime)
                except FileNotFoundError:
                    print(f' Error in saving integration time!')             
                
                # send to instrument
                try:
                    new_itime = self.myInstrument.setIntegrationTime(itime)
                    if new_itime != itime:
                        print(" Error in reading back the new integration time value!")
                    else:         
                        print(f" Integration time set : {new_itime} ms")
                except ValueError:
                    print(" Error : Incorrect integration time!")

            else:
                print(" Error : No integration time!")

        # READ FULL SPECTRUM (ALL CHANNELS)
        # edit : 2023-12-15
        elif inputCommand == 'r':
            if(self.myInstrument.getSpectrum(self.myData.data) == 1):
                self.myData.channelToWavelength()
                self.myData.data_file_name = ""         # data in memory
                self.myData.drawLineSpectrum()
                self.myData.added_to_average = False    # new data
        
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
        # ver 2023-12-15
        # desc : Use unit info to choose proper draw method. 
        #        Note! Does not work in VSCode environment.
        # todo : Select proper data type for returned spectrum (data or rel_absoption).
        #        Test if deepcopy is required.
        #        Error in drawing the spectrum may cause exception with misleading 
        #        print "Wrong file name or file type!"
        #        
        elif inputCommand == 'l':
            print(" Load from file")
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
                    self.myData.added_to_average = False # can be added to average

                except TypeError: 
                    print(" Wrong file name or file type!")
            
        # REMOVE BACKGROUND
        # ver 19.8.2022
        elif inputCommand == 'b':
            self.myData.removeBackground(settings.my_spectra_folder + settings.background_file_name)
            self.myData.drawLineSpectrum()

        # ADD A SPECTRUM TO AVERAGE
        # ver 2023-12-15
        elif inputCommand == 'a':
            print("Add to average")
            if (self.myData.added_to_average == False):
                self.myData.addSpectrumToAverage()
                print(" Average contains now " + str(self.myData.ave_size) + " spectrums.")
                self.myData.drawLineAverage()
            else:
                print(" Can't be added multiple times")

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

        # elif inputCommand == 'm':
        #     print(' Max intensity at wavelength : %.2i nm' %mini_temp.find_maximum_l(self.myData.data))
        #     print(' Temp = %.3f K' %mini_temp.get_bb_temp(self.myData.data))

        elif inputCommand == 'f':
            print(' low-pass filtration done')
            self.myData.data = mini_temp.lowpass_filter(self.myData.data)
            self.myData.drawLineSpectrum()

        # CONTINUOUSLY ONE CHANNEL ONCE PER SEC
        # edit : 2023-12-15
        # TODO : Condsider combining 'one' with 'p'
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
                        (ch_nr, ch_val) = self.myInstrument.getOneChannel(self.myData.waveLengthToChannel(int(wave_length)))
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
        # edit 2023-12-15
        # TODO : Condsider combining 'one' with 'p'
        elif inputCommand == 'one':
            
            wave_length = input(" Give a wave length (313...882)")
            ch_number = self.myData.waveLengthToChannel(int(wave_length))
            if(ch_number < 1):
                print(' ' + wave_length + ' nm is too SHORT a wave length for the hardware.')
            elif (ch_number > settings.hw_channel_count):
                print(' ' + wave_length + ' nm is too LONG a wave length for the hardware.')
            else:
                (ch_nr, ch_val) = self.myInstrument.getOneChannel(self.myData.waveLengthToChannel(int(wave_length)))

        # edit 2024-3-20
        # desc : Ask uc to measure a new spectrum and the to send the value of the channel matching the selected wavelength.
        #        -1 one used as bad value, and it can be coming also from the myInstrument.getOneChannel
        elif inputCommand == 'gui_first_ch':

            ch_nr = -1     # init with bad values
            ch_val = -1

            wave_length = int(kwargs['wavelength'])
            ch_number = self.myData.waveLengthToChannel(wave_length)
             
            if(ch_number < 1):
                print(' ERROR: ' + wave_length + ' nm is too SHORT a wave length for the hardware.')
            elif (ch_number > settings.hw_channel_count):
                print(' ERROR:' + wave_length + ' nm is too LONG a wave length for the hardware.')
            else:
                (ch_nr, ch_val) = self.myInstrument.GetFirstChannel(ch_number)
            
            try:
                self.myMultiTimedData.AddDataPoint(0, ch_val, time.time() - self.myMultiTimedData.startTime)
                self.myMultiTimedData.AddChWavelength(0, str(wave_length))
            
            except ValueError as e:
                print(str(e))

            return (ch_nr, ch_val)
        
        # ANOTHER VALUE FROM MEASURED SPECTRUM
        # edit : 2024-2-27
        # desc : Get another channel value from already measured spectrum.
        #        Use the timestamp of the first channel of this same spectrum data.
        elif inputCommand == 'gui_another_ch':

            ch_nr = -1     # init with bad values
            ch_val = -1

            wave_length = int(kwargs['wavelength'])
            ch_index = int(kwargs['index'])
            ch_number = self.myData.waveLengthToChannel(wave_length)
            
            if(ch_index < 0 or ch_index > self.myMultiTimedData.ch_count):
                print(' ERROR: Channel index outside of expected range 0...%i!' %self.myMultiTimedData.ch_count)

            if(ch_number < 1):
                print(' ERROR: ' + wave_length + ' nm is too SHORT a wave length for the hardware.')
            elif (ch_number > settings.hw_channel_count):
                print(' ERROR:' + wave_length + ' nm is too LONG a wave length for the hardware.')
            else:
                (ch_nr, ch_val) = self.myInstrument.GetAnotherChannel(ch_number)
            
            try:
                last_ts = self.myMultiTimedData.GetLatestTimestamp()
                self.myMultiTimedData.AddDataPoint(ch_index, ch_val, last_ts)
                self.myMultiTimedData.AddChWavelength(ch_index, str(wave_length))
                #self.myMultiTimedData.DrawTimedGraph()
            except ValueError as e:
                print(str(e))

            return (ch_nr, ch_val)

        # START TIMER OF CONTINUOUS MEASUREMENT
        # edit : 2024-3-15
        # desc : interval is in seconds        
        elif inputCommand == 'gui_start_timer':
            self.continuousInterval = int(kwargs['interval'])
            self.continuousActivated = True
            print(' Continuous measuring started!')
            threading.Timer(self.continuousInterval, self.TimerInterruptHandler).start()
        
        # STOP TIMER OF CONTINUOUS MEAUSREMENT
        # edit : 2024-3-15
        elif inputCommand == 'gui_stop_timer':
            self.continuousActivated = False  

        # SAVE TIMED CHANNEL DATA INTO FILE
        # edit : 2024-3-10
        elif inputCommand == 'gui_save_timed':
            try:
                file_name = kwargs['filename']
                comment = kwargs['comment']
                fop.WriteTimedFile(self.myMultiTimedData.timed_data, file_name, comment)
            except Exception as e:
                print(' ERROR in writing timed file!')
                print(str(e))

        # DRAW MULTI TIMED GRAPH
        # edit : 2024-2-25
        elif inputCommand == 'gui_draw_timed_graph':
            self.myMultiTimedData.DrawTimedGraph()
            self.myMultiTimedData.PrintLastDataRow()
        
        # SET THE NUMBER OF TIMED CHANNELS (1...9)
        # edit : 2024-2-23
        elif inputCommand == 'gui_timed_ch_count':
            self.myMultiTimedData = mini_timed_multi_data(int(kwargs['count']))

        # edit : 2024-3-17
        # NOT READY! Consider copying all wavelengths as one array instead of one by one.        
        elif inputCommand == 'gui_timed_add_wavelength':
            self.myMultiTimedData.AddChWavelength(kwargs['index'], kwargs['wavelength'])

        # edit 2024-2-11
        # desc: Reset time series of channels and clear the graph.
        elif inputCommand == 'gui_one_reset':
            #self.myTimedData.CloseTimedGraph()
            #self.myTimedData.ClearTimedData()
            self.myMultiTimedData.CloseTimedGraph()
            self.myMultiTimedData.ClearTimedData()

        # CHANGE SOURCE (LED) INTENSITY VIA GUI
        # edit : 2025-2-16
        # desc : Save the new LED value in to the settings file, then send it to the instrument.
        elif inputCommand == 'gui_int':
            print(' Change LED intensity')
            if 'led_intensity' in kwargs:
                LED_int = kwargs['led_intensity']
                # save to file
                try:
                    fop.save_LED_intensity(LED_int)
                except FileNotFoundError:
                    print(f' Error in saving LED setting!')             
                # send to instrument
                try:
                    new_LED_int = self.myInstrument.setSourceIntensity(LED_int)
                    # old firmware does not return the set value, -1 instead
                    if new_LED_int == -1:
                        print(f" LED intensity set : {LED_int}")
                    # new firmware does return the set value
                    elif new_LED_int == LED_int:         
                        print(f" LED intensity set : {new_LED_int}")
                    # unexpected value 
                    else:
                        print(f" ERROR in reading back the new LED intensity value : {new_LED_int}!")
                
                except ValueError:
                    print(" Error : Incorrect LED intensity value!")
            else:
                print(" Error : No new LED instensity value defined!")
            
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
            print(" Draw spectrum in memory")
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
        # edit : 2023-12-27
        elif inputCommand == 'ask_ave_count':
            return self.myData.ave_size
        
        # ASK EXTERN INPUT STATE
        # edit : 2024-3-28
        elif inputCommand == 'gui_input_state':
            state = self.myInstrument.AskInputState()
            if (state == 'W0'):
                return 'LOW'
            elif state == 'W1':
                return 'HIGH'
            else:
                return 'ERROR'

        # QUIT
        elif inputCommand == 'q':
            print("Quit")
            if self.connected is True:
                self.myInstrument.setSourceIntensity(0) # turn LED off
            print('Bye!')
            exit()

        else:
            print('Unknown command!')
   

    # edit : 2024-3-15
    # desc : Interrupt handler for timer of the continuous measurement. 
    def TimerInterruptHandler(self):
        #print('time out!')

        # read one channel TEST CODE
        ch_nr = -1
        ch_val = -1
        wave_length = 555
        ch_number = self.myData.waveLengthToChannel(wave_length)
        try:
            (ch_nr, ch_val) = self.myInstrument.GetFirstChannel(ch_number)
            self.myMultiTimedData.AddDataPoint(0, ch_val, time.time() - self.myMultiTimedData.startTime)
        except ValueError as e:
            print(str(e))

        self.myMultiTimedData.DrawTimedGraph()
        self.myMultiTimedData.PrintLastDataRow()
        

        if (self.continuousActivated):
            threading.Timer(self.continuousInterval, self.TimerInterruptHandler).start()
            return(1, 112)
        else:
            print(' Continuous measuring stopped!')  


# edit 2023-10-6
if __name__ == "__main__":
    app = MainApp()
    



	
