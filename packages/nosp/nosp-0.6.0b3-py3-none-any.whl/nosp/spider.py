import abc
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from . import SpiderInfo
from .http import Request, BaseRequest


class SpiderThreadPool(object):

    def __init__(self):
        self.executor: Optional[ThreadPoolExecutor] = None

    def future_callback(self, future):
        if future.exception():
            raise future.exception()

    def submit_task(self, task_func, task):
        """
        向线程池中添加新任务
        :param task_func:
        :param task:
        :return:
        """
        future = self.executor.submit(task_func, task)
        future.add_done_callback(self.future_callback)

    def get_task_count(self) -> int:
        """
        获取当前线程池中还有多少任务数量
        :return:
        """
        return self.executor._work_queue.qsize()

    def start_batch_task(self, task_func, task_list: list, thread_num: int, wait=True):
        """
        多线程批量处理任务
        :param task_func: 任务函数
        :param task_list: 任务列表
        :param thread_num: 线程数量
        :param wait: 是否等待
        :return:
        """
        self.executor = ThreadPoolExecutor(max_workers=thread_num)
        try:
            for task in task_list:
                future = self.executor.submit(task_func, *task)
                future.add_done_callback(self.future_callback)
        finally:
            if wait:
                self.executor.shutdown(wait=True)
            # if wait:
            #     self.executor.shutdown(wait=False)
            #     while True:
            #         try:
            #             time.sleep(10)
            #         except KeyboardInterrupt:
            #             self.executor.shutdown(wait=True,cancel_futures=True)

    def task_wait(self):
        self.executor.shutdown(wait=True)


class BaseSpider(abc.ABC):

    def __init__(self, name, group_name=None, headers=None, cookies=None, monitor=False, proxy_url=None,
                 domain=None, url=None, freq=None, metadata=None, user=None, insert_table=None, task_type=0,
                 monitor_endpoint=None):
        """
        Spider 基类
        :param name: 任务名称
        :param group_name: 分组路径 /A/B/C
        :param headers: self.request -> headers
        :param cookies: self.request -> cookies
        :param monitor: 是否开启上报数据
        :param proxy_url: 代理池地址
        :param domain: 目标站点域名
        :param url: 目标站点url
        :param freq: 更新频率: 时更，日更，周更，月更，一次性
        :param metadata: 元数据
        :param user: 所属用户 [ENV:SERVER_NAME]
        :param insert_table: 插入主表名
        :param task_type: 任务类型 default 0
        :param monitor_endpoint: 上报端点地址 [ENV:PY_MONITOR_ENDPOINT]
        """
        self.info = SpiderInfo(name=name, group_name=group_name, monitor=monitor, monitor_endpoint=monitor_endpoint,
                               task_type=task_type, domain=domain, url=url, freq=freq, metadata=metadata, user=user,
                               insert_table=insert_table)
        self.local = threading.local()
        self.headers = headers if headers is not None else getattr(self.__class__, "headers", None)
        self.cookies = cookies if cookies is not None else getattr(self.__class__, "cookies", None)
        self.proxy_url = proxy_url if proxy_url is not None else getattr(self.__class__, "proxy_url", None)

    def get_request(self):
        return Request(proxy_url=self.proxy_url, headers=self.headers, cookies=self.cookies)

    @property
    def request(self) -> BaseRequest:
        if not hasattr(self.local, 'request'):
            self.local.request = self.get_request()
        return self.local.request

    def reset_monitor(self):
        self.info.stop()
        name = self.info.name
        group_name = self.info.group_name
        monitor_endpoint = self.info._monitor_endpoint
        del self.info
        self.info = SpiderInfo(name=name, group_name=group_name, monitor_endpoint=monitor_endpoint, monitor=True)

    def start(self, *args):
        pass

    def page_list(self, *args):
        pass

    def page_detail(self, *args):
        pass

    def parse(self, *args):
        pass
