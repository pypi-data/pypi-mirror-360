# -*- coding: utf8 -*-
import sys
from time import sleep
from select import select
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
if sys.platform == 'linux':
    from socket import SO_KEEPALIVE, IPPROTO_TCP, TCP_KEEPCNT, TCP_KEEPIDLE, TCP_KEEPINTVL
else:
    from socket import SIO_KEEPALIVE_VALS, SO_KEEPALIVE
if sys.version_info >= (3, 5):
    from socket import socketpair
else:
    from .pair import socketpair


class Tcpc:
    def __init__(self, host=('127.0.0.1', 30000), log=None):
        self.host = host
        self.log = log
        self.pair = socketpair()  # пара сокетов для self-pipe трюка
        self.sock = None
        self.busy = False
        self.exit = False

    def close(self):
        self.pair[1].send(b'\0')  # self-pipe трюк
        self.exit = True
        while self.busy:  # ждем когда завершится чтение/запись
            sleep(.1)
        if self.sock:
            self.sock.close()
            self.sock = None
        self.log.info("tcpc close")

    def __keepalive(self, keepalivetime=2, keepaliveinterval=1):
        self.sock.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)
        if sys.platform == 'linux':
            # TCP_KEEPCNT Максимальное количество тестов keepalive, до разрыва соединения.
            self.sock.setsockopt(IPPROTO_TCP, TCP_KEEPCNT, 3)
            # TCP_KEEPIDLE - Время бездействия (сек), перед отправкой зондирующих сообщений
            self.sock.setsockopt(IPPROTO_TCP, TCP_KEEPIDLE, keepalivetime)
            # TCP_KEEPINTVL - Время (в секундах) между пробными сообщениями.
            self.sock.setsockopt(IPPROTO_TCP, TCP_KEEPINTVL, keepaliveinterval)
        else:
            # keepalivetime - интервал между посылкой сообщений при пассивном состоянии канала
            # keepaliveinterval - определяет интервал посылки сообщений, если ответ не получен
            self.sock.ioctl(SIO_KEEPALIVE_VALS, (1, keepalivetime * 1000, keepaliveinterval * 1000))

    def connect(self, timeout=1):
        if self.sock:  # соединение уже установлено
            return True
        self.busy = True
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.settimeout(timeout)
        self.__keepalive(keepaliveinterval=timeout or 1)
        try:
            self.sock.connect(self.host)
            self.log.info("tcpc connected to %s", repr(self.host))
            ret = True
        except (ConnectionRefusedError, TimeoutError) as e:
            self.log.error("tcpc connect fail %s", repr(e))
            self.sock.close()
            self.sock = None
            ret = False
        self.busy = False
        return ret

    def read(self, timeout=None):
        if self.exit:
            sleep(.1)
        elif self.connect(timeout):
            self.busy = True
            rs, wr, es = select([self.pair[0], self.sock], [], [], timeout)
            for s in rs:
                if s == self.sock:
                    try:
                        data = self.sock.recv(4096)
                        self.busy = False
                        return data
                    except ConnectionResetError as e:
                        self.log.error("tcpc read fail %s", repr(e))
                # сокет закрывается при ошибках чтения или self-pipe трюке
                self.sock.close()
                self.sock = None
            self.busy = False

    def write(self, data):
        if self.exit:
            sleep(.1)
        elif self.connect():
            self.busy = True
            try:
                self.sock.send(data)
            except ConnectionResetError as e:
                self.log.error("tcpc write fail %s", repr(e))
                self.sock.close()
                self.sock = None
            self.busy = False


import logging
import threading

if __name__ == "__main__":
    logging.basicConfig(format='%(relativeCreated)04d %(name)-5s %(levelname)s %(message)s', level=logging.DEBUG)
    tcpc = Tcpc(log=logging)
    threading.Timer(5.0, lambda: tcpc.close()).start()

    while 1:
        rx = tcpc.read(timeout=30)
        logging.info("rx %s", repr(rx))
