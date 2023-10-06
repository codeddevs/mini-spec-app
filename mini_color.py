# file : mini_color.py
# rev : 9.10.2020
# desc : Functions for color coodinate calculation.
#	 Use for example colorizer.org website to compare results
#
import mini_file_operations as fop
import mini_settings as settings 

LAMBDA_STEP = 5
LAMBDA_MIN = 380
LAMBDA_MAX = 785 # add one step beyond 


# func : calc_XYZ_coords
# ver : 9.10.2020
# desc : Calculate tristimulus values X,Y and Z.
#        Use equation group (4) of ASTM E308-01.
#        Select light source by CIE_ill_source_index.
#
def calc_XYZ_coords(mySpectrum):
    CIE_obs_data = fop.read_CIE_file(settings.CIE_observer_file)
    CIE_ill_data = fop.read_tab_data_file(settings.CIE_illumination_file, 7)

    
    L = LAMBDA_STEP
    bits = 1023
    CIE_ill_source_index = 5 #  source index 5 for daylight
                             #               1 for bulb               
    x_sum = 0
    y_sum = 0
    z_sum = 0

    k = get_K_value(CIE_obs_data, CIE_ill_data, CIE_ill_source_index)


    for lamda in range(LAMBDA_MIN, LAMBDA_MAX, LAMBDA_STEP):
        R = get_interpolated_spectrum_value(lamda, mySpectrum)
        R = R / bits
        S = get_illumination_value(lamda, CIE_ill_data, CIE_ill_source_index)
        
        #X --> index = 1        
        x = get_CIE_value(lamda, CIE_obs_data, 1)
        x_sum = x_sum + (R * S * x * L)

        #Y --> index = 2
        y = get_CIE_value(lamda, CIE_obs_data, 2)
        y_sum = y_sum + (R * S * y * L)

        #Z --> index = 3
        z = get_CIE_value(lamda, CIE_obs_data, 3)
        z_sum = z_sum + (R * S * z * L)
    
    X = k * x_sum
    Y = k * y_sum
    Z = k * z_sum
    return [X, Y, Z]
     

# func : get_illumination_value
# ver : 9.10.2020
# desc : Extract the correct illumination value from illumination data table
#        by wavelength and source type
#        column_index = 1 for (type A) is bulb @ 2856K
#                       2 for (type C) is daylight @ 6774K
#                       3 (type D50) 
#                       4 (type D55)
#                       5 for (type D65) is daylight @ 6504 K
#                       6 (type D75)
# TODO : Make this more generic so that same function can be used for all data extracts. 
# TODO : Check is this becomes faster by testing if new_diff == 0 first
# 
def get_illumination_value(lamda, CIE_ill_data, column_index):
    line_index = 0
    diff = lamda - CIE_ill_data[0][0]
    for i in range (1, len(CIE_ill_data)):
        new_diff = lamda - CIE_ill_data[i][0]
        if abs(diff) < abs(new_diff):
            break
        else:
            diff = new_diff
            line_index = i
    return CIE_ill_data[line_index][column_index]
   

# func : calc_CIE
# ver : 9.10.2020
# desc : Calculate CIE coordinate X, Y or Z depending on coord input
#	     coord = 1 -> X
#		 coord = 2 -> Y
# 	     coord = 3 -> Z
#		 Note! This calculation does not include any standard illumination.
#
def calc_CIE_coord(spectrum, CIE_obs_data, coord):
    #   X = k * SUM[380...780](Wx * R * L)
	# 	W = weighting factor
	# 	R = Radiance factor, scaled 0...1
	# 	L = band width of the CIE data used

    k = get_K_value(CIE_obs_data)
    L = LAMBDA_STEP 	
    bit_scale = 1023
    summ = 0

    for i in range(LAMBDA_MIN, LAMBDA_MAX, L):
        R = get_interpolated_spectrum_value(i, spectrum) / bit_scale
        Wx = k * get_CIE_value(i, CIE_obs_data, coord) * L
        summ = summ + (L * R * Wx)
        
    return summ


# func 	: get_K_value
# ver	: 9.10.2020
# desc	: Calculate CIE scaling factor for X,Y,Z calculation. X coords are scaled 0...100.
#		Use always y values (ci = 2) in calculating k!
# 		  This could be calculated only once per measurement type.
#
def get_K_value(CIE_obs_data, CIE_ill_data, source_index):
    L = LAMBDA_STEP  # wave length bandwith
    summ = 0
    for lamda in range(LAMBDA_MIN, LAMBDA_MAX, L):
        y = get_CIE_value(lamda, CIE_obs_data, 2) # use always y --> index value 2
        S = get_illumination_value(lamda, CIE_ill_data, source_index)
        summ = summ + (S * y * L)
    return (100/summ)

# OBSOLETE after get_interpolated_spectrum_value was made
# function: get_spectrum_value
# ver : 8.4.2019
# desc : Pick a value from spectrum that is closest to wave_length.
#		 ci is index of data type requested.
#	     ci = 0, wave_length column
#        ci = 1, measured bits column
#
def get_spectrum_value(wave_length, spectrum, ci):
	ret_index = 0
	diff = wave_length - spectrum[0][0]
	for i in range (1, len(spectrum)):
		new_diff = wave_length - spectrum[i][0]
		if abs(diff) < abs(new_diff):
			break
		else:
			diff = new_diff
			ret_index = i
	return spectrum[ret_index][1]

# function: get_interpolated_spectrum_value
# ver : 7.10.2020
# desc: Return interpolated value of the spectrum at wave_length.
# TODO: Extend interppolation outside of spectrum
# 
def get_interpolated_spectrum_value(wave_length, spectrum):
    ret_value = -1
    for i in range (0, len(spectrum)):
        diff = wave_length - spectrum[i][0]
        if diff == 0: # exact match
            ret_value = spectrum[i][1]            
            break
        elif diff < 0 and i>0: # larger point found
            linear_coeff = (spectrum[i][1] - spectrum[i-1][1])/(spectrum[i][0] - spectrum[i-1][0])
            ret_value = (wave_length - spectrum[i-1][0]) * linear_coeff + spectrum[i-1][1]
            break
        elif diff < 0 and i == 0: # wave_length is shorter than spectrum begin (313 nm)
            ret_value = spectrum[0][1]
            break
        elif diff > 0 and i == len(spectrum)-1: #wave_length is longer than spectrum end (882 nm)
            ret_value = spectrum[len(spectrum)-1][1]
    return ret_value
 
            

	
# function : get_CIE_value
# ver : 8.4.2019
# desc : Pick a value from CIE standard observer data by wave_length.
#		 ci is index of data type requested.
#		 ci = 0, wave length data column
#	     ci = 1, CIE coordinate x data column
#        ci = 2, CIE coordinate y data column
#        ci = 3, CIE coordinate z data column
#
def get_CIE_value(wave_length, CIE_obs_data, ci):
	ret_index = 0
	diff = wave_length - CIE_obs_data[0][0]
	for i in range (1, len(CIE_obs_data)):
		new_diff = wave_length - CIE_obs_data[i][0]
		if abs(diff) < abs(new_diff):
			break
		else:
			diff = new_diff
			ret_index = i
	return CIE_obs_data[ret_index][ci]

	
# unit test main
# ver 9.10.2020
#
if __name__ == '__main__':
    CIE_data = fop.read_CIE_file("CIE.txt")
    spectrum_data = fop.read_file("spectrum.txt")
    print(get_interpolated_spectrum_value(420, spectrum_data))

    CIE_ill_data = fop.read_tab_data_file("CIE_illuminants.txt", 7)
    ill_value = get_illumination_value(690, CIE_ill_data, 1)
    print(ill_value)
    
    XYZ = calc_XYZ_coords(spectrum_data)
    print(XYZ[0])
    print(XYZ[1])
    print(XYZ[2])

    #print(calc_CIE_coord(spectrum_data, CIE_data, 1))
    #print(calc_CIE_coord(spectrum_data, CIE_data, 2))
    #print(calc_CIE_coord(spectrum_data, CIE_data, 3))

