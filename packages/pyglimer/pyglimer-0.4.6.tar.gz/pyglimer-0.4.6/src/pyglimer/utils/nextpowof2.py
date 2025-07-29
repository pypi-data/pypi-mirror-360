#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:copyright:
   The PyGLImER development team (makus@gfz-potsdam.de).
:license:
    EUROPEAN UNION PUBLIC LICENCE v. 1.2
   (https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12)
:author:
    Peter Makus (makus@gfz-potsdam.de)

Created: Friday, 18th October 2019 08:11:03 pm
Last Modified: Thursday, 25th March 2021 03:56:56 pm
"""


def nextPowerOf2(n: int):
    """ just returns the next higher power of two from n"""
    count = 0

    # First n in the below
    # condition is for the
    # case where n is 0
    if n and not (n & (n - 1)):
        return n

    while n != 0:
        n >>= 1
        count += 1

    return 1 << count
