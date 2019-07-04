from __future__ import print_function

import random
import time

from lib.progress.bar import (Bar, ChargingBar, FillingSquaresBar,
                              FillingCirclesBar, IncrementalBar, PixelBar,
                              ShadyBar)


def sleep():
    t = 0.01
    t += t * random.uniform(-0.1, 0.1)  # Add some variance
    time.sleep(t)


for bar_cls in (Bar, ChargingBar, FillingSquaresBar, FillingCirclesBar):
    suffix = '%(index)d/%(max)d [%(elapsed)d / %(eta)d / %(eta_td)s]'
    bar = bar_cls(bar_cls.__name__, suffix=suffix)
    for i in bar.iter(range(200)):
        sleep()

for bar_cls in (IncrementalBar, PixelBar, ShadyBar):
    suffix = '%(percent)d%% [%(elapsed_td)s / %(eta)d / %(eta_td)s]'
    bar = bar_cls(bar_cls.__name__, suffix=suffix)
    for i in bar.iter(range(200)):
        sleep()

bar.finish()
