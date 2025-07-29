import sys
import win32con
import win32gui

from haige_pyqt.straper.guard import SingleApplicationGuard

WM_ACTIVATE_SELF_WINDOW_MESSAGE = win32con.WM_USER + 100


class ApplicationRunningManager:

    def __init__(self, app_id):
        self.single_app_lock = SingleApplicationGuard(app_id)

    def run(self, m_win_hwnd):
        if self.single_app_lock.is_used():
            self._active_started_app_window()
            sys.exit(0)
        self._set_main_win_hwndId(m_win_hwnd)

    def _set_main_win_hwndId(self, hwnd_id):
        self.single_app_lock.set_data(str(hwnd_id).encode('utf-8'))

    def _active_started_app_window(self):
        d_bts = self.single_app_lock.get_data().decode('utf-8')
        if d_bts + "" != "":
            hwnd = int(d_bts)
            win32gui.SendMessage(hwnd, WM_ACTIVATE_SELF_WINDOW_MESSAGE, 0, 0)
