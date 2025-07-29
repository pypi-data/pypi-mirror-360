from struct import pack
from sdg_utils import log_open
from sdg_dev import SdgDevMaster, DevException, SdgDevAsync

log = log_open()


class MyMaster(SdgDevMaster):
    def __init__(self):
        super().__init__(port='', log=log.getChild('mastr'))

    def check_id(self):
        return self.send(b'\x00', ackfrmt='H') == 0xAAAA

    def send_val(self, val):
        return self.send(b'\x31' + pack('I', val), ackfrmt='')

    def request_val(self):
        return self.send(b'\x32', ackfrmt='I', timeout=.1, remix=0)


class MySlave(SdgDevAsync):
    def __init__(self, port):
        super().__init__(port, log=log.getChild('slave'))
        self.val = 0x04030201
        self.ID = 0xAAAA
        self.add_incmd(b'\x00', '', self._getid)
        self.add_incmd(b'\x31', 'I', self._setval)
        self.add_incmd(b'\x32', '', self._getval)
        self.add_incmd(b'\x33', '', lambda: pack('BBBB', 5, 6, 7, 8))

    def _setval(self, val):
        self.val = val
        return b''

    def _getval(self):
        return pack('I', self.val)

    def _getid(self):
        return pack('H', self.ID)


if __name__ == "__main__":
    print('Порт для master-a будет определен автопоиском по всем доступным портам системы.')
    PORT = input("Ведите название порта для slave-a или нажмите Enter(по умочанию 'COM26'):")
    if not PORT:
        PORT = 'COM26'

    slave = MySlave(PORT)
    master = MyMaster()
    master.search_port()

    try:
        val = master.request_val()
        log.info(f"request_val 0x{val:08x}")

        log.info(f"send new val 0x01020304")
        master.send_val(0x01020304)

        val = master.request_val()
        log.info(f"request_val 0x{val:08x}")

        a, b, c, d = master.send(b'\x33', ackfrmt='BBBB')
        log.info(f"{a}, {b}, {c}, {d}")

    except DevException as e:
        log.error(e)

    master.close()
    slave.close()
