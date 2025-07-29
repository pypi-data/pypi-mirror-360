# -*- coding: utf8 -*-
import sys
import time
import socket
from select import select
if sys.version_info >= (3, 5):
    from socket import socketpair
else:
    from .pair import socketpair


class UdpIO:
    def __init__(self,
                 host=('127.0.0.1', 30000),
                 dest=('127.0.0.1', 30001),
                 log=None):
        self.pair = socketpair()  # пара сокетов для self-pipe трюка
        self.dest = dest
        self.log = log
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if dest[0].split('.')[3] == '255':  # todo: ?
            self.log.debug("UdpIO broadcast")
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.s.bind(host)
        self.s.setblocking(0)
        self.inputs = [self.s, self.pair[0]]
        self.busy = False
        self.exit = False
        if self.log:
            self.log.debug("UdpIO open")

    def close(self):
        self.pair[1].send(b'\0')  # self-pipe трюк
        while self.busy:
            time.sleep(.1)
        self.s.close()
        for s in self.pair:
            s.close()
        if self.log:
            self.log.debug("close")

    def read(self, timeout=None):
        if self.exit or self.s.fileno() == -1:
            raise IOError("UdpIO rd: socket closed!")
        data = b''
        self.busy = True
        rs, ws, es = select([self.pair[0], self.s], [], [], timeout)
        for s in rs:
            if s == self.s:
                data = s.recv(4096)
                if self.log:
                    self.log.debug("UdpIO rd %d bytes", len(data))
            else:
                self.exit = True
                self.log.debug("UdpIO rd: self-pipe trick exit signal")
        self.busy = False
        return data

    def write(self, data):
        if self.exit or self.s.fileno() == -1:
            raise IOError("UdpIO wr: socket closed!")
        self.busy = True
        self.s.sendto(data, self.dest)
        if self.log:
            self.log.debug("UdpIO wr %d bytes", len(data))
        self.busy = False


import threading
if __name__ == '__main__':
    logging.basicConfig(format='%(relativeCreated)04d %(name)-5s %(levelname)s %(message)s', level=logging.DEBUG)

    class NullModem(threading.Thread):
        def __init__(self, udp_io):
            super().__init__()
            self.udp_io = udp_io
            self._exit = False
            self.start()

        def close(self):
            self._exit = True

        def run(self):
            while not self._exit:
                try:
                    rx = self.udp_io.read(1)
                except IOError as e:
                    self.udp_io.log.error(e)
                else:
                    if rx:
                        self.udp_io.write(rx)


    s1 = UdpIO(host=('127.0.0.1', 30001), dest=('127.0.0.1', 30000), log=logging)
    s2 = UdpIO(host=('127.0.0.1', 30000), dest=('127.0.0.1', 30001), log=logging)

    NullModem(s2)

    while True:
        try:
            s1.write(b'olololo')
            s1.write(b'olololo')
            s1.write(b'olololo')
            s1.read(1)
            s1.read(1)
            s1.read(1)
            # s1.close()
            s1.read(10)
        except IOError as e:
            print(e)
            break
