import os
import sys


def _get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    elif __file__:
        return os.path.dirname(sys.argv[0])


App_Root = _get_app_dir()
App_Data = App_Root + "/dat"

if not os.path.exists(App_Data):
    os.mkdir(App_Data)
