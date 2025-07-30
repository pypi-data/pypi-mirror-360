# -*- coding:utf-8 -*-
'''
import datetime
now = datetime.datetime.now()

month = now.month
day = now.day
hour = now.hour
minute = now.minute
# f"{number:.2f}"
# f"{number:02d}"
s = f"{month:02d}{day:02d}{hour:02d}{minute:02d}"

__version_info = (0, 0, 3, int(s))
'''
__version_info = (0, 0, 33)
__version__ = ".".join([str(x) for x in __version_info])
