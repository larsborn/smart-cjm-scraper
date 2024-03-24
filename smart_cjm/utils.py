#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import logging
from typing import Optional

import requests.adapters
from urllib3 import Retry


class ConsoleHandler(logging.Handler):
    def emit(self, record):
        print('[%s] %s' % (record.levelname, record.msg))


class CustomHTTPAdapter(requests.adapters.HTTPAdapter):
    def __init__(
            self,
            fixed_timeout: int = 5,
            retries: int = 3,
            backoff_factor: float = 0.3,
            status_forcelist=(500, 502, 504),
            pool_maxsize: Optional[int] = None
    ):
        self._fixed_timeout = fixed_timeout
        retry_strategy = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        kwargs = {'max_retries': retry_strategy}
        if pool_maxsize is not None:
            kwargs['pool_maxsize'] = pool_maxsize
        super().__init__(**kwargs)

    def send(self, *args, **kwargs):
        if kwargs['timeout'] is None:
            kwargs['timeout'] = self._fixed_timeout
        return super(CustomHTTPAdapter, self).send(*args, **kwargs)


def parse_datetime(s: str) -> datetime.datetime:
    # 2024-04-05T08:00:00.0000000+02:00
    s = s.replace('.0000000', '')
    if s[-3] == ':':
        s = s[:-3] + s[-2:]
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S%z')
