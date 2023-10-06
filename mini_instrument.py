# Copyright (c) 2023 Coded Devices Oy

# file name : mini_instrument.py
# ver : 2023-8-25
# desc: Defines instrument class which controls Mini Spectrometer hardware via 
#       serial communication.

# Firmware command set (edited 2022-5-6):
# 'S' read a single pre set channel
# 'A' read all channels
# 'L' flash LED pre set number of times
# 'I' set one step higher integration time (after max value returns to min value).
# 'R' reset instrument
# 'V' read instrument firmware version
# 'H' set intensity value of the source
# '0'...'9' four numbers are captured to be later used with commands 'L', 'H', 'S'

import serial
import random
import time
import mini_settings

class mini_instrument:

    myPort = serial.Serial()
 

    # constructor
    # ver : 12.3.2020
    #
    def __init__ (self):
         
        self.myPort.baudRate = 9600
        self.myPort.bytesize = 8
        self.myPort.parity = 'N'
        self.myPort.stopbits = 1
        self.myPort.timeout = None
        self.myPort.xonxoff = 0
        self.myPort.rtscts = 0
        self.myPort.timeout = 1             # 1 sec timeout in reading lines
        self.myPort.port = mini_settings.comport_name 
        self.spectrum_data = []

    def openPort(self):
        port_opened = False
        try:
            self.myPort.open()
            port_opened = True
        except serial.SerialException:
            print("Error in connecting to the device!")
        return port_opened

    # method : writeC
    # ver : 1.4.2022
    # desc : Writes a char to COM port. No check if port is open --> do not call directly
    #        outside of this class.
    def writeC(self, c):
        try:
            self.myPort.write(c)
        except serial.SerialException as serr:
            print(str(serr))
    
    # method : getFirmwareVer
    # ver : 8.4.2022
    # desc : Print to therminal the version number of the instrument firmware. 
    def printFirmwareVersion(self):

        try:
            self.myPort.flush()
            self.myPort.write(b'V')
            
            time.sleep(0.1)
            line_1 = self.myPort.readline().strip().decode("ascii") # catch extra line change ??  
            #print(line_1)

            time.sleep(0.1)
            line_2 = self.myPort.readline().strip().decode("ascii") # read the returned command 'V'
            
            print(" Firmware version ", end = "")
            time.sleep(0.1)
            line_3 = self.myPort.readline().strip().decode("ascii") # read the version data
            for i in range(len(line_3)-1):
                print(line_3[i] + ".", end = "")
            print(line_3[len(line_3)-1])
                
        except serial.SerialException as serr:
            print(str(serr))
        except ValueError as verr:
            print(str(verr))
        except Exception as e:
            print(str(e))
        
    # method : getrandomValue
    # ver : 2.1.2019
    # desc : Return a random value like a real 10-bit reading from mini-spectrometer
    #
    def getRandomValue(self):
        return random.randint(230, 1023)

    # method : getSpectrum
    # ver    : 2023-8-25
    # desc   : Request and read full spectrum.
    #          First test if port is open (return 1 or 0)          
    #          Store values into mini_data.data[channel nr][value]
    #          Notice indexing : channel nr 1 --> data[0]
    # 
    def getSpectrum(self, output_data):

        if (self.myPort.is_open == True):   # isOpen() of pySerial will be depricated
               
            del output_data[:]              # clear old data
            self.myPort.write(b'A')         # request for spectrum
            time.sleep(0.1)                 # sleep for 0.1 sec
            channel_count = 0;              # 4.6.2021       

            #first input line repeats the command 'R'
            line = self.myPort.readline().strip().decode("ascii")
                    
            #second input line tells number of channels, example b'0288'
            try:
                line = self.myPort.readline().strip()   # remove '\n'
                channel_count = int(line)               # 290 expected
                print('channel count: %i' %channel_count)       
            except ValueError as verr:
                print(str(verr))
        
            #first reading is from outside of real spectrum, not saved
            try:
                line = self.myPort.readline().strip().decode("ascii")    # read a '\n' terminated line, remove '\n' and convert from bytes to ASCII str
                #print('outside of spectrum:')
                #print(line)
            except ValueError as verr:
                print(str(verr))

            ch_index = 1
            channel_count = channel_count - 1 # 289 expected

            #read & store true readings
            print('receiving spectrum...')
            while(ch_index < channel_count):
                try:
                    line = self.myPort.readline().strip().decode("ascii")    # read a '\n' terminated line, remove '\n' and convert from bytes to ASCII str
                    #print(line)
                    values = line.split()
                    output_data.append([int(values[0]), int(values[1])])
                    ch_index = ch_index + 1
                except ValueError as verr:
                    print(str(verr))

            # check if all calues were received
            if ch_index == channel_count:
                print("Ready!")
            else:
                print("Something went wrong and not all values were received!")

            #last reading outside of spectrum, not saved
            try:
                #print('outside of spectrum:')
                line = self.myPort.readline().strip().decode("ascii")
                #print(line)
            except ValueError as verr:
                print(str(verr))

            #clear port input
            time.sleep(0.2)
            try:
                self.myPort.reset_input_buffer()
                if(self.myPort.in_waiting != 0):
                    print('WARNING : bytes waiting in input buffer.')
            except serial.SerialException as serr:
                print(str(serr))

            return 1
        
        # is_open == False
        else:       
            print(" ERROR: No connection to the instrument!")
            return 0

        # method : getOneChannel
        # ver    : 2023-5-5
        # desc   : Get reading of one pre selected channel. 
        #          Sends the channel number (1...288) to instrument just before requesting the reading.
        def getOneChannel(self, ch_number):
            
            try:
                for x in str(ch_number):
                    self.myPort.write(x.encode())   # encodes text to bytes using UTF-8 (partly compatible with ASCII)
                    time.sleep(0.1)                 # importance of correct intendation ;)    
            except Exception as x:
                print(x)
                    
            self.myPort.write(b'S')         # request for spectrum
            time.sleep(0.1)                 # sleep for 0.1 sec

            # first input line echoes the command 'S'
            try:
                line = self.myPort.readline().strip().decode("ascii")
                print(line)
            except ValueError as verr:
                print(str(verr))

            # second input line tells the number of the selected channel and its value
            try:
                line = self.myPort.readline().strip() # remove '\n'
                [channel, value] = line.split()
                print('channel number: %i' %int(channel))
                print('channel value : %i' %int(value))       
            except ValueError as verr:
                print(str(verr))
        

    # method : setSourceIntensity
    # ver    : 22.4.2022
    # desc   : Change intensity of the LED source. First send new intensity value 0...31.
    #          Then send the command 'H' to use the sent value as the new intensity setting.
    def setSourceIntensity(self, intensity):

        intensity = int(intensity)

        if intensity > 31:
            intensity = 31
            print(" Intensity changed to " + str(intensity))
        elif intensity < 0:     
            intensity = 0
            print(" Intensity changed to " + str(intensity))

        try:
            for x in str(intensity):
                self.myPort.write(x.encode()) # encodes text to bytes using UTF-8 (partly compatible with ASCII)
                time.sleep(0.1)                 
            self.myPort.readline() # read the returned command 'x' 
            self.myPort.write(b'H')
            time.sleep(0.1)
            self.myPort.readline() # read the returned command 'H'
        except serial.SerialException:
            print("Error in using serial port!")
            

    # method : setIntegrationTime
    # ver    : 12.3.2020
    # desc   : Write char I to com port to increase integration time one step i.e 10 units.
    #          Read return value of the new integration time.
    #
    def setIntegrationTime(self):
        self.myPort.write(b'I')
        time.sleep(0.1)
        line = self.myPort.readline() # read the returned command 'I'
        time.sleep(0.1)
        line = self.myPort.readline().strip().decode("ascii") # read new time value
        try:
            newTime = int(line)
        except ValueError as verr:
            print(str(verr))
        return newTime * mini_settings.hw_time_to_ms # time in ms


    # method : blink_LED
    # ver : 5.1.2021
    #
    def blink(self,times):
        try:
            for x in str(times):
                self.myPort.write(x.encode()) # encodes text to bytes using UTF-8 (partly compatible with ASCII)
                time.sleep(0.1)                 
            self.myPort.readline() # read the returned command 'x' 
            self.myPort.write(b'L')
            time.sleep(0.1)
            self.myPort.readline() # read the returned command 'L'
                         
        except serial.SerialException:
            print("Error in opening serial port!")
        except Exception as x:
            print(x)

    # method : clearInputBuffer
    # edit : 2023-5-5
    # desc : Read imput buffer untill it is empty, discard all data.
    def clearInputBuffer(self):
        try:
            time.sleep(0.5)
            self.myPort.flushInput()
            time.sleep(0.5)
            self.myPort.read_all()
        except serial.SerialException as serr:
            print(str(serr))
    





        

