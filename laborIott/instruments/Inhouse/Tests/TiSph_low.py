import usb.core

requests = { 'REQ_ECHO':0,'REQ_SET_SPEED' : 1, 'REQ_GET_SPEED' : 2, 'REQ_SET_DELTA' : 3, 
'REQ_GET_DELTA' : 4, 'REQ_STOP' : 5, 'REQ_SET_RELEASE' : 6,'REQ_SET_DIGI_OUT': 7, 'REQ_GET_WAVELENGTH' : 8, 'REQ_USART_LOOPBACK':9}

conn = usb.core.find(idVendor = 0xcacc, idProduct = 2)


ret = conn.ctrl_transfer(0xc0, requests['REQ_GET_WAVELENGTH'], 0, 0, 4 ) #bReq, wVal, wIndex, len)
print(ret)
ret = conn.ctrl_transfer(0xc0, requests['REQ_GET_SPEED'], 0, 0, 2)
print(ret)
ret = conn.ctrl_transfer(0xc0, requests['REQ_USART_LOOPBACK'], 30, 0, 1) #connect rx/tx, otherwise it gives random numbers
print(ret) 
