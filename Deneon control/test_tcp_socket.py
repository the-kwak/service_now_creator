import socket
import re

def lightware_vol_get():
    HOST = '172.21.251.206'
    PORT = 6107
    buff = 1024
    addr = (HOST,PORT)
    ltw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ltw.connect(addr)
    #data = b'CALL /MEDIA/VIDEO/XP:switch(0:O2)\r\n'
    data = b'GET /SYS/MB/ADAUOUT/ANALOGOUTDIFF.VolumePercent\r\n'
    ltw.send(data)
    response = ltw.recv(buff)
    str_response = response.decode()
    print(str_response.split('=')[1].rstrip())
    ltw.close()

#lightware_vol_get()

def lightware_vol_get():
    HOST = '172.21.251.206'
    PORT = 6107
    buff = 1024
    addr = (HOST,PORT)
    ltw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ltw.connect(addr)
    data = b'CALL /MEDIA/VIDEO/XP:switch(0:O2)\r\n'
    ltw.send(data)
    response = ltw.recv(buff)
    str_response = response.decode()
    print(str_response)
    ltw.close()

def lightware_get_switch():
    HOST = '172.21.251.206'
    PORT = 6107
    buff = 1024
    addr = (HOST,PORT)
    ltw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ltw.connect(addr)
    data = b'GET /MEDIA/VIDEO/O*.ConnectedSource\r\n'
    ltw.send(data)
    response = ltw.recv(buff)
    response = response.decode()
    ltw.close()
    output_list = response.split('\r\n')
    output_list.pop()
    sources_out = []
    for i in output_list:
        sources_out.append(i.split('=')[1])
    print(output_list)
    print(sources_out)
    ltw.close()

lightware_get_switch()

def dvd():
    HOST = '172.21.251.207'
    PORT = 9030
    buf = 1024
    addr = (HOST,PORT)


    ## Command Data to send to dvd
    data_prefix = b'\x40'
    command = b'02348'
    data_postfix = b'\x0D'

    ## Combining the prefix command and postfix
    data = data_prefix + command + data_postfix


    ### Creating the TCP socket Connection to the DVD player to send commands to it.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f'sending command {data}')
        s.connect(addr)
        s.sendall(data)
        data = s.recv(buf)

    print(f'Received {data!r}')
