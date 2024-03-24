#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Dienstleistung:
    uuid: str
    caption: str


@dataclass
class NextAppointment:
    date: datetime
    unit: str
    unit_uid: str
    duration: int
    link: str
