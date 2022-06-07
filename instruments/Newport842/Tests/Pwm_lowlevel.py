import serial
conn = serial.Serial('COM3',115200, timeout = 3)
#conn.write(b"*swa 500\n")
#conn.write("*cvu\n".encode())
conn.write("*sta\n".encode())
#conn.write(b"*atu 1\n")
#conn.write("*ssa {}\n".format('100u').encode())
print(b"\n".join(conn.readlines()).decode())
conn.close()