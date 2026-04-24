import socket
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('10.43.0.1', 11008))
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
s.settimeout(3)

for i in range (2):
	s.send('*IDN?\n'.encode())
	back = s.recv(1000)
	print(back)
	
s.close()