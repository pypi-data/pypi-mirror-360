# xhsark-data-collection
小红书千帆数据平台数据抓取

## 安装
```bash
pip install xhsark-data-collection
```

## 使用方法
### 连接浏览器
```python
from XhsarkDataCollection import Collector

collector = Collector()
collector.connect_browser(port=9122)
```

### 登录
```python
# 通过 cookie 登录
user_info = collector.login.by_cookie(cookie=cookie)
```

### 下载直播间列表
```python
data_list = collector.datacenter.live.download__liveroom_list(
    begin_date='2025-06-01', end_date='2025-06-30', raw=False, close_page=True
)
```