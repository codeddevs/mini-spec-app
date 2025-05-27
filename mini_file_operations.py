# Copyright (c) 2025 Coded Devices Oy

# file : mini_file_operations.py
# edit : 2025-05-27
# desc : Reads and writes of the Mini Spec app
# TODO : After reading the reference file name from the saved settings,
#        then test that this filepath still points to a usable data.

import os
import mini_defaults
import configparser

# settings ini file
settigs_file_name = "mini_settings.ini"

# edit : 2025-5-23
# desc : Returns True if path exists.
def Check_File_Path(file_path):
    return os.path.exists(file_path)

# edit : 2025-4-19
# desc : Check if all content of the settings file exist. Defaults used if missing.
def test_settings(config):
    for section_name, options in mini_defaults.DEFAULT_SETTINGS.items():
        if not config.has_section(section_name):
            config.add_section(section_name)
        for option_name, value in options.items():
            if not config.has_option(section_name, option_name) or not config.get(section_name, option_name):
                config.set(section_name, option_name, str(value))

# Edit : 2025-4-19
# Desc : Reading settings from a structured .ini file.
# Note! Config.read will return the file name (actually list) that was succesfully read. 
#       If file reading fails an empty list is returned.
#       Check read settings values later in try... except way and prepare for parsing errors 
#       --> Raises: MissingSectionHeaderError if the INI file is malformed.
def load_settings(config, file_name):
    read_file = config.read(file_name)
    if not read_file:
        raise FileNotFoundError(f" File {file_name} may not exist or is invalid.")
    return config

# Edit : 2025-3-21
# Note! If the file is missing but directory is correct a new file is created.
def save_settings(config, file_name):
    try:
        with open(file_name, "w") as configfile:
            config.write(configfile)
    except Exception as e:
        print(f" ERROR in saving settings. {e}")
        

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

# desc : Writea a new value in the settings file.
# edit : 2025-05-08
def update_settings_file(section, key, value):
    temp_config = configparser.ConfigParser(inline_comment_prefixes = "#")
    try:
        temp_config = load_settings(temp_config, settigs_file_name)

        if section not in temp_config:
            print(f" ERROR: section [{section}] not found!")
            return None
        
        if value is None or str(value) == "None":
            print(f" ERROR: trying to save {key} value as None")
            return None

        temp_config[section][key] = str(value)
        save_settings(temp_config, settigs_file_name)
        return temp_config[section][key]
    
    except FileNotFoundError:
        print(f" ERROR: settigs file {settigs_file_name} not found!")
        return None
    
    except configparser.MissingSectionHeaderError:
        print(f" ERROR: section [{section}] was not found!")
        return None
    
    except Exception as e:
        print(f" ERROR: unexpected problem in writing to settings file. {e}")
        return None

# desc : Read a key value from the settings file.
# edit : 2025-05-08
def read_settings_file(section, key):
    temp_config = configparser.ConfigParser(inline_comment_prefixes = "#")
    try:
        temp_config = load_settings(temp_config, settigs_file_name)

        if section not in temp_config:
            print(f" ERROR: section [{section}] not found!")
            return None
        
        if key not in temp_config[section]:
            print(f" ERROR: key '{key}' not found in section [{section}]!")
            return None

        return temp_config[section][key]
    
    except FileNotFoundError:
         print(f" ERROR: settigs file {settigs_file_name} not found!")
         return None
    
    except configparser.MissingSectionHeaderError:
         print(f" ERROR: section {[section]} was not found!")
         return None
    
    except Exception as e:
        print(f" ERROR: unexpected problem in reading the settings file. {e}")
        return None

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
# edit : 2025-05-08
#
if __name__ == '__main__':
    
    t_section = "measurement"
    t_key = "hw_source_intensity"
    
    # test reading a value from the settings file
    t_value = read_settings_file(t_section, t_key)
    print(f" Test : Found {t_key} = {t_value}")

    # test adding a new value to settings file
    ret_val = update_settings_file(t_section, t_key, str(t_value))
    if ret_val:
         print(f" Test : Updated successfully: {t_key} = {t_value}")
    else:
         print(f" Test : Error in updating {t_key} = {t_value}") 

