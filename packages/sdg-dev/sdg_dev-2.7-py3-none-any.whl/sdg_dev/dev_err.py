"""
DevMaster и DevAsync генерируют исключение DevException, если:
-подчиненное устройство не отвечает на команду;
-принят ответ подчиненного "недопустимая команда";
-при ошибке ввода/вывода (перехватывается IOError);
"""


class DevException(Exception):
    """ОШИБКА ОБМЕНА"""
    def __init__(self, val, badcode=None):
        self.val = val
        self.badcode = badcode  # недопустимая команда

    def __str__(self):
        badcode_ts = f"{self.badcode}" if self.badcode else ""
        return f"{self.val} {badcode_ts}"

    def get_badcode(self):
        return self.badcode.val if self.badcode else 0


class DevBadCode:
    """ коды ошибок недопустимых команд """
    EXECERR = -1  # неопределенная ошибка выполнения функции входящей команды
    UNKNOWN = -2  # неизвестная команда (отсутствует в списке входящих команд)
    SIZEERR = -3  # неправильный размер команды (в списке входящих команд, другой размер)

    # todo: коды ниже индивидуальны для проекта, нужен механизм добавления своих кодов, а пока так.
    MODEERR = -4  # недопустима в текужем режиме работы
    PARAMERR = -6  # недопустимые параметры

    codes = {abs(EXECERR): 'bad_exec',
             abs(UNKNOWN): 'cmd_unknown',
             abs(SIZEERR): 'bad_size',
             abs(MODEERR): 'bad_mode',
             abs(PARAMERR): 'bad_param'}

    def __init__(self, badcode):
        self.val = badcode

    def __str__(self):
        ts = self.codes.get(abs(self.val), "badcode")
        return f"{ts}{self.val}"
