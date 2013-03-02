import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

import time

import psmove

moves = [psmove.PSMove(i) for i in xrange(psmove.count_connected())]

while True:
  for move in moves:
    move.poll()
    ax, ay, az = move.get_accelerometer_frame(psmove.Frame_SecondHalf)
    move.set_rumble(0)
    ax = ax*ax
    ay = ay*ay
    az = az*az
    if ax > ay and ax > az:
      move.set_leds(255, 0, 0)
    elif ay > ax and ay > az:
      move.set_leds(0, 255, 0)
    elif az > ax and az > ay:
      move.set_leds(0, 0, 255)
    else:
      move.set_leds(0, 0, 0)
    move.update_leds()
      
  time.sleep(.01)
