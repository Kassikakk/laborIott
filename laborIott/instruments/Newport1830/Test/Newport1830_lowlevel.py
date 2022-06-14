from ctypes import windll, c_char_p, c_ulong, create_string_buffer, byref, c_double, c_int, Structure, pointer,POINTER


dll = windll.LoadLibrary("../Inst/usbdll")
buflen = 128 #sellest pikemaid stringe küll ei tule
buf = create_string_buffer(buflen)
bread = c_ulong()

dll.newp_usb_init_system()
dll.newp_usb_init_product(0xCEC7)
#nüüd oleks vaja siin sisse tõmmata product id
#(teine variant on keyd kasutada)
dll.newp_usb_get_device_info(buf)

if len(buf.value) > 0: #siis midagi on taga
	#Leiame ID, millega edasisi toiminguid teha
	devID = int(buf.value[:buf.value.find(b',')])
	#dll.newp_usb_send_ascii(devID, c_char_p(b"W800"), c_ulong(4))
	dll.newp_usb_send_ascii(devID, c_char_p(b"PM:AUTO?"), c_ulong(9))
	dll.newp_usb_get_ascii(devID, buf, buflen, byref(bread))
	print(float(buf.value[:buf.value.find(b'\n')]))
	#b"*cvu \n\r" -> D?
	#b"*swa " + str(wl) + '\n\r' -> Wnnnn / W?
	
	


dll.newp_usb_uninit_system()
