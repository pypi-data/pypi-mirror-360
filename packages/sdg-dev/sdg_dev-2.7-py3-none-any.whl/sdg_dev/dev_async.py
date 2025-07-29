"""
Created on 3 окт. 2019 г.
@author: chernecov

Модуть содержит класс DevAsync для обмена командами,
через подключаемый интерфейс ввода/вывода,
который должен иметь методы read/write и
вызывать исключение IOError при ошибках чтения/записи.

DevAsync умеет не только передавать команды, а еще и асинхроннно
(в отдельном потоке) принимать команды, т.е позволяет
организовать работу как 'Главного' так и 'Подчиненного' устройства.

При приеме 'своей' команды, вызывается связанная с ней callback функция,
которая НЕ ДОЛЖНА блокировать поток DevAsync._thread.
Добавление входящих команд осуществляется методом add_incmd().
"""

import threading
from binascii import hexlify
from struct import unpack, calcsize
from .dev_master import DevMaster, CmdMaster, dump
from .dev_err import DevException, DevBadCode
from .protocol import Protocol


class DevAsync(DevMaster):
    """ Класс реализует работу как 'Главного' так и 'Подчиненного'.
    Основная работа идет в отдельном потоке. При приеме 'своей' команды, вызывается
    связанная ней callback функция, которая НЕ ДОЛЖНА блокировать этот поток.
    Связывание входящих команд и функций осуществляется методом add_incmd().
    """
    def __init__(self,
                 io,
                 addr=None,
                 remix=3,
                 timeout=0.1,
                 log=None,
                 rxtimeout=0.02):
        """ Конструктор класса DevAsync устройства.
        DevAsync наследуется от DevMaster, описание параметров смотрите там.
        """
        super().__init__(io, addr, timeout, remix, log)
        self._incmd_table = {}               # Таблицa входящих команд
        self._cmdlist = []                   # Список активных исходящих команд
        self._Exeption_io_thread = None      # Исключения потока обмена
        self._exit = False
        self._thread = None
        self._rxtimeout = rxtimeout
        self.set_io(io)
        self._prtcl_slave = None

    def set_io(self, io):
        """ Задать интерфейс ввода/вывода. Подробнее можно
        посмотреть в описании одноименного метода в родительском классе DevMaster.
        """
        self._thread_stop()
        self._io = io
        if io:
            self._thread_start()

    def set_protocol_tx(self, protocol):
        """Подключить расшифровщик обмена для ИСХОДЯЩИХ команд"""
        super().set_protocol(protocol)

    def set_protocol_rx(self, protocol):
        """Подключить расшифровщик обмена для ВХОДЯЩИХ команд"""
        assert (isinstance(protocol, Protocol))
        self._prtcl_slave = protocol

    def close(self):
        """ Закрыть устройство"""
        self._thread_stop()
        super().close()

    def add_incmd(self, code: bytes, datafrmt: str, callback, broadcast=False) -> None:
        """ Добавление входящей команды.

        :param code: код входящей команды.
        :param datafrmt: формат данных команды, смотрите в описании модуля 'struct',
                         https://docs.python.org/2/library/struct.html#format-characters
        :param callback: выполняемая функция при совпадения кода команды и размера данных
            в соответствии datafrmt.
        :param broadcast: допустимость выполнения команды при широковещательной рассылке.

        Связанная функция вызывается с тем кол-вом аргументов, которое указано в datafrmt.
        Если datafrmt='', то без аргументов. Если datafrmt='raw', то в функцию передается
        массив байт (сырые данные), их размер не контролируется.
        Связанная callback функция, должна возвращать данные в формате (bytes) при
        необходимости передать данные в ответ мастеру.
        Если передавать данные в ответ не нужно, должна возвращать b'' или True.
        Если команда 'недопустима' должна возвращать отрицательное число равное коду (причине)
        недостимости выполнения команды (в общем случаее BADCMD_EXECERR=-1) это значение
        будет передано мастеру по формату "недопустимая команда".
        """
        assert(type(code) is bytes and len(code) == 1)
        assert(type(datafrmt) is str)
        self._incmd_table[code[0]] = (callback, datafrmt, broadcast)

    def sendto(self, addr, msg, ackfrmt='raw', timeout=None, remix=None, safe=False):
        """ Передать команду подчиненному с адресом 'addr', если addr=BROADCAST, то
        команда широковещательная. Остальное аналогично send() в родительском DevMaster.
        """
        assert(msg and type(msg) is bytes)
        if not self._io:
            raise DevException(f"DevException '{self._name}'._io is None!")
        c = _CmdAsync(addr, msg, ackfrmt, self.log,
                      timeout if timeout is not None else self._timeout,
                      remix if remix is not None else self._remix,
                      self._prtcl)
        self._cmdlist.append(c)
        c.event_wait()
        self._cmdlist.remove(c)
        if type(c.ack) is DevBadCode:
            if safe:
                self.log.info(f"Safe '{self._name}' {c.name} badcode {c.ack}")
                return None
            raise DevException(f"DevException '{self._name}' {c.name} badcode", badcode=c.ack)
        if c.ack is None:
            if safe:
                self.log.info(f"Safe '{self._name}' {c.name} nack!")
                return None
            raise DevException(f"DevException '{self._name}' {c.name} nack!")
        if self._Exeption_io_thread:
            raise self._Exeption_io_thread
        return c.ack

    def _thread_start(self):
        if not self._thread:
            self._exit = False
            self._Exeption_io_thread = None
            self._thread = threading.Thread(target=self._io_thread)
            self._thread.start()

    def _thread_stop(self):
        if self._thread:
            self._exit = True
            self._thread.join()
            self._thread = None

    def _io_thread(self):
        """ Поток ввода/вывода и обработки команд"""
        # self.log.info('device io thread started')
        while not self._exit:
            try:
                rx = self._io.read(timeout=self._rxtimeout)
                # Обработака исходящих команд
                for c in self._cmdlist:
                    if c.is_alive():
                        # передаем команду, если пришло время очередной попытки
                        tx = c.check_tx()
                        if tx:
                            self._io.write(tx)
                        if c.check_rx(rx) is not None:
                            # Принятое сообщение - ответ на одну из команд
                            # исключаем его из последующей обработки
                            # и оповещаем функцию sendto() об ответе
                            rx = None
                            c.event_set()
                # Обработака входящиx команд
                if rx:
                    ack = self._incmd_parser(rx)
                    if ack:
                        self._io.write(ack)
            except IOError as e:
                self.log.error(f"device err read_process > {e}")
                self._Exeption_io_thread = e
                break
        # self.log.info('device io thread stoped')

    def _incmd_parser(self, rx):
        """ Обработака входящиx команд """
        msg = rx
        name = '['
        broadcast = False
        # Проверяем адрес, еще до поиска в таблице команд
        if self._addr:
            # сообщение является широковещятельным -> запоминаем (используем при поиске в таблице)
            if rx[0] == 0x00:
                broadcast = True
            # сообщение не широковещательное и адрес не совпадает -> выход
            elif self._addr[0] != rx[0]:
                return None
            # aдрес проверен, информация о нем уже не нужна -> откидываем
            name += f"{rx[0]:02x}:"
            rx = rx[1:]

        # В принятом сообщении установлена маска ответа 0х80 -> выход
        if not rx or rx[0] & 0x80:
            return None
        name += f"{rx[0]:02x}]"

        # Поиск и выполнение команды в таблице
        if rx[0] in self._incmd_table:
            func, frmt, boadrcast_available = self._incmd_table[rx[0]]

            # Сообщение широковещательное, но для данной команды это недопустимо
            if broadcast and not boadrcast_available:
                self.log.warning(f"<cmd{name}!boardcast")
                return None

            # Проверка размера входящего сообщения
            if frmt != 'raw':
                waitsize = 1 + calcsize(frmt) + len(self._addr)
                if len(msg) != waitsize:
                    self.log.warning(f"<cmd{name}!size{len(msg)} wait{waitsize}")
                    return self._addr + bytes([0xF0, rx[0], abs(DevBadCode.SIZEERR)])

            note = self._prtcl_slave.note(rx) if self._prtcl_slave else ""
            self.log.debug(f"<cmd{name}{note} [{dump(msg)}]")

            # Выполняем функцию "callback" команды
            if not frmt:
                ret = func()
            elif frmt == 'raw':
                ret = func(rx[1:])
            else:
                ret = func(*unpack(frmt, rx[1:]))

            # пасрим ответ функции
            ack = err = None
            if type(ret) is bytes:
                ack = self._addr + bytes([rx[0] | 0x80]) + ret
            # Truе - в ответ b''
            elif ret is True:
                ack = self._addr + bytes([rx[0] | 0x80])
            # код ошибки - отрицательная квитанция
            elif type(ret) is int and -256 < ret < 0:
                err = ret
            # ничего в ответ не передаем
            elif ret is None:
                return None
            # функция вернула непонятно что - отрицательная квитанция
            else:
                err = DevBadCode.EXECERR

            if err is not None:
                ack = self._addr + bytes([0xF0, rx[0], abs(err)])
                self.log.debug(f"<cmd{name}!exe{err} [{dump(msg)}]")

            if broadcast:
                return None
            else:
                note = self._prtcl_slave.note(ack) if self._prtcl_slave else ""
                self.log.debug(f">ack{name}{note} [{dump(ack)}]")
                return ack

        # нет такой команды в таблице -> команда недопустима
        self.log.warning(f"<cmd{name}?unknown [{dump(msg)}]")
        return self._addr + bytes([0xF0, rx[0], abs(DevBadCode.UNKNOWN)])


    def set_protocol_master(self, protocol):
        """ deprecated. use set_protocol_tx() """
        self.set_protocol_tx(protocol)

    def set_protocol_slave(self, protocol):
        """ deprecated. use set_protocol_rx() """
        self.set_protocol_rx(protocol)


class _CmdAsync(CmdMaster):
    """ Для Команд DevAsync дополнительно требуется 'семафор' """
    def __init__(self, addr, msg, ackfrmt, log, timeout, remix, prtcl):
        super().__init__(addr, msg, ackfrmt, log, timeout, remix, prtcl)
        self.event = threading.Event()

    def event_wait(self):
        # таймаут берем с запасом 0.3, событие по приему или таймауту в обработчике обязано случиться раньше
        self.event.wait(self.TIMEOUT * (self.REMIX+1) + 0.3)

    def event_set(self):
        self.event.set()
