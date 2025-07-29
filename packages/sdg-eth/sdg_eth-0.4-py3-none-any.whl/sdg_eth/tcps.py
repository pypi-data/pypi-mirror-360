import sys
import logging
from time import sleep
from select import select
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
if sys.version_info >= (3, 5):
    from socket import socketpair
else:
    from .pair import socketpair


class Tcps:
    def __init__(self,
                 host=('127.0.0.1', 30000),
                 log=None):
        self.pair = socketpair()  # пара сокетов для self-pipe трюка
        self.log = log
        self.host = host
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.bind(host)
        self.server.listen(5)
        self.clients = []
        if self.log:
            self.log.debug("tcps %s wait connection", repr(host))
        self.busy = False

    def close(self):
        self.pair[1].send(b'\0')  # self-pipe трюк
        while self.busy:
            sleep(.1)
        for s in self.clients:
            s.close()
        if self.log:
            self.log.debug("tcps %s close", repr(self.host))

    def new_client_cb(self, newclient):
        pass

    def read(self, timeout=None):
        rx = ''
        self.busy = True
        rs, [], [] = select([self.server, self.pair[0]] + self.clients, [], [], timeout)
        for s in rs:
            if s == self.server:
                newclient, addr = s.accept()
                self.clients.append(newclient)
                self.new_client_cb(newclient)
                if self.log:
                    self.log.debug("tcps %s new client %s", repr(self.host), repr(addr))
            elif s == self.pair[0]:
                if self.log:
                    self.log.debug("tcps %s self-pipe trick signal", repr(self.host))
                break
            else:  # clients
                try:
                    rx = s.recv(4096)
                except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError) as e:
                    if self.log:
                        self.log.error("tcps %s read fail %s", repr(self.host), repr(e))
                    self.clients.remove(s)
                    s.close()
                break
        self.busy = False
        return rx

    def write(self, data):
        ret = 0
        for s in self.clients:
            try:
                s.send(data)
                ret += 1
            except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError) as e:
                if self.log:
                    self.log.error("tcps %s write fail %s", repr(self.host), repr(e))
                self.clients.remove(s)
                s.close()
        return ret != 0


if __name__ == "__main__":
    logging.basicConfig(format='%(relativeCreated)04d %(name)-5s %(levelname)s %(message)s', level=logging.DEBUG)

    # tcps = Tcps(host=('192.168.127.100', 50001), log=logging)
    tcps = Tcps(host=('127.0.0.1', 30000), log=logging)
    while 1:
        rx = tcps.read()
        if rx:
            print(rx)
        sleep(1)

