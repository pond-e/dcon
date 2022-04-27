import bluetooth

PORT = 1
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(('', PORT))
server_sock.listen(1)

client_sock, client_addport = server_sock.accept()

print('client_addport')
print(client_addport)
print('client_sock')
print(client_sock)
#sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
#client_sock.connect(client_addport)
while True:
    data = client_sock.recv(1024)
    print(data)
    client_sock.sendall('1\n'.encode())
