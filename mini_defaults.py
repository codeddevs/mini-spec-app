# Copyright (c) 2025 Coded Devices Oy
#
# file : mini_defaults.py
# ver  : 2025-5-23
# desc : Default structure and values for the settings file. This file is not used actively,
#        but only when recreating or fixing the actual settings file.
#
# USB PORT
# In Linux, use command 'sudo dmesg|grep tty' to check the correct port name.
# Sometimes it's necessary to start the program using command 'sudo python3 mini_main.py'
# In Windows, use Device manager --> Ports (COM & LPT) to find correct COM number.

DEFAULT_SETTINGS = { 
    # Wavelength calibration coefficients
    "calibration" : {
        "a0" : 3.105747633e2,
        "b1" : 2.692683654,
        "b2" : -1.193440500e-3,
        "b3" : -6.935010901e-6,
        "b4" : 5.818299355e-9,
        "b5" : 1.043693591e-11
    },

    # Device specific data
    "device" : {
        "comport_name" : "COM3",            # Windows style
        #"comport_name" : "/dev/ttyUSB0"    # Linux style
        "hw_delay" : 660,                   # Hardware delay in sending one reading
        "hw_channel_count" : 288
    },

    # Measurement settings
    "measurement" : {
        "hw_source_intensity" : 5,         # LED intensity (1...31)
        "hw_integration_time" : 25         # Sensor integration time (ms)
    },

    # Special file names
    "files" : {
         "my_spectra_folder" : "./my_spectra/",         # default subfolder for saving spectra"
         "background_file_name" : "",
         "intensity_calib_file" : "",
         "zero_reference_file" : ""   # default name for the zero reference file
    }
}
