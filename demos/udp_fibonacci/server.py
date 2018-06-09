import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 7777
SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)

BYTEORDER = "big"
BYTECOUNT = 8
INVALID = (2**(8*BYTECOUNT) - 1).to_bytes(BYTECOUNT, BYTEORDER)

def main():
    print("Generating fibonacci numbers...")
    fibonacci = [0, 1]
    while len(fibonacci) < 50:
        fibonacci.append(fibonacci[-2] + fibonacci[-1])
    print(fibonacci)
    print("Done\n")
    print("Setting up socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SERVER_ADDRESS)
    print("Done\n")
    print("Listening")
    while True:
        data, address = sock.recvfrom(BYTECOUNT)
        data = int.from_bytes(data, BYTEORDER)
        print(f"Received: {data} from {address}")
        if data < len(fibonacci):
            b = fibonacci[data].to_bytes(BYTECOUNT, BYTEORDER)
        else:
            b = INVALID
        sock.sendto(b, address)

if __name__ == "__main__":
    main()