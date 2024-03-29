import socket
import select
import time
import sys

from ldaptor.protocols import pureldap, pureber
from time import gmtime, strftime


buffer_size = 4096
delay = 0.0001
forward_to = ('samba4.test.dom', 389) # Target LDAP server
filthy_basedn = 'dc=test, dc=dom'     # BaseDN with the whitespace

class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception, e:
            print e
            return False

class TheServer:
    input_list = []
    channel = {}

    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)

    def main_loop(self):
        self.input_list.append(self.server)
        while 1:
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept()
                    break

                self.data = self.s.recv(buffer_size)
                if len(self.data) == 0:
                    self.on_close()
                else:
                    self.on_recv()

    def on_accept(self):
        forward = Forward().start(forward_to[0], forward_to[1])
        clientsock, clientaddr = self.server.accept()
        if forward:
            print clientaddr, "has connected"
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            print "Can't establish connection with remote server.",
            print "Closing connection with client side", clientaddr
            clientsock.close()

    def on_close(self):
        print self.s.getpeername(), "has disconnected"
        #remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]
 

    def on_recv(self):
        data = self.data
        # here we can parse and/or modify the data before send forward
        if data:
            if data.find(filthy_basedn) == -1:
                print strftime("%Y-%m-%d %H:%M:%S : ", gmtime()) + " LDAP request -> no filthy baseDn -> relaying to " + str(forward_to)
            else:
                test = pureldap.LDAPMessage(data)
                #print test.value
                berdecoder = pureldap.LDAPBERDecoderContext_TopLevel(
                    inherit=pureldap.LDAPBERDecoderContext_LDAPMessage(
                    fallback=pureldap.LDAPBERDecoderContext(fallback=pureber.BERDecoderContext()),
                    inherit=pureldap.LDAPBERDecoderContext(fallback=pureber.BERDecoderContext())))
                o, bytes = pureber.berDecodeObject(berdecoder, data)
                print strftime("%Y-%m-%d %H:%M:%S : ", gmtime()) + " LDAP request -> has filthy baseDn : " + o.value.baseObject
                o.value.baseObject = str(o.value.baseObject).replace(", ",",")
                print "  -> converted baseDn : " + o.value.baseObject + " -> relaying to " + str(forward_to)
                data = str(o)

        self.channel[self.s].send(data)


if __name__ == '__main__':
        server = TheServer('', 389)
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print "Ctrl C - Stopping server"
            sys.exit(1)
