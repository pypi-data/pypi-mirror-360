"""
Created on 7 ноября. 2019 г.

@author: chernecov
"""


""" адрес широковещательной команды """
BROADCAST = b'\x00'


class DevBadCode:
    """ коды ошибок недопустимых команд """
    EXECERR = -1  # неопределенная ошибка выполнения функции входящей команды
    UNCNOWN = -2  # неизвестная команда (отсутствует в списке входящих команд)
    SIZEERR = -3  # неправильный размер команды (в списке входящих команд, другой размер)

    def __init__(self, badcode):
        self.val = badcode

    def __str__(self):
        names = {abs(self.EXECERR): 'bad_exec',
                 abs(self.UNCNOWN): 'cmd_unknown',
                 abs(self.SIZEERR): 'bad_size'}
        ts = names.get(abs(self.val), "bad_other")
        return f"badcode{self.val} '{ts}'"


class DevException(Exception):
    """ОШИБКА ОБМЕНА"""
    """ DevMaster и DevAsync генерируют исключение DevException, если:
    -подчиненное устройство не отвечает на команду;
    -принят ответ подчиненного "недопустимая команда";
    -при ошибке ввода/вывода (перехватывается IOError);
    """
    def __init__(self, val, badcode=None):
        self.val = val
        self.badcode = badcode  # недопустимая команда

    def __str__(self):
        badcode_ts = f"{self.badcode}" if self.badcode else ""
        return f"{self.val} {badcode_ts}"

    def get_badcode(self):
        return self.badcode.val if self.badcode else 0

