# Copyright (c) 2022 Coded Devices Oy

# Settings for Mini Spec App
# ver : 2022-8-19

# SPECIAL FILE NAMES
background_file_name = "background.txt"
intensity_calib_file = "int_calib.txt"      
zero_reference_file = "zero_reference.txt"  # default name for a zero reference file
my_spectra_folder = "./my_spectra/"         # default subfolder for saving and loading spectra
#my_spectra_folder = ".\\my_spectra\\"      # correct Win style path

# USB PORT
# in Linux use command 'dmesg|grep tty' to check the correct address and if 
# the device has been detected correctly
# sometimes it is necessary to start the program using command 'sudo python3 mini_main.py'
comport_name = "COM5" # Windows pc type port name 
#comport_name = "/dev/ttyUSB0" # Ubuntu pc type port name


# CALIBRATION COEFFS
calib_a0 = 3.105747633e2
calib_b1 = 2.692683654
calib_b2 = -1.193440500e-3
calib_b3 = -6.935010901e-6
calib_b4 = 5.818299355e-9
calib_b5 = 1.043693591e-11

# HARD WARE TIME UNIT
hw_time_to_ms = 1.6

# CHANNEL COUNT
hw_channel_count = 288

# DEFAULT SOURCE INTENSITY
hw_source_intensity = 5
