"""
SDG UTILS.
"""

__version__ = '1.5'

import re
import random
import datetime
import inspect
from .terminal import *
from .log import *
from serial.tools.list_ports import comports  # это pyserial!
from binascii import hexlify


def funcname():
    return inspect.stack()[1][3]


def safe_repr(obj, short=False):
    _MAX_LENGTH = 80
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < _MAX_LENGTH:
        return result
    return result[:_MAX_LENGTH] + ' [truncated]...'


def rm_redurant_spaces(s):
    """Удалить лишние пробелы"""
    return re.sub(r' +', ' ', s)


def rand_bytes(size=None, mtu=256):
    """
    Генерирует случайный пакет байт размера size.
    если size не задан, то размер случайный, но не более mtu.
    """
    if not size:
        assert(mtu > 0)
        size = random.randint(1, mtu)
    return bytes(random.randrange(255) for _ in range(size))


def dump_bytes(msg=b''):
    """
    Человеко читаемое представление пакета байт
    print(dump_msg(b'012345') > (6){30,31,32,33,34,35}
    """
    assert(type(msg) is bytes)
    return "" if not msg else "(%d){%s}" % (len(msg), repr(hexlify(msg, ',', 1))[2:-1])
    # return f"({len(msg)}){{{','.join(f'{i:02x}' for i in msg)}}}" if msg else ""


def bytes2srt(msg=b''):
    return ','.join('%02x' % i for i in msg).replace("'", "")


def dump_bits(bitsmask: int, shift=0) -> str:
    """
    Выводит строку с номерами установленных битов в числе 'bitsmask', через запятую.
    Например dump_bits(0x8080) --> '7,15'
    Параметр 'shift' позволяет начать отсчет битов с произвольного значения.
    Например dump_bits(0x8080, shift=1) --> '8,16'
    """
    # Таже фигня что и return ','.join(i for i in bits2nums(bitsmask)) только шустрее
    return ','.join([str(i + shift) for i in range(bitsmask.bit_length()) if bitsmask & 1 << i])


def bits2nums(bitsmask: int, shift=0) -> list:
    """
    Возвращает список с номерами установленных битов в числе 'bitsmask'.
    Например bits2nums(0x8080) --> [7, 15].
    Параметр 'shift' позволяет начать отсчет битов с произвольного значения.
    Например bits2nums(0x8080, shift=1) --> [8, 16]
    """
    return [i + shift for i in range(bitsmask.bit_length()) if bitsmask & 1 << i]


def nums2bits(*bits, shift=0):
    """
    Возвращает битовую маску с установленными битами из списка 'bits'
    Например nums2bits(7, 15) --> 0x8080.
    Параметр 'shift' позволяет сдвинуть биты на произвольное значение.
    Например nums2bits(8, 16, shift=-1) --> 0x8080.
    """
    bitmask = 0
    for b in bits:
        bitmask |= 1 << b + shift
    return bitmask


def get_comports(vidpid='', bluetooth_ports_filter=True):
    """ Возвращает список кортежей (порт, имя, hwid) доступных последовательных портов
    [ ('COM1', 'Последовательный порт 1, id), ('COM5','USB Serial Port', id), ... ]
    по умолчанию с фильтрацией Bluetooth портов, тк они в системе присутствуют
    даже когда соединение с Bluetooth устройством не установлено
    и при попытке открыть такой порт происходит 'мертвая говядина'. """

    def it_bluetooth(port_name):
        for bt_name in ["luetooth", "BT Port"]:
            if port_name.find(bt_name) != -1:
                return True
    ports = []
    for port, portname, hwid in comports():
        if sys.version_info < (3, 7):  # замена "невыводимых" символов на?
            portname = portname.encode(sys.stdout.encoding, errors='replace')
            portname = portname.decode(sys.stdout.encoding)
        if bluetooth_ports_filter and it_bluetooth(portname):
            continue

        if not vidpid:
            ports.append((port, portname, hwid))
            continue
        if type(vidpid) is str:
            vidpid = (vidpid, )
        for i in vidpid:
            if i in hwid:
                ports.append((port, portname, hwid))
    return sorted(ports)


def try_mkdir(path):
    """ Попытка создать каталог по пути path """
    try:
        os.makedirs(path)
    except FileExistsError:
        pass


def get_datetime() -> str:
    """ Возвращает строку с текущей датой временем в формате 2020.02.04_09.52.420 """
    return datetime.datetime.today().strftime('%Y.%m.%d_%H.%M.%S%f')[:-5]


def align(data, alignlen=4, filling=b'\xff'):
    """ Выравнивание массива байт с заполнением filling"""
    if len(data) & (alignlen-1):
        data += filling * (alignlen - (len(data) & (alignlen-1)))
    return data


def rus2eng(key):
    return {'Й': 'Q', 'й': 'q',
            'Ц': 'W', 'ц': 'w',
            'У': 'E', 'у': 'e',
            'К': 'R', 'к': 'r',
            'Е': 'T', 'е': 't',
            'Н': 'Y', 'н': 'y',
            'Г': 'U', 'г': 'u',
            'Ш': 'I', 'ш': 'i',
            'Щ': 'O', 'щ': 'o',
            'З': 'P', 'з': 'p',
            'Х': '[', 'х': '[',
            'Ъ': ']', 'ъ': ']',
            'Ф': 'A', 'ф': 'a',
            'Ы': 'S', 'ы': 's',
            'В': 'D', 'в': 'd',
            'А': 'F', 'а': 'f',
            'П': 'G', 'п': 'g',
            'Р': 'H', 'р': 'h',
            'О': 'J', 'о': 'j',
            'Л': 'K', 'л': 'k',
            'Д': 'L', 'д': 'l',
            'Ж': ';', 'ж': ';',
            'Э': "'", 'э': "'",
            'Я': 'Z', 'я': 'z',
            'Ч': 'X', 'ч': 'x',
            'С': 'C', 'с': 'c',
            'М': 'V', 'м': 'v',
            'И': 'B', 'и': 'b',
            'Т': 'N', 'т': 'n',
            'Ь': 'M', 'ь': 'm',
            'Б': ',', 'б': ',',
            'Ю': '.', 'ю': '.',
            '.': '/',
            'Ё': '`', 'ё': '`',
            }.get(key) or key

