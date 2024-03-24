#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
from typing import List, Iterator

import requests
from bs4 import BeautifulSoup

from smart_cjm.model import Dienstleistung, NextAppointment
from smart_cjm.utils import parse_datetime


class Termine:
    LANG = 'de'

    def __init__(self, base_url: str, uid: str, user_agent: str):
        if not base_url:
            raise Exception('No BASE_URL or --base-url specified')
        self._base_url = base_url
        if not uid:
            raise Exception('No UID or --uid specified')
        self._uid = uid
        self._session = requests.Session()
        self._session.headers.update({'User-Agent': user_agent})
        self._sid = None
        self._dienstleistungen = None
        self._sid_regex = re.compile(r'sid=(?P<sid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})')

    @staticmethod
    def _sitzung_abgelaufen(response: requests.Response) -> bool:
        return b'Ihre Sitzung ist abgelaufen.' in response.content

    def get_dienstleistungen(self) -> List[Dienstleistung]:
        if self._dienstleistungen is None:
            response = self._session.get(f'{self._base_url}/?uid={self._uid}&lang=de&set_lang_ui=de')
            response.raise_for_status()
            content = response.content.decode('utf-8')
            if self._sitzung_abgelaufen(response):
                raise NotImplemented('Refreshing of sessions not implemented yet')
            m = self._sid_regex.search(content)
            self._sid = m.group('sid')
            response = requests.get(
                f'{self._base_url}/?uid={self._uid}&wsid={self._sid}&lang=de&set_lang_ui=de'
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            self._dienstleistungen = []
            for label in soup.find_all('label', {'class': 'service_title'}):
                label_for = label.get('for')
                self._dienstleistungen.append(Dienstleistung(
                    uuid=label_for[len('service_'):],
                    caption=label.get_text(),
                ))
        return self._dienstleistungen

    def get_next_appointments(self) -> Iterator[NextAppointment]:
        assert self._sid
        response = self._session.get(
            f'{self._base_url}/search_result',
            params={
                'search_mode': 'earliest',
                'uid': self._uid,
                'wsid': self._sid,
                'lang': self.LANG,
                'set_lang_ui': self.LANG,
            }
        )
        response.raise_for_status()
        assert not self._sitzung_abgelaufen(response)
        soup = BeautifulSoup(response.content, 'html.parser')
        div = soup.find(id='json_appointment_list')
        for appointment in json.loads(div.get_text())['appointments']:
            yield NextAppointment(
                date=parse_datetime(appointment['datetime_iso86001']),
                unit=appointment['unit'],
                unit_uid=appointment['unit_uid'],
                duration=int(appointment['duration']),
                link=appointment['link'],
            )

    def select_dienstleistung(self, selected: List[Dienstleistung]) -> None:
        data = [
            ('action_type', ''),
            ('steps', 'serviceslocationssearch_resultsbookingfinish'),
            ('step_current', 'services'),
            ('step_current_index', '0'),
            ('step_goto', '+1'),
            ('services', ''),
        ]
        assert self._dienstleistungen
        for dienstleistung in self._dienstleistungen:
            this_selected = dienstleistung.uuid in [s.uuid for s in selected]
            data.append(('services', dienstleistung.uuid))
            data.append((f'service_{dienstleistung.uuid}_amount', '1' if this_selected else ''))
        response = requests.post(
            f'{self._base_url}/',
            params={
                'uid': self._uid,
                'wsid': self._sid,
                'lang': self.LANG,
                'set_lang_ui': self.LANG,
            },
            data=data,
        )
        response.raise_for_status()
        assert not self._sitzung_abgelaufen(response)

    @property
    def session_url(self) -> str:
        return f'{self._base_url}/?uid={self._uid}&wsid={self._sid}&lang=de&set_lang_ui=de'
