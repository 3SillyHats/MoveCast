import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

import math
import time

import psmove

print("Run with sudo to pair controllers connected with USB")

moves = [psmove.PSMove(i) for i in xrange(psmove.count_connected())]

print("%(n)d PS Move controllers detected" % {"n": len(moves)})

for i in xrange(len(moves)):
  move = moves[i]
  if move.pair():
    print("Controller %(i)d paired" % {"i": i})
  else:
    print("Controller %(i)d not paired" % {"i": i})

max_ax, max_ay, max_az = 0, 0, 0
min_ax, min_ay, min_az = 0, 0, 0
max_gx, max_gy, max_gz = 0, 0, 0
min_gx, min_gy, min_gz = 0, 0, 0

while True:
  for i in xrange(len(moves)):
    move = moves[i]
    move.poll()
    ax, ay, az = move.get_accelerometer_frame(psmove.Frame_SecondHalf)
    gx, gy, gz = move.get_gyroscope_frame(psmove.Frame_SecondHalf)
    max_ax = max(max_ax, ax)
    max_ay = max(max_ay, ay)
    max_az = max(max_az, az)
    min_ax = min(min_ax, ax)
    min_ay = min(min_ay, ay)
    min_az = min(min_az, az)
    max_gx = max(max_gx, gx)
    max_gy = max(max_gy, gy)
    max_gz = max(max_gz, gz)
    min_gx = min(min_gx, gx)
    min_gy = min(min_gy, gy)
    min_gz = min(min_gz, gz)

    pressed, released = move.get_button_events()
    if pressed & psmove.Btn_T:
      max_ax, max_ay, max_az = 0, 0, 0
      min_ax, min_ay, min_az = 0, 0, 0
      max_gx, max_gy, max_gz = 0, 0, 0
      min_gx, min_gy, min_gz = 0, 0, 0
    elif released & psmove.Btn_T:
      action = ""
      max_g = max(max_gx, max_gy, max_gz, -min_gx, -min_gy, -min_gz)
      max_a = max(max_ax, max_ay, max_az, -min_ax, -min_ay, -min_az)
      if max_gz > 10 and max_gz == max_g and max_az > 0.8:
        action = "L"
      elif min_gz < -10 and min_gz == -max_g and max_az > 0.8:
        action = "R"
      elif max_gx > 10 and max_gx == max_g:
        action = "U"
      elif min_gx < -10 and min_gx == -max_g:
        action = "D"
      elif max_ay > 2:
        action = "S"
      print(action)

    move.set_leds(0, 0, 0)
    move.set_rumble(0)
    move.update_leds()
      
  time.sleep(.01)
