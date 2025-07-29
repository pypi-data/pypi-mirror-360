"""
Cодержит классы **SdgDevMaster** и **SdgDevAsync** для обмена командами, через
СКБ-шный интерфейс ввода/вывода. https://pypi.org/project/sdg-io/

`SdgDevMaster` умеет только передавать команды, т.е. выполняет работу `Главного устройства`.

`SdgDevAsync` предназначен как для передачи так и для приема команд, т.е позволяет
организовать работу как `Главного` так и `Подчиненного устройства`.
Для работы SdgDevAsync создается поток, в котором выполняется переодическое
чтение данных из интерфейса ввода/вывода и их обработка на предмет получения команд.
Входящие команды должны быть заранее добавлены методом `add_incmd()` с указанием кода команды,
форматом ожидаемых данных и callback функции, которой будет передано управление при
поступлении команды с нужным кодом и форматом данных.
`Внимание` callback функция вызывается из внутреннего потока SdgDevAsync и не должна его
блокировать! Для безопасного обмена данными должны быть приняты меры!

`SdgDevMaster` и `SdgDevAsync` могут автоматически определять порт к которому подключено
подчиненное устройство. Для этого нужно:
1. Переопределить функцию `check_id()`, которая будет запрашивать `уникальный идентификатор`
у `подчиненного` и при получении адекватного ответа, возвращать True.
2. Использовать ф-ю `search_port()` для поиска `подчиненного` по всем доступным портам системы,
или search_port(portlist) для поиска по заранее подготовленному списоку портов.

При необходимости подключить какой-то другой интерфейс ввода/вывода нужно
использовать классы **DevMaster** и **DevAsync**.
Интерфейс ввода/вывода должен иметь методы `read/write` и вызывать
исключение `IOError` при ошибках чтения/записи.

Формат обмена:
-------------
`АА СС D0 D1 .. DX` - команда
`AA CA D0 D1 .. DX` - ответ
* `АА`: адрес устройства. Возможна работа без адреса (точка -точка).
* `СС`: код команды, любой в диапазоне 0x00 - 0x7F, кроме 0x70
* `CA`: код ответа = код команды с установленным старшим битом 0x80 - 0xFF, кроме 0xF0
* `D0-DX`: данные команды/ответа опционально.
На широковещательные команды с адресом `АА=0х00` ответ подчиненным(и) не выдается.
Возможен ответ подчиненного с кодом `0xF0` `Недопустимая команда` это означает,
что он не смог выполнить данныую команду. Формат такого ответа:
`AA 0xF0 CC EE`, где `EE` - код ошибки выполнения. (см. class DevBadCode)

Пример использования (example.py):
-------------
"""

__version__ = '2.7'

import logging
from sdg_io import SdgIO
from sdg_utils import get_comports
from .dev_err import DevException, DevBadCode
from .dev_master import DevMaster, BROADCAST
from .dev_async import DevAsync
from .protocol import Protocol


class _ForSeachPort:
    """Дополнительный класс для реализации автопоиска порта в SdgDevMaster или SdgDevAsync"""
    def __init__(self):  # pep8 warning if use no init values
        self._port = self.log = self._io = self.set_io = self._dump = self._portcfg = None

    def check_id(self) -> bool:
        """" Эта функция должна быть переопределена в наследнике SdgDevMaster или SdgDevAsync.
        Используется для поиска порта. Запрашивает 'уникальный идентификатор' у 'подчиненного'
         и должна возвращать 'True' при его совпадении с ожидаемым. Например:
        return True if 0x55 == self.send(b'\x00', ackfrmt='B')[0] else False """
        self.log.warning('This is default check_id function!')
        return False

    def search_port(self, vidpid='', portlist=None) -> str:
        """ Поиск порта (на котором сидит подчиненное устройство) по списку портов.
        Реализован на функции запроса уникального идентификатора check_id() у
        подчиненного. Поиск осуществляется пока с какого-то порта не получим 'нужный' id.

        :param vidpid: Если задан, поиск осуществляется только для портов с указанным VID:PID
                Например: vidpid='VID:PID=0483:3752' так же можно передать список
                vidpid=('VID:PID=0483:3752', '0403:6001')
        :param portlist: если portlist не задан, поиск по списку всех доступных портов
                системы, за исключением портов bluetooth т.к. они могут виснуть.
        :return: 'порт' на котором подчиненное было найдено, иначе '' пустую строку.
        """
        def _do_check_id():
            try:
                if self.check_id():
                    self.log.info(f"Порт {self.__class__.__name__} найден {self._port}.")
                    return True
            except DevException:
                return False

        # Если io уже открыт, первым делом проверяем его
        if self._io and _do_check_id():
            return self._port
        # Поиск (пытаемся получить внятный ответ подчиненного перебирая все доступные порты)
        portlist = portlist or get_comports()
        self.log.info(f"Поиск порта. {vidpid}")
        for p in portlist:
            self._port, portname, pid = p[0], p[1] if p[1] else str(p[0]), p[2]
            skip_port = False
            if vidpid:
                skip_port = True
                if type(vidpid) is str:
                    vidpid = (vidpid,)
                for i in vidpid:
                    if i in pid:
                        skip_port = False
            if skip_port:
                self.log.info(f"- {self._port:6} Пропуск    {portname}'")
                continue
            try:
                io = SdgIO(self._port, self._portcfg, dump=self._dump)
            except IOError:
                self.log.info(f"! {self._port:6} Недоступен {portname}' ")
            else:
                self.log.info(f"+ {self._port:6} Проверка   {portname}' ")
                self.set_io(io)
                if _do_check_id():
                    return self._port
                self.set_io(None)
                io.close()
        self.log.error(f"Порт '{self.__class__.__name__}' не найден.")
        return ''


class SdgDevMaster(DevMaster, _ForSeachPort):
    """ Класс реализует работу 'Главного' на 'SdgIO' (СКБ-шном интерфейсе
      ввода/вывода), с возможностью автопоиска 'последовательного порта'.
    """
    def __init__(self,
                 port: str = '',
                 portcfg='115200_O_2',
                 addr=None,
                 timeout=.1,
                 remix=3,
                 log=None,
                 dump=None):
        self.log = log or logging.getLogger(self.__class__.__name__)
        self._dump = dump
        self._portcfg = portcfg
        self._port = port
        io = None
        if port:
            try:
                io = SdgIO(port, portcfg, dump=dump)
            except IOError:
                self.log.warning(f"Порт недоступен '{port}'")
        super().__init__(io, addr, timeout, remix, self.log)

    def close(self):
        super().close()
        if self._io:
            self._io.close()


class SdgDevAsync(DevAsync, _ForSeachPort):
    """ Класс реализует работу 'Главного' и/или 'Подчиненного' на 'SdgIO'
     (СКБ-шном интерфейсе ввода/вывода), с возможностью автопоиска порта.
    """
    def __init__(self,
                 port: str = '',
                 portcfg='115200_O_2',
                 addr=None,
                 timeout=.1,
                 remix=3,
                 log=None,
                 dump=None):
        self.log = log or logging.getLogger(self.__class__.__name__)
        self._dump = dump
        self._portcfg = portcfg
        self._port = port
        try:
            io = SdgIO(port, portcfg, dump=dump)
        except IOError:
            io = None
            self.log.warning("порт недоступен '%s'" % port)
        super().__init__(io, addr, remix, timeout, self.log)

    def close(self):
        super().close()
        if self._io:
            self._io.close()
