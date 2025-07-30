# -*- coding: utf-8 -*-
# Copyright (C) 2024 TUD | ZIH
# ralf.klammer@tu-dresden.de

import logging


log = logging.getLogger(__name__)

timeslots = [
    {
        "value": "T1",
        "start": 1840,
        "end": 1859,
    },
    {
        "value": "T2",
        "start": 1860,
        "end": 1879,
    },
    {
        "value": "T3",
        "start": 1880,
        "end": 1899,
    },
    {
        "value": "T4",
        "start": 1900,
        "end": 1920,
    },
]

authorgender = [
    {"value": "male", "versions": ["M", "male", "m", "männlich"]},
    {"value": "female", "versions": ["F", "female", "f", "weiblich"]},
    {"value": "mixed", "versions": ["X", "mixed", "gemischt", "verschiedene"]},
    {"value": "unknown", "versions": ["U", "unknown", None]},
]

# this version would be the "correct" one if textgrid would stick to 100%
# percent to
# https://distantreading.github.io/Schema/eltec-1.html#TEI.authorGender
# authorgender = [
#     {"value": "M", "versions": ["male", "m", "männlich"]},
#     {"value": "F", "versions": ["female", "f", "weiblich"]},
#     {"value": "X", "versions": ["mixed", "gemischt", "verschiedene"]},
#     {"value": "U", "versions": ["unknown", None]},
# ]

sizes = [
    {
        "value": "short",
        "start": 10000,
        "end": 50000,
    },
    {
        "value": "medium",
        "start": 50000,
        "end": 100000,
    },
    {
        "value": "long",
        "start": 100000,
        "end": float("inf"),
    },
]


def date_to_timeslot(date):
    log.debug("date_to_timeslot - date: %s" % date)
    if not date:
        return
    if isinstance(date, str) or isinstance(date, int):
        try:
            date = int(date)
        except:
            log.debug("%s is not convertible to int" % date)
            return
        for slot in timeslots:
            if date >= slot["start"] and date <= slot["end"]:
                return slot["value"]
        else:
            return None
    else:
        log.error(
            'Unhandled datatype (%s) for "date" in "date_to_timeslot"'
            % type(date)
        )


def gender_to_authorgender(gender):
    log.debug("gender_to_authorgender - gender: %s" % gender)
    for og in authorgender:
        if gender in og["versions"]:
            return og["value"]


def wordcount_to_size(wordcount):
    log.debug("wordcount_to_size - wordcount: %s" % wordcount)
    if not wordcount:
        return
    try:
        wordcount = int(wordcount)
    except:
        log.debug("%s is not convertible to int" % wordcount)
        return
    for size in sizes:
        if wordcount >= size["start"] and wordcount <= size["end"]:
            return size["value"]
    else:
        return None
