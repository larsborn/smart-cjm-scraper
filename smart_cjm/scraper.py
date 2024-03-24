#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import os
import platform
from datetime import datetime, timezone

import requests

__service__ = 'SmartCjmOnlineTerminvereinbarungScraper'
__version__ = '0.1.0'

from smart_cjm.termine import Termine
from smart_cjm.utils import ConsoleHandler

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--base-url', default=os.getenv('BASE_URL'))
    parser.add_argument('--tenant-uid', default=os.getenv('TENANT_UID'))
    parser.add_argument(
        '--user-agent',
        default=F'{__service__}/{__version__} (python-requests {requests.__version__}) '
                F'{platform.system()} ({platform.release()})'
    )
    parser.add_argument('--list-dienstleistungen', action='store_true')
    parser.add_argument('--always-print-url', action='store_true')
    parser.add_argument('--days', default=os.getenv('DAYS', '7'), type=int)
    parser.add_argument('dienstleisung')
    parser.add_argument('unit')

    args = parser.parse_args()
    logger = logging.getLogger(__service__)
    logger.handlers.append(ConsoleHandler())
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    termine = Termine(args.base_url, args.tenant_uid, args.user_agent)
    selected = [
        dienstleistung for dienstleistung in termine.get_dienstleistungen()
        if dienstleistung.caption == args.dienstleisung
    ]
    if args.always_print_url:
        print(termine.session_url)
    if args.list_dienstleistungen:
        for dienstleistung in termine.get_dienstleistungen():
            print(f'{dienstleistung.caption} ({dienstleistung.uuid})')
    assert len(selected) > 0

    termine.select_dienstleistung(selected)
    for next_appointment in termine.get_next_appointments():
        if next_appointment.unit == args.unit:
            if (datetime.now(timezone.utc) - next_appointment.date).days <= args.days:
                print(next_appointment.date.strftime('%Y-%m-%d'))
                if not args.always_print_url:
                    print(termine.session_url)
