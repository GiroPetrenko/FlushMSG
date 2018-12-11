import socket
import threading
import hashlib
import base64

users = ["19cabf441f69ed250b3c033f680a9905fdffd435", "d63aa46e7aa820da3b276a6193c16c2fa7d87762", "c6f3ef98df2bb7dd2834dcccb92750095e9c2317"]

# Giro Petrenko productions, no rights reserved.

keyhash = "b25cf84a7d21f31df0586ed26ac064025e3d38ba"  # cyka
key = "cyka"

def RC4(data, key):
    S = range(256)
    j = 0
    out = []

    # KSA Phase
    for i in range(256):
        j = (j + S[i] + ord(key[i % len(key)])) % 256
        S[i], S[j] = S[j], S[i]

    # PRGA Phase
    i = j = 0
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(chr(ord(char) ^ S[(S[i] + S[j]) % 256]))

    return ''.join(out)


class ThreadedServer(object):

    def __init__(self):
        self.user_list = []
        k = self.read_configure("flushmsg_conf")
        z = k.split(" ")

        self.host = z[0]
        self.port = int(z[1])
        self.MaxUser = int(z[2])
        self.current_user = 0

        print("* --- FLUSHMSG -- [CONFIGURE]")
        print("| Host: %s" % self.host)
        print("| Port: %s" % str(self.port))
        print("| Max User: %s" % str(self.MaxUser))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))


    def read_configure(self, file):
        f = open(file, 'r')
        return f.readline()

    def listen(self):
        self.sock.listen(self.MaxUser)
        print("Ready... Listening.")
        while True:
            client, address = self.sock.accept()
            self.user_list.append(client)
            print("Got connection from [{0}]".format(str(address)))
            self.current_user += 1
            if self.current_user >= 8:
                print("Handling connection that exceeds max range. refusing...")
                client.close()
                return
            client.settimeout(300)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def boardcast(self, msg):
        for sock in self.user_list:
            sock.send(msg.encode("UTF-8"))

    def listenToClient(self, client, address):
        size = 1024
        no_auth = True
        client.send(b"Login? :")
        if client.recv(size) == keyhash.encode("UTF-8") or client.recv(size) == keyhash.encode("UTF-8") + b"\r\n":
            pass
        else:
            print("Unsuccessful login attempt. Refusing...")
            client.send(b"Login failed. Password error.\n\n")
            client.close()
            return
        client.send(b"Welcome to Blyatmann's kindergarten, type ~logout to logout.\n\n")
        while True:
            try:
                data = client.recv(size)
                if data != b"~logout\n" or data != b"~logout\r\n":
                    if no_auth:
                        self.boardcast("[{0}]: {1}".format(str(address), data.decode("UTF-8")))

                else:
                    self.boardcast("[{0}]: LOGOUT".format(str(address)))
                    client.close()
            except Exception as e:
                print("Error from server side.")
                print(e)
                client.close()
                print("Connection from {0} terminated.".format(address))
                self.current_user -= 1
                return False


ThreadedServer().listen()
