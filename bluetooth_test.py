import serial
s = serial.Serial('/dev/rfcomm0', 9600, timeout=30)
textlen=1
print('データを受け取る:')
x = s.read(textlen)
print(x)
if(x=='1'):
    print('recv 1')
else:
    print('recv other')
s.write(b'hello\n')
s.close()
