"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-07-01
Author: Martian Bugs
Description: 数据采集器
"""

from BrowserAutomationLauncher import BrowserInitOptions, Launcher

from ._login import LoginUtils
from .datacenter.datacenter import DataCenter


class Collector:
    """采集器. 使用之前请先调用 `connect_browser` 方法连接浏览器."""

    def __init__(self):
        self._browser = None
        self._datacenter = None
        self._login = None

        self._browser_launcher = Launcher()

    def connect_browser(self, port: int):
        """
        连接浏览器

        Args:
            port: 浏览器调试端口号
        """

        browser_options = BrowserInitOptions()
        browser_options.set_basic_options(port=port)
        browser_options.set_window_loc(width=1400, height=900)

        self._browser = self._browser_launcher.init_browser(browser_options)

    @property
    def login(self):
        """登录工具集"""

        if not self._login:
            self._login = LoginUtils(self._browser)

        return self._login

    @property
    def datacenter(self):
        """数据中心数据采集"""

        if not self._datacenter:
            self._datacenter = DataCenter(self._browser)

        return self._datacenter
