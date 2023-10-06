# Copyright (c) 2023 Coded Devices Oy

# file : mini_file_operations.py
# edit : 2023-8-26
# desc : Reads and writes of the Mini Spec app

import os
import pickle

# func : read_file
# rev. : 29.5.2022
# desc : Read spectrum or calibration data from a txt file.
#        Spectrum data follows [spectrum] -header and ends by [End] -header
#        Test if intensity data is int (raw spectrum) or float (calibration).
#	 	 Originally from spectral_product.py ver. 19.8.2018
# todo : Create separate headers for calibration, background, reference and source files.
#        Identify the spectrum type by unit [bits] or [%] and draw the y-axis accordingly.
#
def read_file(fileName):
    header_found = False
    data = []
    unit = ''
    try:
        file = open(fileName, 'r')
    except FileNotFoundError:
        print(' Error: File not found!')
        return -1, unit
    except IsADirectoryError:
        print(' Error: File name missing!')
        return -1, unit

    print(' Reading file '+ fileName + ' ...')
    for line in file:
		
        if(line == '[spectrum]\n'):
            header_found = True
        
        # check what unit is used
        if('[%]' in line):
            print(" Absorption spectrum found...")
            unit = '%'
        elif('[bits]' in line):
            print(" Absolute spectrum found...")
            unit = 'bits'
		
        # parse data lines	
        elif(line != '[end]\n' and line != '[Source]\n' and header_found == True):
            point = line.split()
            if (point[0].isdigit() and point[1].isdigit() and point[2].isdigit()): 
                data.append([int(point[1]), int(point[2])])
            
            elif (point[0].isdigit() and point[1].isdigit() and point[2].isdigit() != True):
                data.append([int(point[1]), float(point[2])])

        elif(line == '[end]\n' and header_found == True):
            header_found = False
			
        elif(line == ''):
            break
	
    file.close()
    return data, unit

# func : save_zero_path
# edit : 2023-8-26
# desc : Use pickle module to save the previous zero reference file path into settings file
#        my_settings.txt.
def save_zero_path(zero_file):
     try:
          settings_file = open('my_settings.txt', 'wb')
          pickle.dump(zero_file, settings_file)
          settings_file.close()

     except FileNotFoundError:
          print("Error in writing to file my_settings.txt.")

# func : read_zero_path
# edit : 2023-8-26
# desc : Use pickle module to read the previous zero reference file path
def read_zero_path():
    try:
          settings_file = open('my_settings.txt', 'rb')
          zero_file = pickle.load(settings_file)
          settings_file.close()
          return zero_file
    
    except FileNotFoundError:
         print("Error in reading from file my_settings.txt")


# func : read_CIE_file
# rev. : 31.3.2019
# desc : Read CIE standard observer data from a txt file.
#        Data line has four elements : wavelength	x	y	z
#	 	 Originally from spectral_product.py ver. 19.8.2018
# todo : Create separate headers for calibration, background, reference and source files.
#
def read_CIE_file(fileName):
	data = []
	try:
		file = open(fileName, 'r')
	except FileNotFoundError:
		print('Error: File Not Found')
		return -1

	print('reading CIE file: '+ fileName)
	for line in file:
		point = line.split()
		if len(point) == 4:
			if (point[0].isdigit() and point[1].isdigit and point[2].isdigit and point[3].isdigit): 
				data.append([float(point[0]), float(point[1]), float(point[2]), float(point[3])])
		elif(line == ''):
			break
		
	file.close()
	return data

# func : read_tab_data_file
# ver  : 9.10.2020
# desc : Read a selected number of columns from a tab separeted data file.
#        Return 2-dim array 
#
def read_tab_data_file(fileName, column_count):
    data_out = []
    data_line_count = 0

    try:
        file = open(fileName, 'r')
        print(" Reading file: " + fileName)
    except:
        print(" Error: problems in reading this file!!")
        return -1
    
    for line in file:
        if line[0].isdigit():   # if first character of line is number
            point = line.split()
            if len(point) == column_count:
                if (point[0].isdigit()):                            # check only first
                    data_line_count = data_line_count + 1               
                    data_out.append([float(i) for i in point])      # convert all items to float
                elif (line == ''):
                    break
            else:
                print(' Error: incorrect number of columns found')
                break
                
    print(" Number of lines found: %i" %data_line_count)
    file.close()
    return data_out
    
	
# ver : 29.4.2022
# desc: Original write_file function used before need for float writing.
#
def write_int_file(data, file_name, comment):

	new_file = open(file_name, 'w')
	new_file.write(str(comment) + '\n')
	new_file.write('[spectrum]\n')
	new_file.write('[ch]\t[nm]\t[bits]\n')
	for i in range(0,len(data)):
		new_file.write('%i\t%i\t%i\n' %(i+1, data[i][0], data[i][1]))
	new_file.write('[end]\n')
	new_file.close()

# func : write_file
# ver : 20.5.2022
# Desc: Checks if the instensity data is float or int and writes accordingly.
#       Returns -1 if no data to write.
#       Returns 1 after writing data.
#
def write_file(data, file_name, comment, unit = '[bits]'):
    new_file = open(file_name, 'w')
    new_file.write(str(comment) + '\n')
    new_file.write('[spectrum]\n')
    #new_file.write('[ch]\t[nm]\t[bits]\n')
    new_file.write('[ch]\t[nm]\t' + unit +'\n')

    #check if there is any data to save
    if len(data) == 0:
        print(" Error: No data to save!")
        return -1
    
    #check if intensity value is integer or float
    if isinstance(data[0][1], float):
        for i in range(0,len(data)):
            new_file.write('%i\t%i\t%.4f\n' %(i+1, data[i][0], data[i][1])) # 1st column is ch nr, not index!
    elif isinstance(data[0][1], int):
        for i in range(0, len(data)):
            new_file.write('%i\t%i\t%i\n' %(i+1, data[i][0], data[i][1]))

    new_file.write('[end]\n')
    new_file.close()
    return 1

# func : create_spectra_folder
# ver : 29.4.2022
# desc : Check if the default subfolder for spectra exists.
#        Create it if missing.
def create_spectra_folder(folder_name):
    if os.path.exists(folder_name):
        # name exist but is not a folder (maybe a file)
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
            print(" Folder " + folder_name + " created.") 
    else:
        os.mkdir(folder_name)
        print(" Folder " + folder_name + " created.")


# unit test main
# ver 9.10.2020
#
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    data = []
    data = read_tab_data_file("CIE_illuminannts.txt", 7)
    #data=read_CIE_file('CIE_ill_test.txt')	
    x_data = [x[1] for x in data]
    y_data = [x[2] for x in data]
    z_data = [x[3] for x in data]
    wavelength_data = [x[0] for x in data]
    plt.plot(wavelength_data, x_data)
    plt.plot(wavelength_data, y_data)
    plt.plot(wavelength_data, z_data)
    plt.show()
