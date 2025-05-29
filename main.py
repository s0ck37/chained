import uuid
import socket
import threading

BIND_IP   = "127.0.0.1"
BIND_PORT = 8000

proxy_list = [
    ("127.0.0.1",9050),
    ("161.35.31.237",1080)
]

print(r"""
 ________  ___  ___  ________  ___  ________   _______   ________     
|\   ____\|\  \|\  \|\   __  \|\  \|\   ___  \|\  ___ \ |\   ___ \    
\ \  \___|\ \  \\\  \ \  \|\  \ \  \ \  \\ \  \ \   __/|\ \  \_|\ \   
 \ \  \    \ \   __  \ \   __  \ \  \ \  \\ \  \ \  \_|/_\ \  \ \\ \  
  \ \  \____\ \  \ \  \ \  \ \  \ \  \ \  \\ \  \ \  \_|\ \ \  \_\\ \ 
   \ \_______\ \__\ \__\ \__\ \__\ \__\ \__\\ \__\ \_______\ \_______\
    \|_______|\|__|\|__|\|__|\|__|\|__|\|__| \|__|\|_______|\|_______|
                                                                      
 ~ Proxy chain trough a simple proxy server
""")

print("[Proxy chain] ")
for proxy in proxy_list:
    print(f"  {proxy[0]}:{proxy[1]}")
print("")

def proxy_connect(sock,host,port):
    sock.send(b'\x05\x01\x00')
    hello_response = sock.recv(2)
    if hello_response[1] == 0xFF:
        return 1
    host = host.encode()
    host_len = len(host).to_bytes(1,byteorder='big')
    port = port.to_bytes(2,byteorder='big')
    sock.send(b'\x05\x01\x00\x03'+host_len+host+port)
    connect_response = sock.recv(10)
    if connect_response[1] != 0x00:
        return connect_response[1]
    return 0

def handle_connection(cuuid,sock):
    global proxy_list

    def forward(source_sock,target_sock):
        source_sock.settimeout(2)
        while True:
            try:
                data = source_sock.recv(1024)
                if not data:
                    break
                target_sock.sendall(data)
            except:
                break

    redirect_sock = socket.socket()
    redirect_sock.connect(proxy_list[0])
    for proxy in range(1,len(proxy_list)):
        proxy_connect(redirect_sock,proxy_list[proxy][0],proxy_list[proxy][1])
    fw_one = threading.Thread(target=forward,args=(redirect_sock,sock,))
    fw_two = threading.Thread(target=forward,args=(sock,redirect_sock,))
    fw_one.start()
    fw_two.start()
    print(f"[{cuuid}] Forwarding sockets for client")

def main():
    global BIND_IP, BIND_PORT
    print(f"Listening on {BIND_IP}:{BIND_PORT}")
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((BIND_IP, BIND_PORT))
    server_socket.listen(5)
    while True:
        con, con_addr = server_socket.accept()
        cuuid = uuid.uuid4()
        print(f"[{cuuid}] New client {con_addr[0]}:{con_addr[1]} connected")
        th = threading.Thread(target=handle_connection,args=(cuuid,con,))
        th.start()

if __name__ == "__main__":
    main()
