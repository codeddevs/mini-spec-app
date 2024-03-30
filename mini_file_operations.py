# Copyright (c) 2024 Coded Devices Oy

# file : mini_file_operations.py
# edit : 2024-3-10
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

# edit : 2024-3-10
# desc : timed data is 2d-array
def WriteTimedFile(timed_data, file_name, comment=''):
    columns = len(timed_data[0])
    rows = len(timed_data)

    # init & header
    new_file = open(file_name, 'w')
    new_file.write(str(comment) + '\n')
    new_file.write('[Time Domain Values]\n')
    for i in range(columns-1):
        temp_str = 'Ch%i' %(i+1)
        new_file.write(temp_str+'\t')
    new_file.write('Time\t\n')

    # data rows
    for i in range(rows):
        for j in range(columns):
            new_file.write(str(timed_data[i][j]) + '\t')
        new_file.write('\n')

    # end & close
    new_file.write('[end]\n')
    new_file.close()

    return 1


# unit test main
# edit : 2024-3-6
#
if __name__ == '__main__':
    
    # test writing timed data into a file
    myData = []
    myData.append([10.32, 12, 11, 8.945])
    myData.append([12, 11, 10, 11.229])
    myData.append([-1, 12, 0, 12.00])
    WriteTimedFile(myData, 'test.txt')


    



