# Copyright (c) 2025 Coded Devices Oy

# file name : mini_instrument.py
# ver : 2025-2-14
# target firmware ver : 1.5.0.1 or later
# desc: Defines instrument class which controls Mini Spectrometer hardware via 
#       serial communication.

# Firmware command set (edited 2022-5-6):
# 'S' read a spectrum and send a single pre selected channel
# 'G' send a single pre selected channel from already measured spectrum
# 'A' read a spectrum and send all channels
# 'L' flash LED pre set number of times
# 'I' set one step higher integration time (after max value returns to min value).
# 'R' reset instrument
# 'V' read instrument firmware version
# 'H' set intensity value of the source
# 'W' activate wait state
# '0'...'9' four numbers are captured to be later used with commands 'L', 'H', 'S'

import serial
import random
import time
import mini_settings

class mini_instrument:

    myPort = serial.Serial()
 

    # Constructor
    # ver : 2025-2-14
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
        self.fw_version = None  # firmware version, 
                                # will be read back from the instrument during the startup

    def openPort(self):
        port_opened = False
        try:
            self.myPort.open()
            port_opened = True
        except serial.SerialException:
            print(" Error in connecting to the device!")
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
    # desc : Print to terminal the version number of the instrument firmware.
    #        Not called by GUI but only command line main. 
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
            print(' Error in receiving the firmware version!')
            print(str(verr))
        except Exception as e:
            print(' Error in receiving the firmware version!')
            print(str(e))
    
    # return str instead of printing
    # edit : 2025-2-14
    # desc : Return the current hardware firmware version. If version is 'None' it has not been
    #        read-back from the instrument after starting the program. Then read it first. 
    def getFirmwareVersion(self):

        # if the firmware version has not yet been read back the device
        if (self.fw_version == None):

            try:
                self.myPort.flush()
                self.myPort.write(b'V')
                
                time.sleep(0.1)
                line_1 = self.myPort.readline().strip().decode("ascii") # catch extra line change ??  
                
                time.sleep(0.1)
                line_2 = self.myPort.readline().strip().decode("ascii") # read the returned command 'V'
                        
                time.sleep(0.1)
                line_3 = self.myPort.readline().strip().decode("ascii") # read the version data

                str_fw_version = ''
                for i in range(len(line_3)-1):
                    str_fw_version = str_fw_version + str(line_3[i] + ".")
                str_fw_version = str_fw_version + str(line_3[len(line_3)-1])

                self.fw_version = str_fw_version
                    
            except serial.SerialException as serr:
                print(str(serr))
            except ValueError as verr:
                print(str(verr))
                print(" Consider adding reset call into getFirmwareVersion method!")
            except Exception as e:
                print(str(e))
            
        return self.fw_version
        
    # method : getrandomValue
    # ver : 2.1.2019
    # desc : Return a random value like a real 10-bit reading from mini-spectrometer
    #
    def getRandomValue(self):
        return random.randint(230, 1023)

    # method : getSpectrum
    # ver    : 2025-2-14
    # desc   : Request and read a full spectrum.
    #          First test if port is open (return 1 or 0)          
    #          Store values into mini_data.data[channel nr][value]
    #          Notice indexing : channel nr 1 --> data[0][channel_nr = 1, intensity]
    #                            channel nr 288 --> data[287][channel_nr = 288, intensity]
    # 
    def getSpectrum(self, output_data):

        if (self.myPort.is_open == True):   # isOpen() of pySerial will be depricated
               
            del output_data[:]              # clear old data
            self.myPort.write(b'A')         # request for spectrum
            time.sleep(0.1)                 # sleep for 0.1 sec
            channel_count = 0;                  

            # first input line repeats the command 'A'
            line = self.myPort.readline().strip().decode("ascii")
                               
            # second input line tells the number of channels the uc is going to send, example b'0288'
            try:
                line = self.myPort.readline().strip()   # remove '\n'
                channel_count = int(line)               
                print(' Channel count: %i' %channel_count)       
            except ValueError as verr:
                print(str(verr))

            # firmware is 1.0.5.1 or later, returns 288 samples
            if (self.isLater(self.fw_version, '1.0.5.0')):

                # read & store channel number (values[0]) and intensity (values[1])
                print(' Receiving spectrum...', end='', flush=True)
                ch_index = 0
                while(ch_index < channel_count):
                    try:
                        line = self.myPort.readline().strip().decode("ascii")    # read a '\n' terminated line, remove '\n' and convert from bytes to ASCII str
                        values = line.split()
                        output_data.append([int(values[0]), int(values[1])])
                        #print(f'received {[int(values[0]), int(values[1])]}')
                        ch_index = ch_index + 1
                    except ValueError as verr:
                        print(str(verr))

            # firmware version 1.0.5.0 or earlier returns 290 samples and use different indexing
            else:
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
                print(' Receiving spectrum...', end='', flush=True)
                while(ch_index < channel_count):
                    try:
                        line = self.myPort.readline().strip().decode("ascii")    # read a '\n' terminated line, remove '\n' and convert from bytes to ASCII str
                        #print(line)
                        values = line.split()
                        output_data.append([int(values[0]), int(values[1])])
                        ch_index = ch_index + 1
                    except ValueError as verr:
                        print(str(verr))
                                        
            # check if all values were received
            if ch_index == channel_count:
                print(" Ready!")
            else:
                print(" Something went wrong and not all values were received!")

            # clear input buffer
            time.sleep(0.2)
            try:
                self.myPort.reset_input_buffer()
                if(self.myPort.in_waiting != 0):
                    print(' WARNING : bytes waiting in input buffer.')
            except serial.SerialException as serr:
                print(str(serr))

            return 1
        
        # is_open == False
        else:       
            print(" ERROR: No connection to the instrument!")
            return 0

    # method : GetFirstChannel
    # ver    : 2025-2-8
    # desc   : Get reading of one pre selected channel. 
    #          Sends the channel number (1...288) to instrument just before requesting the reading.
    #          Short sleep values are essential to reliability of the operation.    
    def GetFirstChannel(self, ch_number):

        delay = 0.05

        if (self.myPort.is_open == False):
            print(' ERROR : no connection to hardware, port is not open!')
            print(' ERROR in sending "S" command to the uc!')
            return(ch_number, -1)
            
        try:
            for x in str(ch_number):
                self.myPort.write(x.encode())   # encodes text to bytes using UTF-8 (partly compatible with ASCII)
                time.sleep(delay)               # importance of correct intendation ;)
            self.myPort.write(b'S')             # request for spectrum
            time.sleep(delay)                   # sleep for 0.1 sec
            line = self.myPort.readline().strip().decode("ascii")   # read the echo 'S'
            #time.sleep(delay)
            #print('command echo: ' + line)
        except Exception as x:
            print(' ERROR in sending "S" command to the uc!')
                
        try:
            line = self.myPort.readline().strip() # read the ch nr (1...288) and its value, remove '\n'
            [channel, value] = line.split()
            return(channel, value)       
        except Exception as e:
            print(' ERROR in receiving the Channel Number and its Value after command "S"!')
            return(-1, -1)
                   
    # method : GetAnotherChannel
    # edit   : 2025-2-8
    # desc   : Get value of a predefined channel from already measured spectrum still in the memory of the
    #          micro controller (usually a reference channel value of the same measurement as one 
    #          received by calling getOneChannel method).
    #          Some sleep between the writes is a must.    
    def GetAnotherChannel(self, ch_number):

        delay = 0.05
        
        # send the number of a channel & command 'G'         
        try:
            for x in str(ch_number):
                self.myPort.write(x.encode())   # encodes text to bytes using UTF-8 (partly compatible with ASCII)
                time.sleep(delay)               # importance of correct intendation ;)
            self.myPort.write(b'G')             # request another channel from the already measured spectrum
            time.sleep(delay)
            line = self.myPort.readline().strip().decode("ascii")   # read the echo 'G'
        except Exception as e:
            print(' ERROR in sending "G" command to the uc!')
            
        # read the response for the command 'G'
        try:
            line = self.myPort.readline().strip() # read the ch nr (1...288) and its value, remove '\n'
            [channel, value] = line.split()
            return(channel, value)
        except Exception as e:
            print(f' Error in receiving channel value!')
            return(channel, -1)

    # method : setSourceIntensity
    # ver    : 2025-2-14
    # desc   : Change intensity of the LED source. First send new intensity value 0...31.
    #          Then send the command 'H' to use the sent value as the new intensity setting.
    #          Finally read the new value sent back by the device.
    # todo   : Use different return values for errors and for not having a read-back value.
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
            time.sleep(0.1)

            # firmware version 1.0.5.0 and older ones do not return the new intensity value 
            if (self.isLater(self.fw_version, '1.0.5.0')):
                try:
                    line = self.myPort.readline().strip().decode("ascii") # read new intensity value
                    return int(line)
                
                except ValueError as verr:
                    print(' Error in returning intensity value!')
                    return -1
            # fw version is 1.0.5.0 or earlier
            else:
                return -1
            
        except serial.SerialException:
            print(" Error in using serial port!")
            return -1
   
    # edit : 2023-12-30
    # desc : give time in ms units using int type
    #        when ready and tested replace current setIntegrationTime method
    #        Works with firmware version 1.0.1.0 or later
    def setIntegrationTime(self, itime):
        try:
            for x in str(itime):
                self.myPort.write(x.encode()) # encodes text to bytes using UTF-8 (partly compatible with ASCII)
                time.sleep(0.1)                 
            self.myPort.readline() # read the returned command 'x' 
            self.myPort.write(b'I')
            time.sleep(0.1)
            line = self.myPort.readline() # read the returned command 'I'
            time.sleep(0.1)
            line = self.myPort.readline().strip().decode("ascii") # read new time
            try:
                itime = int(line)
                return itime
            except ValueError as verr:
                print(str(verr))
                return -1

        except serial.SerialException:
            print(" Error in using serial port!")
            return -1
            

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
            print(" Error in opening serial port!")
        except Exception as x:
            print(x)

    # edit : 2024-3-28
    # desc : Ask the current state of the external input pin (RA2).
    def AskInputState(self):
        try:
            self.myPort.write(b'W')
            time.sleep(0.1)
            line = self.myPort.readline().strip().decode("ascii")   # read the echo 'W' and the state
            #print(line)
            return line
        except Exception as e:
            print(e)
            return -1
            

    # method : clearInputBuffer
    # edit : 2023-5-5
    # desc : Read input buffer untill it is empty, discard all data.
    def clearInputBuffer(self):
        try:
            time.sleep(0.5)
            self.myPort.flushInput()
            time.sleep(0.5)
            self.myPort.read_all()
        except serial.SerialException as serr:
            print(str(serr))

    # edit : 2025-2-14
    # desc : Tells if one version number given as string 'a.b.c.d' is later that other.
    #        First convert strings to integer tuples for comparison.
    def isLater(self, this_ver, ref_ver):
        try:
            t_ver = tuple(map(int, this_ver.split('.')))
            r_ver = tuple(map(int, ref_ver.split('.')))
            return t_ver > r_ver
        except ValueError:
            print(f' Error in version number comparison!')
            return False

            
    





        

