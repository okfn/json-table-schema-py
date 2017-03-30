# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six
from ..config import ERROR


# Module API

def cast_yearmonth_default(value):
    if not isinstance(value, int):
        if not isinstance(value, six.string_types):
            return ERROR
        if len(value) not in [1, 2]:
            return ERROR
        try:
            value = int(value)
        except Exception:
            return ERROR
    if value < 0 or value > 12:
        return ERROR
    return value