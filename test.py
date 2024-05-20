import socket
import threading

def server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 8000))
    server.listen(0)
    client, name = server.accept()
    threading.Thread(target=client_handel, args=(client,)).start()
    while True:
        msg = input()
        if msg == 'quit':
            break
        client.send(msg.encode("utf-8"))

    server.close()


def client_handel(conn):
    while True:
        try:
            msg = conn.recv(1024)
            if msg:
                print(msg.decode("utf-8"))
            else:
                conn.close()
                break
        except:
            print("error")
            conn.close()
            break

def client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 8000))
    threading.Thread(target=client_handel, args=(client,)).start()
    while True:
        msg = input()
        if msg == 'quit':
            break
        client.send(msg.encode("utf-8"))

    client.close()


# server()
client()