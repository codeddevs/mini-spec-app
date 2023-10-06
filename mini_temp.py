# file name : mini_temp
# ver : 16.10.2019
# desc : Temperature measurement of blacbody spectrum.

# func: find_maximum_l
# ver: 15.10.2019
# desc: Find wavelength corresponding maximum intensity of a black body spectrum.
#       Notice, returns only first if many maximums.
#
def find_maximum_l(data):
    int_data = [x[1] for x in data]
    max_index = int_data.index(max(int_data))
    return data[max_index][0]

# func: calc_temp
# ver: 16.10.2019
# desc: Use Wien's displacement law T = b / max_lamda to calculate source temperature. Use unit nm
# with input value max_lambda --> b = 2.898*10⁶ nm*K
#
def calc_temp(max_lamda):
    b = 2.898e6
    return b/max_lamda

# func: get_bb_temp
# ver: 16.10.2019
# desc: Returns temperature of a black body.
def get_bb_temp(data):
    max_lamda = find_maximum_l(data)
    max_temp = calc_temp(max_lamda)
    return max_temp

# ver : 20.10.2019
# desc: Moving average low pass filter. 
#       Data is 2dim array containing both pos and int value.
#
def lowpass_filter(data):
        filt = [0.10, 0.80, 0.10]
        filt_data = []
        int_data = [x[1] for x in data]
                
        if(len(data) > 3):
                filt_data.append(int_data[0])               # first item unchanged
                for i in range(1,len(int_data)-1):
                        sum = filt[0]*int_data[i-1] + filt[1]*int_data[i] + filt[2]*int_data[i+1]
                        filt_data.append(sum)
                filt_data.append(int_data[len(int_data)-1]) # last item unchanged

        for i in range(0, len(filt_data)):
                data[i][1] = filt_data[i]
                
        return data


