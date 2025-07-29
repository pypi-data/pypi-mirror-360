"""
数据中心模块
"""

from BrowserAutomationLauncher import Browser

from .live import Live


class DataCenter:
    def __init__(self, browser: Browser):
        self._live = None

        self._browser = browser

    @property
    def live(self):
        """直播数据采集"""

        if not self._live:
            self._live = Live(self._browser)

        return self._live
