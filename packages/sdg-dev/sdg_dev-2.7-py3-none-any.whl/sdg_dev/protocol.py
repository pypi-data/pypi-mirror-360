from struct import unpack, error
from sdg_utils import dump_bytes


class Protocol:
    """ Парсер протоколов обмена"""
    def __init__(self, cmds, addr: int = None, name='', frmt="{}"):
        assert(type(addr) == int or addr is None)
        self._dict = {addr: (name, cmds)}
        self.frmt = frmt

    def __add__(self, other):
        """ Сложение протоколов. Сложить адресный и безадресный нельзя! """
        assert(isinstance(other, Protocol))
        assert(self.is_with_addr() == other.is_with_addr())
        if self.is_with_addr():
            self._dict.update(other._dict)
        else:  # {addr=None: (name='', cmds={dict})}
            self._dict[None][1].update(other._dict[None][1])
        return self

    def is_with_addr(self):
        """ Протокол адресный если в ключах словаря не None """
        return None not in self._dict.keys()

    def note(self, msg: bytes) -> str:
        """ Получение описания команды 'msg' в соответствии с протоколом обмена """
        assert(isinstance(msg, bytes))
        try:
            if self.is_with_addr():
                addr, code, data = msg[0], msg[1], msg[2:]
            else:
                addr, code, data = None, msg[0], msg[1:]
        except IndexError:
            return ''  # f"msg is short {dump_bytes(msg)}"
        # Проверка совпадения адреса входящего собщения
        if addr in self._dict:
            name, cmds = self._dict[addr]
            m = f" {name} {self._parse_my_cmd(code, data, cmds)}".lstrip()
            return self.frmt.format(m)
        return ''

    def _parse_my_cmd(self, code, data, cmds):
        """ Получение описания команды из таблицы протокола 'cmds' """

        def _frmt_msg(note, frmt, data):
            """Форматирование строки"""
            try:
                vals = unpack(frmt, data)
                note = note.format(*vals)
            except error as e:
                note = f"{note} [Error unpack data. {e}]"
            except (IndexError, ValueError, KeyError) as e:
                note = f"{note} [Error note format. {e}]"
            return note

        def _exec_func(func, frmt, data):
            """Попытка выполнения функции"""
            try:
                if frmt == 'raw':
                    return func(data)
                try:
                    data = unpack(frmt, data)
                    return func(*data)
                except (error, UnicodeEncodeError) as e:
                    return f"[Error unpack func(data). {e}]"
                    # UnicodeEncodeError - вылез когда формат написал русскими буквами O_o
            except TypeError as e:
                return f"[Error exec func(). {e}]"

        # Команда описана в протоколе обмена?
        if code in cmds:
            try:
                frmt, argv = cmds[code]
            except (ValueError, IndexError) as e:
                return f"[Error {self.__class__.__name__}.cmds format: {e}]"
            else:
                # argv - может содержать форматную строку
                if isinstance(argv, str):
                    return _frmt_msg(argv, frmt, data)
                # или функцию
                return _exec_func(argv, frmt, data)

        # Команда с таким кодом не описана в протоколе
        return f"[Uncknown cmd{code:02x}]"


if __name__ == '__main__':
    class TempPrtcl(Protocol):
        def __init__(self, addr=None, name=''):
            cmds = {
                0x00: ('B', "Команда"),
                0x01: ('B', self.cmdfunc1),
                0x02: ('BB', self.cmdfunc2),
                0x03: ('raw', self.cmdfunc3),
                0x04: ('raw', self.cmdfunc4),
                0x05: ('', self.cmdfunc5),
            }
            super().__init__(cmds, addr, name)

        def cmdfunc1(self, b1):
            return f"cmdfunc1 {b1}"

        def cmdfunc2(self, b1, b2):
            return f"cmdfunc2 {b1}-{b2}"

        def cmdfunc3(self, data):
            return f"cmdfunc3 {dump_bytes(data)}"

        def cmdfunc4(self):
            return f"cmdfunc4"

        def cmdfunc5(self):
            return f"cmdfunc5"

    addr = None
    # addr = 0x55
    tp = TempPrtcl(addr=addr, name="ololo")
    data = (
        b'',
        b'\x55',
        b'\x00\x03',
        b'\x01\x04',
        b'\x02\x06\x07',
        b'\x02\x03',
        b'\x02',
        b'\x03\x01\x02\x03\x03\x03\x03\x03',
        b'\x03',
        b'\x04\x03',
        b'\x05',
        b'\x05\x03',
    )

    for d in data:
        d = (bytes([addr]) + d) if addr else d
        # print(dump_bytes(d))
        ts = tp.note(d)
        if ts:
            print(ts)
    exit()
