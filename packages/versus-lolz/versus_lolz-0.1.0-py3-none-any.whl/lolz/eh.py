import os
import sys
from types import TracebackType
import colorama as cr


__all__ = ["hook"]

LIBRARY_PATH = os.path.dirname(os.path.abspath(__file__))

NO_COLOR = os.getenv('PY_DOTEST_NO_COLOR') == '1'

orig_eh = sys.excepthook

if not NO_COLOR:
    cr.init()


def eh(type: type[BaseException], val: BaseException, tb: TracebackType | None) -> object:
    """
    Truncates traceback by removing frames from the current library
    
    :param exc_type: Exception type
    :param exc_value: Exception value
    :param exc_traceback: Original traceback
    :return: Formatted traceback string
    """

    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

    orig_eh(type, val, tb)

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    if not NO_COLOR:
        print(cr.Style.BRIGHT + cr.Fore.RED, end='')

    print("\nTraceback (most recent call last):\n")

    if not NO_COLOR:
        print(cr.Style.RESET_ALL, end='')
    
    while tb:
        filename = tb.tb_frame.f_code.co_filename
        
        if filename.startswith(LIBRARY_PATH) or 'debugpy' in filename or 'runpy' in filename or \
        (os.getenv('PY_DOTEST_SKIP_TB') == '1' and filename.endswith('dotest.py')):
            tb = tb.tb_next
            continue

        pretty_filename = os.path.relpath(filename, os.getcwd())
        
        if not NO_COLOR:
            print(cr.Style.BRIGHT + cr.Fore.LIGHTBLUE_EX, end='')

        print(f"  File \"{pretty_filename}\", line {tb.tb_lineno}, in {tb.tb_frame.f_code.co_name}")

        if not NO_COLOR:
            print(cr.Style.RESET_ALL, end='')

        lineno = tb.tb_lineno

        slno = str(lineno)

        slno = ' ' * (8 - len(slno)) + slno + ' |'

        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
                context = lines[lineno-1].strip()
                print(slno + context)
        except Exception:
            print(slno + f" [Unable to read file {filename}]")
    
        print()
        tb = tb.tb_next

    # print exception type and value
    print(f"{cr.Style.BRIGHT+cr.Fore.LIGHTMAGENTA_EX if not NO_COLOR else ''}\n"
          f"{type.__name__}{cr.Style.RESET_ALL if not NO_COLOR else ''}: {val}")


def hook():
    sys.excepthook = eh
