import os
import subprocess
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

import random
import math
import time

import psmove

print("Run with sudo to pair controllers connected with USB")

moves = [psmove.PSMove(i) for i in xrange(min(2, psmove.count_connected()))]

print("%(n)d PS Move controllers detected" % {"n": len(moves)})

for i in xrange(len(moves)):
  move = moves[i]
  if move.pair():
    print("Controller %(i)d paired" % {"i": i})
  else:
    print("Controller %(i)d not paired" % {"i": i})
  move.sequence = ""
  move.set_leds(255, 255, 255)
  move.update_leds()
  move.actionTimer = 0

action2colour = {
  "U": (255, 255, 0),
  "D": (0, 255, 0),
  "L": (0, 0, 255),
  "R": (255, 0, 0),
  "S": (255, 0, 255),
}

class Wizard:
  health = 20
  move = None
  opponent = None
  shield = "none"
  shieldTimer = 0
  castTimer = 0
  damageTimer = 0
  
  def __init__(self, move, opponent):
    self.move = move
    self.opponent = opponent
    move.wizard = self

wizards = []
wizards.append(Wizard(moves[0], None))
wizards.append(Wizard(moves[1], wizards[0]))
wizards[0].opponent = wizards[1]

class Spell:
  name = None
  sequence = None
  
  def __init__(self, name, sequence):
    self.name = name
    self.sequence = sequence
  
  def cast(self, caster):
    pass

class DirectDamageSpell(Spell):
  element = None
  damage = 0
  
  def __init__(self, name, sequence, element, damage):
    Spell.__init__(self, name, sequence)
    self.element = element
    self.damage = damage
    
  def cast(self, caster):
    if caster.opponent.shield == self.element:
      caster.opponent.health -= self.damage/2
    else:
      caster.opponent.health -= self.damage
    caster.opponent.damageTimer = .5

class ShieldSpell(Spell):
  element = None
  
  def __init__(self, name, sequence, element):
    Spell.__init__(self, name, sequence)
    self.element = element
    
  def cast(self, caster):
    caster.shield = self.element
    caster.shieldTimer = 5.0

spells = [
  DirectDamageSpell("Mud Shot", "DUS", "earth", 2),
  DirectDamageSpell("Luke-Warm Blast", "RUR", "fire", 3),
  ShieldSpell("Fire Shield", "RD", "fire"),
  DirectDamageSpell("Light Drizzle", "LUL", "ice", 3),
  ShieldSpell("Ice Wall", "LD", "ice"),
]

winner = None

while winner == None:
  for i in xrange(len(moves)):
    move = moves[i]
    move.poll()
    ax, ay, az = move.get_accelerometer_frame(psmove.Frame_SecondHalf)
    gx, gy, gz = move.get_gyroscope_frame(psmove.Frame_SecondHalf)

    move.actionTimer -= 0.01
    if move.actionTimer <= 0:
      action = ""
      max_g = max(0, abs(gx), abs(gy), abs(gz))
      max_a = max(0, abs(ax), abs(ay), abs(az))
      if az > 0.8 and ((gz > 10 and gz == max_g) or ax < -2):
        action = "L"
      elif az > 0.8 and ((gz < -10 and gz == -max_g) or ax > 2):
        action = "R"
      elif gx > 10 and gx == max_g:
        action = "U"
      elif gx < -10 and gx == -max_g:
        action = "D"
      elif ay > 1.5:
        action = "S"
      if action != "":
        move.actionTimer = .5
        move.sequence = (move.sequence + action)[-10:]
        for spell in spells:
          if move.sequence[-len(spell.sequence):] == spell.sequence:
            print(spell.name)
            p = subprocess.Popen("echo \""+spell.name+"\" | festival --tts", shell=True)
            spell.cast(move.wizard)
            break

    colour = (255, 255, 255)
    if move.actionTimer <= 0:
      colour = (255, 255, 255)
      move.set_rumble(0)
    elif len(move.sequence) > 0:
      colour = action2colour[move.sequence[-1:]]
      move.set_rumble(128)
    colour = [(c * move.wizard.health) / 20 for c in colour]
    move.set_leds(*colour)

    if move.wizard.damageTimer > 0:
      move.set_rumble(255)
    move.update_leds()
  
  for wizard in wizards:
    wizard.castTimer -= 0.01
    wizard.shieldTimer -= 0.01
    wizard.damageTimer -= 0.01
    if wizard.shieldTimer < 0:
      wizard.shield = "none"
      wizard.shieldTimer = 0
    if wizard.health <= 0:
      winner = wizard.opponent
  
  time.sleep(.01)

# Declare winner
timer = 0
h = 0
while timer < 5.0:
    for wizard in wizards:
        if wizard != winner:
            wizard.move.set_leds(0, 0, 0)
            wizard.move.set_rumble(0)
        else:
            h = (h + 0.05) % 6
            if h < 3.0:
                wizard.move.set_rumble(128)
            else:
                wizard.move.set_rumble(0)
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
            wizard.move.set_leds(int(r*255), int(g*255), int(b*255))
        wizard.move.update_leds()
        
    timer = timer + .01
    time.sleep(.01)
  
for move in moves:
  move.set_leds(0, 0, 0)
  move.set_rumble(0)
  move.update_leds()
time.sleep(0.1)
