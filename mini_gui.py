# Copyright (c) 2024 Coded Devices Oy

# Mini Spec App GUI
# edit 2024-1-11
# todo : continue TIME D

import tkinter
from tkinter import ttk
from tkinter import filedialog
from tkinter import * 
from tkinter import messagebox
import time
from datetime import datetime


import mini_settings
import mini_file_operations as fop

class GUI:

    
    def __init__(self, root, callback):

        self.callback = callback
        self.root = root
        self.root.title("Mini Spec App by Coded Devices")
        self.default_file_location = "c:"   # mini_settings.my_spectra_folder
        self.app_version = ""               # MainApp constructor sets version during start up
        
        # NOTEBOOK & STYLE definition
        self.notebook = ttk.Notebook(self.root)
        self.notebook.configure(padding=(5, 5))
        self.my_style = ttk.Style()
        self.my_style.theme_use('winnative') # 'winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative'
                                
        # TAB 'MEAS' for brinning measurements **********************************************
        # edit : 2023-9-15
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

        # TAB 'ABSORPTION' ********************************************************************
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

        # cut long file paths --> more readable
        try:
            file_path = fop.read_zero_path()
            file_path = self.cut_long_filename(file_path)
        except TypeError:
            file_path = ''
            print(' Error: Reference filepath is not correct!')
        self.ref_file_name_var.set(file_path)
        

        button_change_file = ttk.Button(page_abs, text='Change', command= self.button_browse_file_click)
        button_change_file.grid(column=3, row=2, padx=5, pady=7)

        button_calc_abs = ttk.Button(page_abs, text="CALC ABS", command=self.button_calc_abs_click)
        button_calc_abs.grid(column=1, row=5, padx=5, pady=7)

        button_save_abs = ttk.Button(page_abs, text='SAVE ABS', command=self.button_save_abs_click)
        button_save_abs.grid(row=6, column=1, padx=5, pady=7, sticky=W)

        button_clear_abs = ttk.Button(page_abs, text="CLEAR ABS", command=self.button_clear_abs_click)
        button_clear_abs.grid(column=1, row=7, padx=5, pady=7)

        # TAB 'AVERAGE' *************************************************************************
        page_ave = ttk.Frame(self.notebook)
        
        self.str_ave_count = tkinter.StringVar(page_ave, '')
        self.str_ave_count.set('AVE SIZE : ')
        label_ave_count = ttk.Label(page_ave, textvariable=self.str_ave_count)
        label_ave_count.grid(row=1, column=2, padx=5, pady=7, sticky=W)

        button_add_to_ave = ttk.Button(page_ave, text='ADD', command=self.button_add_to_ave_click)
        button_add_to_ave.grid(row=1, column=1, padx=5, pady=7, sticky=W)

        button_save_ave = ttk.Button(page_ave, text='SAVE AVE', command=self.button_save_ave_click)
        button_save_ave.grid(row=2, column=1, padx=5, pady=7, sticky=W)

        button_clear_ave = ttk.Button(page_ave, text='CLEAR AVE', command=self.button_clear_ave_click)
        button_clear_ave.grid(row=3, column=1, padx=5, pady=7)

        self.str_ave_count.set('AVE SIZE : ' + str(self.callback('ask_ave_count')))

        self.notebook.add(page_ave, text = ' AVERAGE ', padding='5')

        # __init__ TAB 'TIME D' *****************************************************************
        # edit : 2023-1-12
        page_timed = ttk.Frame(self.notebook)
        self.notebook.add(page_timed, text=' TIME D', padding='5')
        self.str_ch1_nm = tkinter.StringVar(page_timed, '550')
        
        self.label_ch1_nm = ttk.Label(page_timed, text='Channel #1 waveleght (nm) : ')
        self.label_ch1_nm.grid(row=1, column=1, padx=5, pady=7, sticky=W)

        self.entry_ch1_nm = ttk.Entry(page_timed, width=3, textvariable=self.str_ch1_nm, validate='focusout', validatecommand=self.new_ch1_wavelength)
        self.entry_ch1_nm.grid(row=1, column=2, padx=5, pady=7, sticky=W)

        self.button_read_one = ttk.Button(page_timed, text='READ ONE', command=self.button_read_one_click)
        self.button_read_one.grid(row=1, column=3, padx=5, pady=7, sticky=W)


        # __init__ TAB 'SETTINGS' ************************************************************************
        page_set = ttk.Frame(self.notebook)
        self.notebook.add(page_set, text=' SETTINGS ', padding='5')

        self.str_app_version = tkinter.StringVar(page_set, 'PC App Version: ?')
        
        self.str_fw_version = tkinter.StringVar(page_set, 'Firmware Version: ?')
        
        self.str_port = tkinter.StringVar(page_set, 'COM port name: ' + mini_settings.comport_name)
        label_port = ttk.Label(page_set, textvariable=self.str_port)
        label_port.grid(row=3, column=1, padx=5, pady=7, sticky=W)
        
        label_app_version = ttk.Label(page_set, textvariable=self.str_app_version)
        label_app_version.grid(row=1, column=1, padx=5, pady=7, sticky=W)

        label_fw_version = ttk.Label(page_set, textvariable=self.str_fw_version)
        label_fw_version.grid(row=2, column=1, padx=5, pady=7, sticky=W)

        # LED intensity control
        labelfr_set_intensity = ttk.Labelframe(page_set, text=' LED intensity (0...31)')
        labelfr_set_intensity.grid(column=1, row=4, padx=5, pady=7, sticky=E)
        self.str_source_int = tkinter.StringVar(page_set, '')
        self.spin_intensity = ttk.Spinbox(labelfr_set_intensity, from_= 0, to=31, width=2, validate='focusout', validatecommand=self.spin_intensity_change, textvariable=self.str_source_int)    
        if (mini_settings.hw_source_intensity >= 0 and mini_settings.hw_source_intensity <= 31):    # set correct default to begin with
           #self.spin_intensity.set(mini_settings.hw_source_intensity)
           self.str_source_int.set(mini_settings.hw_source_intensity)
        else:
            self.spin_intensity.set(5)
        self.spin_intensity.grid(column=2, row=1, padx=10, pady=7)
        self.button_set_intensity = ttk.Button(labelfr_set_intensity, text=' SET ', command=self.button_set_intensity_click)
        self.button_set_intensity.grid(column=3, row=1, padx=5, pady=7)

        # __init__ INTEGRATION TIME control *************************
        # edit 2023-12-31
        min_itime = 10   # shortest possible integration time in ms
        max_itime = 500  # longest possible

        labelfr_set_integration = ttk.Labelframe(page_set, text=' Integration time (ms)')
        labelfr_set_integration.grid(row=4, column=2, padx=5, pady=7, sticky=E)
        
        self.str_itime = tkinter.StringVar(labelfr_set_integration, '')
        self.spin_itime =ttk.Spinbox(labelfr_set_integration, from_=min_itime, to=max_itime, width=3, validate='focusout', validatecommand=self.spin_itime_change, textvariable=self.str_itime)
        if(mini_settings.hw_integration_time >= min_itime and mini_settings.hw_integration_time <= max_itime): # check that default is correct
            self.str_itime.set(mini_settings.hw_integration_time)
        else:
            self.str_itime.set('20')
        
        self.button_set_itime = ttk.Button(labelfr_set_integration, text=' SET ', command=self.button_set_itime_click)
        self.button_set_itime.grid(row=1, column=2, padx=5, pady=7)
        
        self.spin_itime.grid(row=1, column=1, padx=5, pady=7, sticky=E)

        # Notebook in the root window
        #self.notebook.pack(expand=1, fill='both')
        self.notebook.grid(column=0, row=0, sticky=(N, W, S, E))   
    # END OF __init__ ***

    # # button_OK event handler
    # def button_OK_click(self):
    #     self.callback(self.input_var.get())
    #     self.input_var.set("")

    # button_new event handler 
    def button_new_click(self):
        self.callback('r')
        self.responder(self.button_new_new)
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

    def button_set_intensity_click(self):
        #messagebox.showinfo('Intensity change', 'SET ' + self.str_source_int.get())
        self.callback('gui_int', led_intensity = int(self.str_source_int.get()))

    # event handler for set button of integration time
    # edit : 2023-12-29
    def button_set_itime_click(self):
        self.callback('gui_itime', time = int(self.str_itime.get()))

    # button_load event handler
    # edit: 2023-9-22
    # desc: Windows tracks well previous file paths used.
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
    # edit : 2023-8-26
    def button_browse_file_click(self):
        zero_file = filedialog.askopenfilename(title = "Select file", filetypes = (("txt files", "*.txt"),("all files", "*.*")))
        
        if len(zero_file) > 0:
            self.ref_file_name_var.set('')
            fop.save_zero_path(zero_file)
            self.ref_file_name_var.set(self.cut_long_filename(zero_file))

    # button_calc_abs_click event handler
    def button_calc_abs_click(self):
        ref_file = fop.read_zero_path()
        self.callback('cab', filename = ref_file)

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

        #self.spin_intensity.set(temp_value)
        #self.str_source_int.set(str(temp_value))
        #self.root.after(50, lambda : messagebox.showinfo('spinbox', str(temp_value)))
        #messagebox.showinfo('spinbox', str(self.spin_intensity.get()))
        return True

    # responder
    def responder(self, button):
        time.sleep(2)

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
    # edit : 2024-1-12
    # todo : get max & min values somewhere
    def new_ch1_wavelength(self, *args):
        max_nm = 890
        min_nm = 310
        if (int(self.str_ch1_nm.get()) > max_nm):
            self.str_ch1_nm.set(str(max_nm))
        elif (int(self.str_ch1_nm.get()) < min_nm):
            self.str_ch1_nm.set(str(min_nm))
        return True
    
    # edit 2024-1-11
    # desc : Eventhandler of 'READ ONE' button, gets one reading of ch1 wavelength
    def button_read_one_click(self):
        self.callback('gui_one', wavelength=self.str_ch1_nm.get())


# edit 2023-12-15
if __name__ == "__main__":

    def myCallback(callback_string):
        print("Callback received %s" %(callback_string))

    root = tkinter.Tk()
    gui = GUI(root, myCallback)
   
    # test function cut_long_filename
    gui.cut_long_filename("long string for testing", 10)