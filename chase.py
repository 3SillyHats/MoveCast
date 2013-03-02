import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

import math
import random
import time

import psmove

# Helper functions
def clamp(x, a, b):
    return min(b, max(a, x))

# Connect controllers
print("Run with sudo to pair controllers connected with USB")
moves = [psmove.PSMove(i) for i in xrange(psmove.count_connected())]
print("%(n)d PS Move controllers detected" % {"n": len(moves)})
for i in xrange(len(moves)):
    move = moves[i]
    if move.pair():
        print("Controller %(i)d paired" % {"i": i})
    else:
        print("Controller %(i)d not paired" % {"i": i})

# Setup game
caught = [False]*len(moves)

# Run game
while True:
    # Select random target to chase
    validTargets = 0
    for i in xrange(0, len(caught)):
        if not caught[i]:
            validTargets += 1
    if validTargets <= 1:
        break
    target = random.randint(0, validTargets - 1)
    i = 0
    while i <= target:
        if caught[i]:
            target += 1
        i += 1
    
    # Inform players of start of round
    for move in moves:
        move.set_rumble(128)
        move.update_leds()
    time.sleep(.5)
    for i in xrange(len(moves)):
        move = moves[i]
        # Warn next target by disabling all other players rumbles
        if i != target:
            move.set_rumble(0)
        move.update_leds()

    # Randomly flash red or blue on controllers
    timer = 0
    while timer < 3.0:
        for i in xrange(len(moves)):
            move = moves[i]
            
            if caught[i]:
                move.set_leds(0, 255, 0)
            elif random.random() < .5:
                move.set_leds(255, 0, 0)
            else:
                move.set_leds(0, 0, 255)
            move.update_leds()
        timer = timer + .1
        time.sleep(.1)
    moves[target].set_rumble(0)
    
    # Wait until next round
    timer = 0
    while timer < 15.0:
        # Update caught
        moves[target].poll()
        pressed, released = moves[target].get_button_events()
        if pressed != 0:
            caught[target] = True
            moves[target].set_leds(0, 255, 0)
            moves[target].update_leds()
            break
        
        # Set round colours for target or chaser
        for i in xrange(len(moves)):
            move = moves[i]
            
            if i == target:
                move.set_leds(255, 0, 0)
            elif caught[i]:
                move.set_leds(0, 255, 0)
            else:
                move.set_leds(0, 0, 255)
            move.update_leds()
        
        timer = timer + .01
        time.sleep(.01)

# Declare winner
timer = 0
h = 0
while timer < 5.0:
    for i in xrange(len(moves)):
        move = moves[i]
        if caught[i]:
            move.set_leds(0, 0, 0)
        else:
            h = (h + 0.05) % 6
            if h < 3.0:
                move.set_rumble(128)
            else:
                move.set_rumble(0)
            x = 1 - abs((h % 2) - 1)
            if h < 1:
                r, g, b = 1, x, 0
            elif h < 2:
                r, g, b = x, 1, 0
            elif h < 3:
                r, g, b = 0, 1, x
            elif h < 4:
                r, g, b = 0, x, 1
            elif h < 5:
                r, g, b = x, 0, 1
            elif h < 6:
                r, g, b = 1, 0, x
            move.set_leds(int(r*255), int(g*255), int(b*255))
        move.update_leds()
        
    timer = timer + .01
    time.sleep(.01)

for move in moves:
    move.set_leds(0, 0, 0)
    move.set_rumble(0)
    move.update_leds()
