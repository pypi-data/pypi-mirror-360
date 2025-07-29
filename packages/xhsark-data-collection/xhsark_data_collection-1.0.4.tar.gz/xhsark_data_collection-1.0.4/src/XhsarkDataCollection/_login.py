"""
账号登录工具集
"""

from contextlib import suppress
from time import sleep
from typing import Callable

from BrowserAutomationLauncher import Browser
from DrissionPage._pages.mix_tab import MixTab


class Urls:
    home = 'https://ark.xiaohongshu.com/app-system/home'


class DataPacketUrls:
    seller_info = 'https://ark.xiaohongshu.com/api/edith/seller/info/v2'


class LoginUtils:
    def __init__(self, browser: Browser):
        self._browser = browser

    def __wait__seller_info_datapacket(self, page: MixTab, func: Callable):
        """等待用户信息数据包"""

        page.listen.start(
            targets=DataPacketUrls.seller_info, method='GET', res_type='XHR'
        )
        func()
        datapacket = page.listen.wait(timeout=12)
        if not datapacket:
            raise TimeoutError('用户信息数据包获取超时, 可能接口发生变更')

        return datapacket

    def by_cookie(
        self,
        cookie: list[dict],
        local_storage: dict = None,
        session_storage: dict = None,
        clear_before=False,
    ):
        """
        通过 Cookie 登录

        Args:
            clear_before: 是否再登录之前清除本地信息
        """

        page = self._browser.chromium.latest_tab

        with suppress(TimeoutError):
            # 即使数据包获取超时也尝试设置 cookie
            datapacket = self.__wait__seller_info_datapacket(
                page, lambda: page.get(Urls.home)
            )
            # 如果未登录, status_code 为 401
            if datapacket.response.status == 200:
                return

        if clear_before is True:
            page.clear_cache(
                session_storage=True, local_storage=True, cookies=True, cache=True
            )
            sleep(0.5)

        page.set.cookies(cookie)

        if isinstance(local_storage, dict):
            for key, value in local_storage.items():
                page.set.local_storage(key, value)

        if isinstance(session_storage, dict):
            for key, value in session_storage.items():
                page.set.session_storage(key, value)

        sleep(0.5)
        datapacket = self.__wait__seller_info_datapacket(page, lambda: page.refresh())
        if datapacket.response.status == 401:
            raise RuntimeError('账号登录失败')

        return datapacket.response.body
