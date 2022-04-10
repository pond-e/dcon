import serial
s = serial.Serial('/dev/rfcomm0', 9600, timeout=30)
textlen=1
print(s.read(textlen))
s.write(b'hello\n')
s.close()
