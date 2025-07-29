from ctypes import wintypes

from haige_pyqt.straper.manager import WM_ACTIVATE_SELF_WINDOW_MESSAGE


def is_activate_window_message(message) -> bool:
    try:
        return wintypes.MSG.from_address(message.__int__()).message == WM_ACTIVATE_SELF_WINDOW_MESSAGE
    except:
        return False
