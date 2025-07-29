
import colorama
import os
import sys
if os.name == "nt":
    import msvcrt
    import ctypes
elif os.name == 'posix':
    import tty
    import select
    import termios

__STD_INPUT_HANDLE = -10
__STD_OUTPUT_HANDLE = -11
__ENABLE_INSERT_MODE = 0x0020  # https://docs.microsoft.com/en-us/windows/console/getconsolemode
__ENABLE_QUICK_EDIT_MODE = 0x0040
__light_theme = False


def terminal_init(fontsize=None, size=None, light_theme=False, cursor=True, clear=True, mouse_edit=False):
    global __light_theme
    __light_theme = light_theme
    colorama.init()
    if os.name == "nt":
        os.system('Color f0' if __light_theme else 'Color 07')
    if fontsize:
        terminal_set_fontsize(fontsize)
    if size:
        terminal_set_size(w=size[0], h=size[1])
    if mouse_edit:
        terminal_mouse_edit_on()
    else:
        terminal_mouse_edit_off()
    if cursor:
        terminal_cursor_hide()
    else:
        terminal_cursor_show()
    if clear:
        terminal_clear()


def terminal_beep():
    sys.stdout.write('\a')
    sys.stdout.flush()


def terminal_clear():
    os.system('cls' if os.name == "nt" else 'clear')


def terminal_color(color='default'):
    if __light_theme:
        colors = {"black": colorama.Fore.BLACK,
                  "red": colorama.Fore.LIGHTRED_EX,
                  "green": colorama.Fore.LIGHTGREEN_EX,
                  "yellow": colorama.Fore.YELLOW,
                  "blue": colorama.Fore.BLUE,
                  "magenta": colorama.Fore.MAGENTA,
                  "cyan": colorama.Fore.CYAN,
                  "white": colorama.Fore.WHITE,
                  "soft": colorama.Fore.WHITE,
                  "back": colorama.Fore.LIGHTWHITE_EX,
                  }
        back = colorama.Back.LIGHTWHITE_EX
        fore = colors.get(color, colorama.Fore.BLACK)
    else:
        colors = {"black": colorama.Fore.LIGHTBLACK_EX,
                  "red": colorama.Fore.RED,
                  "green": colorama.Fore.GREEN,
                  "yellow": colorama.Fore.YELLOW,
                  "blue": colorama.Fore.LIGHTBLUE_EX,
                  "magenta": colorama.Fore.LIGHTMAGENTA_EX,
                  "cyan": colorama.Fore.CYAN,
                  "white": colorama.Fore.WHITE,
                  "soft": colorama.Fore.LIGHTBLACK_EX,
                  "back": colorama.Fore.BLACK,
                  }
        back = colorama.Back.BLACK
        fore = colors.get(color, colorama.Fore.WHITE)
    return colorama.Style.NORMAL + back + fore


def terminal_puts(s="", color="default"):
    print(terminal_color(color) + s)


def terminal_set_size(w, h):
    if os.name == "nt":
        # устанавливается и размер окна и размер буфера
        os.system('mode con cols=%d lines=%d' % (w, h))
        # меняем размер буфера
        coord = ctypes.wintypes._COORD(w, 9000)  # rows, columns
        h = ctypes.windll.kernel32.GetStdHandle(__STD_OUTPUT_HANDLE)
        if 0 == ctypes.windll.kernel32.SetConsoleScreenBufferSize(h, coord):
            print("ERROR SetConsoleScreenBufferSize", ctypes.windll.kernel32.GetLastError())


def terminal_set_fontsize(fontsize=20):
    if os.name == "nt":
        def __get_current_console_font_ex():
            class ConsoleFontInfoEx(ctypes.Structure):
                LF_FACESIZE = 32
                _fields_ = [("cbSize", ctypes.c_ulong),
                            ("nFont", ctypes.c_ulong),
                            ("dwFontSize", ctypes.wintypes._COORD),
                            ("FontFamily", ctypes.c_uint),
                            ("FontWeight", ctypes.c_uint),
                            ("FaceName", ctypes.c_wchar * LF_FACESIZE)]

            font_ex = ConsoleFontInfoEx()
            font_ex.cbSize = ctypes.sizeof(ConsoleFontInfoEx)
            h = ctypes.windll.kernel32.GetStdHandle(__STD_OUTPUT_HANDLE)
            ctypes.windll.kernel32.GetCurrentConsoleFontEx(
                h, ctypes.c_long(False), ctypes.pointer(font_ex))
            return font_ex

        def __set_current_console_font_ex(fontEx):
            h = ctypes.windll.kernel32.GetStdHandle(__STD_OUTPUT_HANDLE)
            ctypes.windll.kernel32.SetCurrentConsoleFontEx(
                h, ctypes.c_long(False), ctypes.pointer(fontEx))

        # try:  # fontsize- windows vista or later
        font_ex = __get_current_console_font_ex()
        font_ex.nFont = 0
        font_ex.dwFontSize.X = 10
        font_ex.dwFontSize.Y = fontsize
        font_ex.FontFamily = 54
        font_ex.FontWeight = 400
        font_ex.FaceName = 'Consolas'
        __set_current_console_font_ex(font_ex)
        # except:
        #     self.puts('this version OS does not support font size setting')


def terminal_mouse_edit_off():
    if os.name == "nt":
        h = ctypes.windll.kernel32.GetStdHandle(__STD_INPUT_HANDLE)
        mode = ctypes.c_ulong(0)
        ctypes.windll.kernel32.GetConsoleMode(h, ctypes.pointer(mode))
        mode.value &= ~(__ENABLE_QUICK_EDIT_MODE | __ENABLE_INSERT_MODE)
        ctypes.windll.kernel32.SetConsoleMode(h, mode)


def terminal_mouse_edit_on():
    if os.name == "nt":
        h = ctypes.windll.kernel32.GetStdHandle(__STD_INPUT_HANDLE)
        mode = ctypes.c_ulong(0)
        ctypes.windll.kernel32.GetConsoleMode(h, ctypes.pointer(mode))
        mode.value |= (__ENABLE_QUICK_EDIT_MODE | __ENABLE_INSERT_MODE)
        ctypes.windll.kernel32.SetConsoleMode(h, mode)


class _CursorInfo(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int),
                ("visible", ctypes.c_byte)]


def terminal_cursor_hide():
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()


def terminal_cursor_show():
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


def terminal_getc():
    if "func" not in terminal_getc.__dict__:
        if os.name == 'nt':
            terminal_getc.func_ = msvcrt.getwch
        elif os.name == 'posix':
            def _tty_read():
                fd = sys.stdin.fileno()
                settings = termios.tcgetattr(fd)
                try:
                    tty.setcbreak(fd)
                    answer = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, settings)
                return answer

            terminal_getc.func_ = _tty_read
    return terminal_getc.func_()


def terminal_kbhit():
    if "func_" not in terminal_kbhit.__dict__:
        if os.name == 'nt':
            terminal_kbhit.func_ = msvcrt.kbhit
        elif os.name == 'posix':
            def _kbhit():
                return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

            terminal_kbhit.func_ = _kbhit
    return terminal_kbhit.func_()
