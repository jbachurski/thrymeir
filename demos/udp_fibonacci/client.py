import socket, traceback

SERVER_IP = "127.0.0.1"
SERVER_PORT = 7777
SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)

CLIENT_IP = "127.0.0.1"
CLIENT_PORT = 8888
CLIENT_ADDRESS = (CLIENT_IP, CLIENT_PORT)

BYTEORDER = "big"
BYTECOUNT = 8

def main():
    print("Setting up socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(CLIENT_ADDRESS)
    print("Done\n")
    print("Awaiting user input")
    while True:
        n = input("> ")
        try:
            n = int(n)
        except ValueError:
            continue
        else:
            b = n.to_bytes(BYTECOUNT, BYTEORDER)
            sock.sendto(b, SERVER_ADDRESS)
            rb, _ = sock.recvfrom(BYTECOUNT)
            print("<<<", rb)
            r = int.from_bytes(rb, BYTEORDER)
            print("<<< ", r)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        input("...")