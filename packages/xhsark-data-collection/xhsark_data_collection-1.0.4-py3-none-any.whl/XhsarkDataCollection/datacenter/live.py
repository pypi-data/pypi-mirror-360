"""
数据中心-直播
"""

from enum import Enum
from os import path
from tempfile import gettempdir
from typing import Callable

from BrowserAutomationLauncher import Browser, DataPacketProcessor
from BrowserAutomationLauncher._utils.tools import DictUtils, OsTools
from DrissionPage._pages.mix_tab import MixTab

from ._utils import pick__daterange


class Urls:
    live_list = 'https://ark.xiaohongshu.com/app-datacenter/live-list'


class DataPacketUrls:
    data_query_base = 'https://ark.xiaohongshu.com/api/edith/butterfly/data'
    """数据查询统一接口, 通过 type 参数区分查询的数据"""
    download_task = 'https://ark.xiaohongshu.com/api/edith/long_task/task/detail'
    """下载任务接口"""


class DataPacketType(Enum):
    LIVE_LIST_DETAIL = 'sellerLiveDetailData'
    """直播间详情列表"""


class Live:
    def __init__(self, browser: Browser):
        self._browser = browser
        self._timeout = 15

    def _wait__data_query(
        self, page: MixTab, data_type: str, func: Callable, timeout: float = None
    ):
        """
        等待统一数据查询接口数据包返回

        Args:
            page: 操作的页面对象
            data_type: 查询的数据类型
            func: 数据捕获之前需要执行的方法
            timeout: 超时时间
        """

        _timeout = timeout if isinstance(timeout, (float, int)) else self._timeout

        page.listen.start(
            targets=DataPacketUrls.data_query_base, method='POST', res_type='XHR'
        )
        func()
        target__data_packet = None
        for packet in page.listen.steps(timeout=_timeout):
            req_params = packet.request.params
            if req_params.get('type') != data_type:
                continue

            target__data_packet = packet
            break

        return target__data_packet

    def get__liveroom_list(
        self,
        date_range: list[str] | list[list[str]],
        timeout: float = None,
        throw_err=True,
    ):
        """
        获取直播间详情数据列表

        Args:
            date_range: 日期范围, 例如 `[2025-06-01, 2025-06-30]`或者`[[2025-06-01, 2025-06-15], [2025-06-16, 2025-06-30]]`
            throw_err: 在执行过程中如果出错了是否抛出异常, 如果 False 则不抛出异常并将正确获取到的数据返回
        Returns:
            数据列表. `[{begin_date, end_date, data}]`
        """

        _timeout = timeout if isinstance(timeout, (float, int)) else self._timeout

        page = self._browser.chromium.new_tab()
        if not self._wait__data_query(
            page=page,
            data_type=DataPacketType.LIVE_LIST_DETAIL.value,
            func=lambda: page.get(Urls.live_list),
            timeout=_timeout,
        ):
            raise TimeoutError('进入页面后直播间信息列表数据包获取超时')

        def catch_data(begin_date: str, end_date: str):
            # 选择自定义日期范围
            data_packet = self._wait__data_query(
                page=page,
                data_type=DataPacketType.LIVE_LIST_DETAIL.value,
                func=lambda: pick__daterange(page, begin_date, end_date),
                timeout=_timeout,
            )
            if not data_packet:
                raise TimeoutError('选择自定义日期后获取数据包超时')

            resp_data = DataPacketProcessor(data_packet).filter(
                [
                    'data[0].count',
                    'data[0].data',
                    'data[0].meta.dimensions',
                    'data[0].meta.metrics',
                    'data[0].extra',
                ]
            )
            if not resp_data.get('count'):
                raise ValueError('直播间列表为空')

            # ========== 仅作日期判断 ==========
            extra = resp_data.get('extra')
            if not isinstance(extra, dict):
                raise ValueError('直播间扩展信息格式非预期的 dict')
            if (extra_start_date := extra.get('startDateDtm')) != begin_date or (
                extra_end_date := extra.get('endDateDtm')
            ) != end_date:
                raise ValueError(
                    f'直播间扩展信息的日期 [{extra_start_date}~{extra_end_date}] 与预期日期不一致'
                )
            # ========== 仅作日期判断 ==========

            field_arr: list[dict] = [
                *resp_data.get('dimensions'),
                *resp_data.get('metrics'),
            ]
            field_dict = {item['key']: item['name'] for item in field_arr}

            data_list = []
            for item in resp_data.get('data'):
                record = {}
                for field_key, field_name in field_dict.items():
                    if field_key not in item:
                        continue
                    record[field_name] = item[field_key]['value']

                decimal_fields = [
                    '商品点击率（次数）',
                    '商品点击率（人数）',
                    '观看支付率',
                    '支付转化率',
                    '退款率',
                ]
                record = DictUtils.dict_format__ratio(record, decimal_fields)
                record = DictUtils.dict_format__round(record, decimal_fields)
                data_list.append(record)

            return data_list

        date_range_list = (
            [date_range]
            if isinstance(date_range, list)
            and len(date_range) == 2
            and all(map(lambda x: isinstance(x, str), date_range))
            else date_range
        )
        data_set: list[dict] = []
        for begin_date, end_date in date_range_list:
            try:
                data_list = catch_data(begin_date, end_date)
                data_set.append(
                    {'begin_date': begin_date, 'end_date': end_date, 'data': data_list}
                )
            except Exception as err:
                if throw_err is True:
                    raise RuntimeError(
                        f'{begin_date} ~ {end_date} 获取数据出错了: {err}'
                    ) from err

        page.close()

        return data_set

    def download__liveroom_list(
        self,
        date_range: list[str] | list[list[str]],
        save_path: str = None,
        format=True,
        timeout: float = None,
        throw_err=True,
    ):
        """
        下载直播间详情数据文件

        Args:
            date_range: 日期范围, 例如 `[2025-06-01, 2025-06-30]`或者`[[2025-06-01, 2025-06-15], [2025-06-16, 2025-06-30]]`
            save_path: 下载文件保存位置, 留空则下载到系统缓存目录下
            format: 格式化. 如果设置 True 则返回文件的路径, 否则返回文件内容
            timeout: 超时时间
            throw_err: 在执行过程中如果出错了是否抛出异常, 如果 False 则不抛出异常并将正确获取到的数据返回
        """

        _timeout = timeout if isinstance(timeout, (float, int)) else self._timeout

        page = self._browser.chromium.new_tab()
        if not self._wait__data_query(
            page=page,
            data_type=DataPacketType.LIVE_LIST_DETAIL.value,
            func=lambda: page.get(Urls.live_list),
            timeout=_timeout,
        ):
            raise TimeoutError('进入页面后直播间信息列表数据包获取超时')

        def download_file(begin_date: str, end_date: str):
            # 选择自定义日期范围
            data_packet = self._wait__data_query(
                page=page,
                data_type=DataPacketType.LIVE_LIST_DETAIL.value,
                func=lambda: pick__daterange(page, begin_date, end_date),
                timeout=_timeout,
            )
            if not data_packet:
                raise TimeoutError('选择自定义日期后获取数据包超时')

            resp_data = DataPacketProcessor(data_packet).filter(
                ['data[0].count', 'data[0].extra']
            )
            if not resp_data.get('count'):
                raise ValueError('直播间列表为空')

            # ========== 仅作日期判断 ==========
            extra = resp_data.get('extra')
            if not isinstance(extra, dict):
                raise ValueError('直播间扩展信息格式非预期的 dict')
            if (extra_start_date := extra.get('startDateDtm')) != begin_date or (
                extra_end_date := extra.get('endDateDtm')
            ) != end_date:
                raise ValueError(
                    f'直播间扩展信息的日期 [{extra_start_date}~{extra_end_date}] 与预期日期不一致'
                )
            # ========== 仅作日期判断 ==========

            download_btn = page.ele('t:button@@text()=下载数据', timeout=2)
            if not download_btn:
                raise RuntimeError('未找到 [下载数据] 按钮')

            _save_path = save_path if save_path else gettempdir()
            download_mission = download_btn.click.to_download(
                save_path=_save_path, by_js=True
            )
            file_path = download_mission.wait()
            return file_path

        date_range_list = (
            [date_range]
            if isinstance(date_range, list)
            and len(date_range) == 2
            and all(map(lambda x: isinstance(x, str), date_range))
            else date_range
        )
        data_list: list[dict] = []
        for begin_date, end_date in date_range_list:
            try:
                file_path = download_file(begin_date, end_date)
                data_list.append(
                    {'begin_date': begin_date, 'end_date': end_date, 'data': file_path}
                )
            except Exception as err:
                if throw_err is True:
                    raise RuntimeError(
                        f'{begin_date} ~ {end_date} 下载出错了: {err}'
                    ) from err

        page.close()

        if format is True:
            for i, item in enumerate(data_list):
                file_path = item.get('data')
                if not file_path or not path.exists(file_path):
                    item[i]['data'] = None
                    continue

                data = OsTools.xlsx_read(file_path)
                OsTools.file_remove(file_path)
                data_list[i]['data'] = data

        return data_list
