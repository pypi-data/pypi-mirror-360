from time import sleep
from tcps import Tcps
from sdg_utils import rand_bytes, log_init, DEBUG
from threading import Thread


class TcpsThread(Thread):
    def __init__(self, host, log):
        super().__init__()
        self.log = log
        self.host = host
        self.exit = False
        self.cnt = 0
        self.start()

    def run(self):
        tcps = Tcps(self.host, log)
        self.log.info("run")
        while not self.exit:
            tx = rand_bytes(mtu=128)
            tcps.write(tx)
            self.cnt += len(tx)
            for i in range(3):
                rx = tcps.read(timeout=1)
                if rx != tx:
                    self.log.error(f"err {repr(rx)} {self.cnt}")
                    if i == 2:
                        self.log.error("exit")
                        return


def tcpstest(host, log):
    tcps = Tcps(host, log)
    tcps.read(timeout=10)
    cnt = 0
    log.info(f"Start {host}")
    while 1:
        tx = rand_bytes(size=128)
        tcps.write(tx)
        cnt += len(tx)
        rx = tcps.read(timeout=10)
        if rx != tx:
            log.error(f"{host} err {repr(rx)} {cnt}")
            break


if __name__ == "__main__":
    log = log_init(level=DEBUG)
    t1 = Thread(target=tcpstest, args=(('192.168.127.100', 50000), log.getChild("0")))
    t2 = Thread(target=tcpstest, args=(('192.168.127.100', 50001), log.getChild("1")))
    t1.daemon = True
    t1.start()
    t2.daemon = True
    t2.start()
    while 1:
        sleep(1)
