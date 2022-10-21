from ctypes import windll, c_char_p, create_string_buffer, byref, c_double, c_int, Structure, pointer,POINTER
'''
class JString(Structure):
	_fields_ = [("defstr", c_char_p),("rep", c_char_p),("do_free", c_int)]
jstr = JString()
'''
class DblArr(Structure):
	_fields_ = [("len", c_int),("data", POINTER(c_double))]
darr = DblArr() 

dll = windll.LoadLibrary("../OmniDriver32")
retstr = c_char_p()
retdbl = c_double()
handle = dll.Wrapper_Create()
#print(dll.Wrapper_getBuildNumber(handle))
#dll.Wrapper_getApiVersion(handle,retstr)

dll.Wrapper_getApiVersion(handle,byref(retstr)) #või pointer?
print(retstr.value)

noSpm = dll.Wrapper_openAllSpectrometers(handle)
dll.Wrapper_getSerialNumber(handle,0,byref(retstr))
print(retstr.value)
dll.Wrapper_getName(handle,0,byref(retstr))
print(retstr.value)
dll.Wrapper_getFirmwareVersion(handle,0,byref(retstr))
print(retstr.value)
dll.Wrapper_getWavelengthIntercept.restype = c_double
print(dll.Wrapper_getWavelengthIntercept(handle, 0))

dll.Wrapper_setIntegrationTime(handle,0,1000)
dll.Wrapper_setCorrectForElectricalDark(handle,0,1)


dll.Wrapper_getSpectrum(handle,0,byref(darr))
print([darr.data[i] for i in range(darr.len)])
#print(darr.data[1])
dll.Wrapper_getWavelengths(handle,0,byref(darr))
print([darr.data[i] for i in range(darr.len)])

dll.Wrapper_closeAllSpectrometers(handle)
dll.Wrapper_Destroy(handle);
