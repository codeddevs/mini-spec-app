# Copyright (c) 2025 Coded Devices Oy

# Mini Spec App GUI
# edit 2025-5-27
# todo : 

import tkinter
from tkinter import ttk
from tkinter import filedialog
from tkinter import * 
from tkinter import messagebox
import time
import threading
from datetime import datetime

import importlib
#import mini_settings
import mini_file_operations as fop
import mini_defaults


# edit : 2025-4-24
class GUI:
    
    #edit : 2025-1-17
    def __init__(self, root, callback):

        self.callback = callback
        self.root = root
        self.root.title("Mini Spec App by Coded Devices")
        #self.default_file_location = "c:"   # mini_settings.my_spectra_folder
        self.app_version = ""               # MainApp constructor sets version during start up
        self.continuousActivated = False
        self.continuousInterval = 1000      # in ms
        self.continuousCount = 0            # number of measured sets of selected channels in continuous mode

        # NOTEBOOK & STYLE definition
        self.notebook = ttk.Notebook(self.root)
        self.notebook.configure(padding=(5, 5))
        self.my_style = ttk.Style()
        #self.my_style.theme_use('winnative') # 'winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative'
        self.my_style.theme_use('default') # 'winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative'

        self._initialize_tab_MEAS()
        self._initialize_tab_ABSORP()
        self._initialize_tab_TIMED()                       
        self._initialize_tab_SETTINGS()
        self._initialize_tab_TEST()
    # END OF __init__ ***
        
    # TAB 'MEAS' for making and loading measurements
    # edit : 2023-9-15
    def _initialize_tab_MEAS(self):
    
        page_meas = ttk.Frame(self.notebook, padding='5')
        page_meas.grid(column=0, row=0, sticky=(N, W, E, S))    # fill grid cell
        
        # NEW button to start measurement
        self.button_new_new = ttk.Button(page_meas, text='NEW', command=self.button_new_click)
        self.button_new_new.grid(row=1, column=1, padx=5, pady=7, sticky=W)

        # LOAD button for a saved spectrum
        self.button_load=ttk.Button(page_meas, text='LOAD', command=self.button_load_click)
        self.button_load.grid(row=2, column=1, padx=5, pady=7, sticky=W)

        # SAVE button to save a spectrum into a file
        self.button_save = ttk.Button(page_meas, text='SAVE', command=self.button_save_click)
        self.button_save.grid(row=3, column=1, padx=5, pady=7, sticky=W)
        
        # CLEAR button to erase measurement from memory
        self.button_new_clear = ttk.Button(page_meas, text='CLEAR', command=self.button_new_clear_click)
        self.button_new_clear.grid(row=4, column=1, padx=5, pady=7, sticky=W)

        # REDRAW button to draw spectrum from memory
        self.button_new_redraw = ttk.Button(page_meas, text='REDRAW', command=self.button_new_redraw_clicked)
        self.button_new_redraw.grid(row=4, column=2, padx=5, pady= 7, sticky=W)

        # information about current measurement 
        self.str_meas_source = tkinter.StringVar(page_meas, 'No measurement in memory.')
        label_new_state = ttk.Label(page_meas, textvariable=self.str_meas_source)
        label_new_state.grid(row=1, column=3, padx=5, pady=7)

        self.notebook.add(page_meas, text=' MEAS ')

    # TAB 'ABSORP' for calculating absoption spectra
    # edit : 2024-2-26
    def _initialize_tab_ABSORP(self):
        

        page_abs = ttk.Frame(self.notebook, padding='5')
        self.notebook.add(page_abs, text=' ABSORP ')

        # reference topic
        label_ref_topic = ttk.Label(page_abs, text = 'Reference:')
        label_ref_topic.grid(column=1, row=2, padx=5, pady=7, sticky=W)
        
        # reference file path label
        self.ref_file_name_var = tkinter.StringVar(page_abs)
        label_ref_file_name = ttk.Label(page_abs, textvariable = self.ref_file_name_var)
        label_ref_file_name.grid(column=2, row=2, padx=5, pady=7, sticky=W)

        # source topic
        label_source_topic = ttk.Label(page_abs, text='Measurement:')
        label_source_topic.grid(column=1, row=3, padx=5, pady=7)
        
        # measurement source
        self.str_abs_meas_source = tkinter.StringVar(page_abs, '...')
        label_meas_source = ttk.Label(page_abs, textvariable=self.str_abs_meas_source)  
        label_meas_source.grid(column=2, row=3, padx=5, pady=7, sticky=W)
        #self.str_abs_meas_source.set(callback('ask_meas_file'))

        # edit 2025-4-20
        try:
            #file_path = fop.read_zero_path(True) # True --> give warning if file missing
            file_path = fop.read_settings_file("files", "zero_reference_file")
            file_path = self.cut_long_filename(file_path) # cut long file paths --> more readable
        except TypeError:
            file_path = ''
            print(' Error: Reference filepath is not correct!')
        self.ref_file_name_var.set(file_path)
        
        button_change_file = ttk.Button(page_abs, text='Change', command= self.button_browse_file_click)
        button_change_file.grid(column=3, row=2, padx=5, pady=7)

        button_calc_abs = ttk.Button(page_abs, text="CALC ABS", command=self.button_calc_abs_click)
        button_calc_abs.grid(row=5, column=1, padx=5, pady=7, sticky=W)

        button_save_abs = ttk.Button(page_abs, text='SAVE ABS', command=self.button_save_abs_click)
        button_save_abs.grid(row=6, column=1, padx=5, pady=7, sticky=W)

        button_clear_abs = ttk.Button(page_abs, text="CLEAR ABS", command=self.button_clear_abs_click)
        button_clear_abs.grid(row=7, column=1, padx=5, pady=7, sticky=W)

    # __init__ TAB 'TIME D' for time domain measurements of selected channels
    # edit : 2024-3-20
    def _initialize_tab_TIMED(self):
        
        page_timed = ttk.Frame(self.notebook)
        self.notebook.add(page_timed, text=' TIME D ', padding='5')

        # todo : user selectable number of channels 
        self.channel_list = []
        self.channel_count = 3 # this is the only place for setting the channel count
        self.callback('gui_timed_ch_count', count=self.channel_count) # number of channels to main for a suitable data array

        self.labelFr_chs = ttk.LabelFrame(page_timed, text='Channels')
        self.labelFr_chs.grid(row=1, column=1, padx=5, pady=7, sticky='NW')
        
        for i in range(self.channel_count):

            temp_str = tkinter.StringVar(self.labelFr_chs, str(450 + i*50))
            temp_label = ttk.Label(self.labelFr_chs, text='Channel #' + str(i+1) + ':')
            temp_label.grid(row = i+1, column=1, padx=5, pady=7, sticky=W)

            temp_entry = ttk.Entry(self.labelFr_chs, width=3, textvariable=temp_str, validate='focusout', validatecommand=self.new_wavelength)
            temp_entry.grid(row = i+1, column=2, padx=5, pady=7, sticky=W)
            #self.channel_list.append(Channel(temp_str, temp_label, temp_entry))
            self.channel_list.append(temp_str) # wavelength as tkinter string variable

            temp_label_after = ttk.Label(self.labelFr_chs, text='nm')
            temp_label_after.grid(row=i+1, column=3, padx=5, pady=7, sticky=W)
                
        self.button_read_chs = ttk.Button(page_timed, text='ONCE', command=self.button_read_chs_click)
        self.button_read_chs.grid(row=5, column=2, padx=5, pady=7, sticky=W)

        self.button_reset_serie = ttk.Button(page_timed, text='RESET', command=self.reset_serie_button_click)
        self.button_reset_serie.grid(row=5, column=4, padx=5, pady=7, sticky=W)

        self.button_save = ttk.Button(page_timed, text='SAVE', command=self.save_timed_button_click)
        self.button_save.grid(row=5, column=3, padx=5, pady=7, sticky=E)

        self.labelFr_continuous = ttk.LabelFrame(page_timed, text='Continuous')
        self.labelFr_continuous.grid(row=1, column=2, padx=5, pady=7, sticky='NW')

        self.continuous_text = tkinter.StringVar(self.labelFr_continuous, 'START')
        self.button_continuous = ttk.Button(self.labelFr_continuous, textvariable=self.continuous_text, command=self.continuous_button_click)
        self.button_continuous.grid(row=3, column=1, padx=5, pady=7, sticky=W)
        
        self.label_interval = ttk.Label(self.labelFr_continuous, text='Interval:')
        self.label_interval.grid(row=1, column=1, padx=5, pady=7, sticky=E)
        
        self.str_interval = tkinter.StringVar(self.labelFr_continuous, '1')
        self.entry_interval = ttk.Entry(self.labelFr_continuous, textvariable=self.str_interval, width=5)
        self.entry_interval.grid(row=1, column=2, padx=5, pady=7, sticky=W)
        
        self.label_ms = ttk.Label(self.labelFr_continuous, text='sec')
        self.label_ms.grid(row=1, column=3, padx=5, pady=7, sticky=W)
        
        self.label_max_cnt = ttk.Label(self.labelFr_continuous, text='Max cnt:')
        self.label_max_cnt.grid(row=2, column=1, padx=5, pady=7, sticky=E)

        self.str_max_cnt = tkinter.StringVar(self.labelFr_continuous, '10')
        self.entry_max_cnt = ttk.Entry(self.labelFr_continuous, textvariable=self.str_max_cnt, width=5)
        self.entry_max_cnt.grid(row=2, column=2, padx=5, pady=7, sticky=W)

    def _initialize_tab_SETTINGS(self):
        # __init__ TAB 'SETTINGS' ************************************************************************
        # edit: 2024-4-24
        page_set = ttk.Frame(self.notebook)
        self.notebook.add(page_set, text=' SETTINGS ', padding='5')

        self.str_app_version = tkinter.StringVar(page_set, 'PC App Version: ?')
        
        self.str_fw_version = tkinter.StringVar(page_set, 'Firmware Version: ?')
        
        self.str_port = tkinter.StringVar(page_set, 'COM port name: ' + fop.read_settings_file("device", "comport_name"))
        label_port = ttk.Label(page_set, textvariable=self.str_port)
        label_port.grid(row=3, column=1, padx=5, pady=7, sticky=W)
        
        label_app_version = ttk.Label(page_set, textvariable=self.str_app_version)
        label_app_version.grid(row=1, column=1, padx=5, pady=7, sticky=W)

        label_fw_version = ttk.Label(page_set, textvariable=self.str_fw_version)
        label_fw_version.grid(row=2, column=1, padx=5, pady=7, sticky=W)

        # LED intensity control
        # edit 2025-4-25

        # use these hardcoded values if no better available
        min_intensity = 0
        max_intensity = 31
        default_intensity = 5

        labelfr_set_intensity = ttk.Labelframe(page_set, text=' LED intensity (0...31)')
        labelfr_set_intensity.grid(column=1, row=4, padx=5, pady=7, sticky=W)
        self.str_source_int = tkinter.StringVar(page_set, '')
        self.spin_intensity = ttk.Spinbox(labelfr_set_intensity, from_= min_intensity, to=max_intensity, width=2, validate='focusout', validatecommand=self.spin_intensity_change, textvariable=self.str_source_int)    
        
        try:
            LEDi = int(fop.read_settings_file("measurement", "hw_source_intensity" ))
            if (LEDi < min_intensity or LEDi > max_intensity):
                default_file_i = int(mini_defaults.DEFAULT_SETTINGS["measurement"]["hw_source_intensity"])
                if (default_file_i >= min_intensity and default_file_i <= max_intensity):
                    LEDi = default_file_i          
                else:
                    LEDi = default_intensity
                fop.update_settings_file("measurement", "hw_source_intensity", LEDi)

        except ValueError:
            print(f' ERROR in reading LED intensity value!')
            LEDi = default_intensity
            fop.update_settings_file("measurement", "hw_source_intensity", LEDi)

        self.str_source_int.set(LEDi)
        
        self.spin_intensity.grid(column=2, row=1, padx=10, pady=7)
        self.button_set_intensity = ttk.Button(labelfr_set_intensity, text=' SET ', command=self.button_set_intensity_click)
        self.button_set_intensity.grid(column=3, row=1, padx=5, pady=7)

        # INTEGRATION TIME control *************************
        # edit 2025-4-25

        # use these hardcoded values if no better is available
        min_itime = 10      # shortest possible integration time in ms
        max_itime = 500     # longest possible
        default_iTime = 25  # 

        labelfr_set_integration = ttk.Labelframe(page_set, text=' Integration time (ms)')
        labelfr_set_integration.grid(row=4, column=2, padx=5, pady=7, sticky=W)
        
        self.str_itime = tkinter.StringVar(labelfr_set_integration, '')
        self.spin_itime =ttk.Spinbox(labelfr_set_integration, from_=min_itime, to=max_itime, width=3, validate='focusout', validatecommand=self.spin_itime_change, textvariable=self.str_itime)
        
        try:
            iTime = int(fop.read_settings_file("measurement", "hw_integration_time"))
            if iTime < min_itime or iTime > max_itime:
                default_file_itime = int(mini_defaults.DEFAULT_SETTINGS["measurement"]["hw_integration_time"])
                if default_file_itime >= min_itime and default_file_itime <= max_itime:
                    iTime = default_file_itime
                else:
                    iTime = default_iTime
                fop.update_settings_file("measurement", "hw_integration_time", iTime)
        except ValueError:
            print(f' ERROR in reading integration time!')
            iTime = default_iTime
            fop.update_settings_file("measurement", "hw_integration_time", iTime)

        self.str_itime.set(iTime)
        
        self.button_set_itime = ttk.Button(labelfr_set_integration, text=' SET ', command=self.button_set_itime_click)
        self.button_set_itime.grid(row=1, column=2, padx=5, pady=7)
        
        self.spin_itime.grid(row=1, column=1, padx=5, pady=7, sticky=E)

    def _initialize_tab_TEST(self):
        # __init__ TAB 'TEST' ************************************************************************
        # edit: 2024-3-28
        page_test = ttk.Frame(self.notebook)
        self.notebook.add(page_test, text=' TEST ', padding='5')

        labelfr_test_input = ttk.LabelFrame(page_test, text='Extern Input')
        labelfr_test_input.grid(row=1, column=1, padx=5, pady=7)

        self.button_test_input = ttk.Button(labelfr_test_input, text='CHECK', command=self.button_test_input_click)
        self.button_test_input.grid(row=1, column=1, padx=5, pady=7)

        self.str_test_input = tkinter.StringVar(page_test, ' N.A. ')
        self.label_test_input = ttk.Label(labelfr_test_input, textvariable=self.str_test_input)
        self.label_test_input.grid(row=1, column=2, padx=5, pady=7)

        #self.LED_conn = 0
        #self.check_LED_conn = ttk.Checkbutton(labelfr_test_input, 'Connect LED to input', command=self.check_LED_conn_changed, variable=self.LED_conn)

        # ********************************************************************************************

        # Notebook in the root window
        #self.notebook.pack(expand=1, fill='both')
        self.notebook.grid(column=0, row=0, sticky=(N, W, S, E))

    # button_new event handler 
    def button_new_click(self):
        self.callback('r')
        self.str_meas_source.set('New unsaved measurement in memory!')
        self.str_abs_meas_source.set('New unsaved measurement')

    # button clear of the MEAS-page event handler
    # desc: Clears only the graph not the memory --> spectrum can be drawn again
    # edit : 2023-9-17
    def button_new_clear_click(self):
        self.callback('clg')

    # button REDRAW of NEW page event handler
    # tries to redraw the signal from memory
    # edit : 2023-9-17
    def button_new_redraw_clicked(self):
        self.callback('ds')

    # event handler for SET button in setting LED intensity
    # edit : 2025-2-15
    # desc : 
    def button_set_intensity_click(self):
        self.callback('gui_int', led_intensity = int(self.str_source_int.get()))

    # event handler for set button of integration time
    # edit : 2023-12-29
    def button_set_itime_click(self):
        self.callback('gui_itime', time = int(self.str_itime.get()))

    # button_load event handler
    # edit : 2023-9-22
    # desc : Windows tracks well previous file paths used.
    def button_load_click(self):
        load_name = filedialog.askopenfilename(title="Select file", filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
        if load_name !='':
            self.callback('l', filename = load_name)
            f = self.callback('ask_meas_file')
            #f = self.cut_long_filename(f)
            self.str_abs_meas_source.set(f)
            self.str_meas_source.set(f)

    # button_save event handler
    # edit : 2023-10-6
    # desc : test save name in case of Cancel button press
    def button_save_click(self):
        time_stamp = datetime.now()
        default_filename = time_stamp.strftime("meas %Y-%m-%d %H.%M.%S.txt")
        save_name = filedialog.asksaveasfilename(initialfile=default_filename)
        if save_name != '':
            f = self.callback('s', filename = save_name)
            self.str_meas_source.set(f)
            self.str_abs_meas_source.set(f)
            self.callback('ds')

    # button_clear event handler
    # edit: 2023-8-25
    def button_clear_click(self):
        self.callback('clg')

    # button_browse_file_click event handler
    # edit : 2025-4-20
    # desc : Saves automatically the selected file path in the settings file.
    def button_browse_file_click(self):
        zero_file = filedialog.askopenfilename(title = "Select file", filetypes = (("txt files", "*.txt"),("all files", "*.*")))
        
        if len(zero_file) > 0:
            self.ref_file_name_var.set('')
            #fop.save_zero_path(zero_file)
            fop.update_settings_file("files", "zero_reference_file", zero_file)
            self.ref_file_name_var.set(self.cut_long_filename(zero_file))

    # button_calc_abs_click event handler
    # edit : 2025-5-23
    # desc : If file path is OK, calls absorption calculation in mini_main.py.
    def button_calc_abs_click(self):
       
        ref_file = fop.read_settings_file("files", "zero_reference_file")
        
        if fop.Check_File_Path(ref_file) is True:
            self.callback('cab', filename = ref_file)
        else:
            print(f" ERROR: Reference file {ref_file} was not found!")  

    # button_save_abs_click event handler
    # edit : 2023-10-6
    def button_save_abs_click(self):
        time_stamp = datetime.now()
        default_filename = time_stamp.strftime("abs %Y-%m-%d %H.%M.%S.txt")
        save_name = filedialog.asksaveasfilename(title='Save As', initialfile=default_filename)
        self.callback('gui_sab', filename = save_name)

    # button clear_abs event handler
    # edit : 2023-8-27
    def button_clear_abs_click(self):
        self.callback('clr')

    # button add_to_ave event handler
    # edit : 2023-9-8
    def button_add_to_ave_click(self):
        self.callback('a')
        self.str_ave_count.set('AVE SIZE : ' + str(self.callback('ask_ave_count')))

    # edit : 2023-10-6
    def button_save_ave_click(self):
        time_stamp = datetime.now()
        default_filename = time_stamp.strftime("ave %Y-%m-%d %H.%M.%S.txt")
        save_name = filedialog.asksaveasfilename(initialfile=default_filename)
        if save_name != '':
            f = self.callback('sa', filename = save_name)

    # edit : 2023-9-29
    def button_clear_ave_click(self):
        self.callback('ca')
        self.str_ave_count.set('AVE SIZE : ' + str(self.callback('ask_ave_count')))

    # edit : 2023-9-15
    def spin_intensity_change(self):

        #temp_value = int(self.spin_intensity.get())
        temp_value = int(self.str_source_int.get())

        if temp_value < 0:
            temp_value = 0
        elif temp_value > 31:
            temp_value = 31

        #self.spin_intensity.set(temp_value)
        self.str_source_int.set('')
        self.str_source_int.set(str(temp_value))
        #self.root.after(50, lambda : messagebox.showinfo('spinbox', str(temp_value)))
        #messagebox.showinfo('spinbox', str(self.spin_intensity.get()))
        return True
    
    # edit : 2023-12-31
    # desc : validate values in itime spinner
    def spin_itime_change(self):
        temp_value = int(self.str_itime.get())
        min_time = int(self.spin_itime.config('from')[4])   # min val set in init
        max_time = int(self.spin_itime.config('to')[4])     # max val 
        
        if temp_value < min_time:
            temp_value = min_time
        elif temp_value > max_time:
            temp_value = max_time
        self.str_itime.set('')
        self.str_itime.set(str(temp_value))
        return True
    
    def test_validate(self):
        #temp_value = int(self.spin_intensity.get())
        temp_value = int(self.str_source_int.get())

        if temp_value < 0:
            messagebox.showinfo('spinbox', 'too small')
            return False
        elif temp_value > 31:
            messagebox.showinfo('spinbox', 'too large')
            return False

        return True

    # 
    # edit : 2023-9-29
    # desc : Remove the beginning of a very long filepath.
    def cut_long_filename(self, name, max=80):
        if(len(name) > max):
            start_index = len(name) - max
            short_name = '...' + name[start_index:]
            return short_name
        else:
            return name
        
    # update version string
    # edit : 2023-12-15
    def update_version(self, app_version, fw_version):
        self.str_app_version.set('PC App Version : ' + str(app_version))
        self.str_fw_version.set('Firmware Version : ' + fw_version)

    # check and vallidate ch1_nm entry value in TIME D tab
    # edit : 2024-3-20
    # todo : get correct max & min values from somewhere
    def new_wavelength(self, *args):
        max_nm = 890
        min_nm = 310

        for i in range(len(self.channel_list)):
            
            # channel list of gui items
            #if (int(self.channel_list[i].ch_str.get()) > max_nm):
            #    self.channel_list[i].ch_str.set(str(max_nm))
            #elif (int(self.channel_list[i].ch_str.get()) < min_nm):
            #    self.channel_list[i].ch_str.set(str(min_nm))
            #myCallback('gui_timed_add_wavelength', wavelength=self.channel_list[i].ch_str.get())
            
            # channel list of strings only
            if (int(self.channel_list[i].get()) > max_nm):
                self.channel_list[i].set(str(max_nm))
            elif (int(self.channel_list[i].get()) < min_nm):
                self.channel_list[i].set(str(min_nm))
            #self.callback('gui_timed_add_wavelength', wavelength=self.channel_list[i].get())

        return True
    
    # edit : 2024-3-28
    # desc : Eventhandler of 'ONCE' button, gets one reading of each selected channels.
    def button_read_chs_click(self):

        # TEST WAIT STATE
        #self.callback('gui_input_state')

        try:
            # read first channel
            #self.callback('gui_first_ch', wavelength=self.channel_list[0].ch_str.get())
            self.callback('gui_first_ch', wavelength=self.channel_list[0].get())
            # read other channels in the channel list
            for i in range(1, len(self.channel_list)):
                #print(self.channel_list[i].ch_str.get())
                #self.callback('gui_another_ch', index=i, wavelength=self.channel_list[i].ch_str.get())
                self.callback('gui_another_ch', index=i, wavelength=self.channel_list[i].get())
            self.callback('gui_draw_timed_graph')

        except Exception as e:
            print(' ERROR in handling "READ CHs" button click!')
            print(str(e))

    # edit : 2025-4-20
    # desc : Start continuous measurement. Stop continuous measurement if button is pressed. Adjust interval with hardware delay.
    #        Optimal hw_delay with firmware ver 1.0.4.1 was tested to be 860 ms.
    #        The final value of continuousInterval variable should be above zero.
    def continuous_button_click(self):

        # read & verify the value of the hardware delay
        try:
            hw_delay = int(fop.read_settings_file("device", "hw_delay"))
            if (hw_delay < 0 or hw_delay > 3000):
                default_hw_delay = int(mini_defaults.DEFAULT_SETTINGS["device"]["hw_delay"])
                fop.update_settings_file("device", "hw_delay", default_hw_delay)
                print(f" Incorrect hw_delay value! {default_hw_delay} (ms) will be used instead.")
        except:
            print(f" ERROR in reading hw_delay value from {fop.test_settings_file_name}")
            hw_delay = 860

        # start button pressed
        if(self.continuous_text.get() == 'START'):
            self.continuousInterval = int(float(self.str_interval.get()) * 1000 - hw_delay)
            if self.continuousInterval < 100:
                self.continuousInterval = 100
            self.continuousCount = 0
            self.continuousActivated = True
            self.root.after(self.continuousInterval, self.ContinuousTimeOut)
            self.continuous_text.set('STOP')

        # stop button pressed
        elif(self.continuous_text.get() == 'STOP'):
            self.continuousActivated = False
            self.continuous_text.set('START')

        else:
            print(' ERROR in activating continuous measurement.')

    # edit : 2024-3-16
    def ContinuousTimeOut(self):
        #print(' Time out ')
        if self.continuousActivated == True:
            self.button_read_chs_click()
            self.continuousCount = self.continuousCount + 1

            # all readings are done -> stop
            if self.continuousCount == int(self.str_max_cnt.get()):
                self.continuousActivated = False
                self.continuous_text.set('START')

        if self.continuousActivated == True:
            self.root.after(self.continuousInterval, self.ContinuousTimeOut)
        
    # edit : 2024-3-10
    def save_timed_button_click(self):
        time_stamp = datetime.now()
        default_filename = time_stamp.strftime("timed %Y-%m-%d %H.%M.%S.txt")
        save_name = filedialog.asksaveasfilename(initialfile=default_filename)
        self.callback('gui_save_timed', filename=save_name, comment='')

    # edit : 2024-1-26
    def reset_serie_button_click(self):
        try:
            self.callback('gui_one_reset')
        except Exception as e:
            print( ' ERROR in handling "RESET SERIE" button click!')

    # edit : 2024-3-28
    # desc : Eventhandler of 'CHECK' button on TEST page
    def button_test_input_click(self):
        state = self.callback('gui_input_state')
        self.str_test_input.set(state)

# edit : 2023-12-15
if __name__ == "__main__":

    def myCallback(callback_string):
        print("Callback received %s" %(callback_string))

    root = tkinter.Tk()
    gui = GUI(root, myCallback)
   
    # test function cut_long_filename
    gui.cut_long_filename("long string for testing", 10)

