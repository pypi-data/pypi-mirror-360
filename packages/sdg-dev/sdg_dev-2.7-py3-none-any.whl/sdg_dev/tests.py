"""
Created on 9 окт. 2019 г.

@author: chernecov
"""

import random
import unittest
from struct import pack
from sdg_dev import SdgDevMaster, SdgDevAsync, DevException, DevBadCode, BROADCAST
from sdg_utils import log_init

log = log_init()

PORT_SLAVE = 'COM7'
PORT_MASTER = 'COM4'
PORT_CFG = '500000_O_2'
DUMP_SLAVE = 'slave.dat'
DUMP_MASTER = 'mastr.dat'


class Master(SdgDevMaster):

    def __init__(self, port, portcfg=PORT_CFG, addr=None, log=log.getChild('mastr')):
        super().__init__(port, portcfg, addr, log=log, dump=DUMP_MASTER)

    def check_id(self):
        slave_id = self.send(b'\x00' + pack('H', 0x5555), ackfrmt='I')
        return True if slave_id == 0x04030201 else False


class MasterAsync(SdgDevAsync):

    def __init__(self, port, portcfg=PORT_CFG, addr=None, log=log.getChild('async')):
        super().__init__(port, portcfg, addr, log=log, dump=DUMP_MASTER)

    def check_id(self):
        slave_id = self.send(b'\x00' + pack('H', 0x5555), ackfrmt='I')
        return True if slave_id == 0x04030201 else False


class Slave(SdgDevAsync):

    def __init__(self, port, portcfg=PORT_CFG, addr=None, log=log.getChild('slave')):
        super().__init__(port, portcfg, addr, log=log, dump=DUMP_SLAVE)
        self.val = 0x0001

        self.add_incmd(b'\x00', 'H', self._incmd_getid)
        self.add_incmd(b'\x01', '', self._incmd_getval)
        self.add_incmd(b'\x02', 'I', self._incmd_setval, broadcast=False)
        self.add_incmd(b'\x03', 'I', self._incmd_setval, broadcast=True)
        self.add_incmd(b'\x04', 'raw', self._incmd_rawinput)
        self.add_incmd(b'\x05', 'BBBB', self._incmd_swap)
        self.add_incmd(b'\x06', 'B', self._incmd_other)

    def _incmd_getval(self):
        return pack('I', self.val)

    def _incmd_setval(self, val):
        self.val = val
        return b''

    def _incmd_rawinput(self, rawdata):
        return rawdata

    def _incmd_swap(self, a, b, c, d):
        return pack('BBBB', d, c, b, a)

    def _incmd_other(self, val):
        if val == 0:
            return b'\x55'
        if val == 1:
            return b''
        if val == 2:
            return True
        if val == 3:
            return None
        if val == 4:
            return False
        if val == 5:
            return -4
        if val == 6:
            return -255
        return val

    def _incmd_getid(self, val):
        return pack('I', 0x04030201) if val == 0x5555 else False


class TestDeviceAutoSeach(unittest.TestCase):
    def setUp(self):
        log.info("--- Тест автопоиска порта SdgDevMaster ---")
        self.slave = Slave(PORT_SLAVE)
        self.master = Master('')

    def tearDown(self):
        self.slave.close()
        self.master.close()

    def test_autoseach(self):
        self.assertEqual(PORT_MASTER, self.master.search_port())


class TestDeviceAutoSeachAsync(TestDeviceAutoSeach):
    def setUp(self):
        log.info("--- Тест автопоиска порта SdgDevAsync ---")
        self.slave = Slave(PORT_SLAVE)
        self.master = MasterAsync('')


class TestDeviceMasterAndSlave(unittest.TestCase):
    def setUp(self):
        self.slave = Slave(PORT_SLAVE)
        self.master = Master(PORT_MASTER)

    def tearDown(self):
        self.slave.close()
        self.master.close()

    def test_slave_retval_incmd(self):
        self.assertEqual(b'\x55', self.master.send(b'\x06\x00'))
        self.assertEqual(b'', self.master.send(b'\x06\x01', ackfrmt="raw"))
        self.assertEqual(True, self.master.send(b'\x06\x01', ackfrmt=''))
        with self.assertRaises(DevException):
            self.master.send(b'\x06\x01', ackfrmt='B')
        self.assertEqual(True, self.master.send(b'\x06\x02', ackfrmt=''))
        self.assertEqual(b'', self.master.send(b'\x06\x02', ackfrmt='raw'))
        with self.assertRaises(DevException) as ctx:
            self.master.send(b'\x06\x03')
        self.assertEqual(ctx.exception.badcode, None)
        with self.assertRaises(DevException) as ctx:
            self.master.send(b'\x06\x04')
        self.assertEqual(ctx.exception.badcode.val, DevBadCode.EXECERR)
        with self.assertRaises(DevException) as ctx:
            self.master.send(b'\x06\x05')
        self.assertEqual(ctx.exception.badcode.val, -4)
        with self.assertRaises(DevException) as ctx:
            self.master.send(b'\x06\x06')
        self.assertEqual(ctx.exception.badcode.val, -255)
        with self.assertRaises(DevException) as ctx:
            self.master.send(b'\x06\x07')
        self.assertEqual(ctx.exception.badcode.val, DevBadCode.EXECERR)
        self.assertEqual(None, self.master.send(b'\x06\x03', ackfrmt='raw', safe=True))
        self.assertEqual(None, self.master.send(b'\x06\x05', ackfrmt='raw', safe=True))
        self.assertEqual(None, self.master.send(b'\x06\x07', ackfrmt='raw', safe=True))
        self.assertEqual(None, self.master.send(b'\x07\x03', ackfrmt='raw', safe=True))

    def test_cmd_swap(self):
        log.info('--- тест команды (0х05) смены местами 4х байт ---')
        for i in range(50):
            i = random.randint(0, 250)
            ret = self.master.send(bytes([0x05, i + 0, i + 1, i + 2, i + 3]), ackfrmt='BBBB')
            self.assertEqual(ret, (i + 3, i + 2, i + 1, i + 0))

    def test_exchangeval(self):
        log.info('--- передача параметра с последующим запросом и проверкой значения в слейве ---')
        requested_val = self.master.send(b'\x01', ackfrmt='I')
        self.assertEqual(requested_val, self.slave.val)
        for _ in range(50):  # (random.randrange(0,200)):
            i = random.randrange(0, 0xffffffff)
            self.assertTrue(self.master.send(b'\x02' + pack("I", i), ackfrmt=''))
            self.assertEqual(i, self.slave.val)

    def test_master_send_fail_cmd(self):
        log.info('--- передача команд c неверными параметрами ---')
        with self.assertRaises(AssertionError):
            self.master.send('ololo')
        with self.assertRaises(AssertionError):
            self.master.send(0x10)
        with self.assertRaises(AssertionError):
            self.master.send(None)

    def test_master_send_uncknown_cmd(self):
        log.info('--- передача неизвестной команды ---')
        with self.assertRaises(DevException) as ctx:
            self.master.send(b'\x66')
        self.assertEqual(ctx.exception.badcode.val, DevBadCode.UNKNOWN)

    def test_master_send_errsize_cmd(self):
        log.info('--- передача команды неверной длины ---')
        with self.assertRaises(DevException) as ctx:
            self.master.send(b'\x01\x01')
        self.assertEqual(ctx.exception.badcode.val, DevBadCode.SIZEERR)

    def test_master_wait_errsize_cmd(self):
        log.info('--- ожидание мастером ответа неверной длины ---')
        with self.assertRaises(DevException):
            self.master.send(b'\x01', ackfrmt='IIII')

    def test_slave_anysize_incmd(self):
        log.info("--- слейв принимает команду 0x04 с любым размером (ackfrmt='raw') ---")
        self.assertEqual(b'', self.master.send(b'\x04', ackfrmt='raw'))
        self.assertEqual(b'\x00', self.master.send(b'\x04\x00', ackfrmt='raw'))
        self.assertEqual(b'\x00\x01', self.master.send(b'\x04\x00\x01', ackfrmt='raw'))
#         self.assertEqual(b'\x00\x01\x02', self.master.send(b'\x04\x00\x01\x02', ackfrmt='raw'))


class TestDeviceMasterAsyncAndSlave(TestDeviceMasterAndSlave):
    def setUp(self):
        self.slave = Slave(PORT_SLAVE)
        self.master = MasterAsync(PORT_MASTER)


class TestDeviceMasterAndSlaveWithAddr(TestDeviceMasterAndSlave):
    def setUp(self):
        self.slave = Slave(PORT_SLAVE, addr=b'\x10')
        self.master = Master(PORT_MASTER, addr=b'\x10')

    def test_slave_broadcast_msg(self):
        log.info('--- слейв принимает разрешенную широковещательную команду (broadcast=True) --- ')
        self.slave.val = 0x12345678
        self.assertTrue(self.master.sendto(BROADCAST, b'\x03\x00\x00\x00\x00',
                                           ackfrmt='', timeout=0))
        self.assertEqual(self.slave.val, 0x0000)

        log.info('--- слейв не принимает неразрешенную широковещательную команду ---')
        self.slave.val = 0x12345678
        self.assertTrue(self.master.sendto(BROADCAST, b'\x02\x00\x00\x00\x00', ackfrmt=''))
        self.assertEqual(self.slave.val, 0x12345678)


class TestDeviceMasterAsyncAndSlaveWithAddr(TestDeviceMasterAndSlaveWithAddr):
    def setUp(self):
        self.slave = Slave(PORT_SLAVE, addr=b'\x10')
        self.master = MasterAsync(PORT_MASTER, addr=b'\x10')


if __name__ == "__main__":
    unittest.main()
