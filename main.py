import os
import subprocess
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
if sys.version_info < (3,):
	range = xrange

import random
import math
import time

import psmove

print("Run with sudo to pair controllers connected with USB")

# Pair move controllers connected by usb
usbMoves = [move for move in [psmove.PSMove(i) for i in range(min(2, psmove.count_connected()))] if move.connection_type == psmove.Conn_USB]
for i in range(len(usbMoves)):
  move = usbMoves[i]
  if move.pair():
    print("Controller %(i)d paired" % {"i": i})
  else:
    print("Controller %(i)d not paired" % {"i": i})

#Play with move controllers connected by bluetooth
moves = [move for move in [psmove.PSMove(i) for i in range(min(2, psmove.count_connected()))] if move.connection_type != psmove.Conn_USB]

print("%(n)d PS Move controllers detected" % {"n": len(moves)})

if len(moves) < 2:
  if len(moves) + len(usbMoves) >= 2:
    print("Requires 2 PS Move controllers, connect more controllers by pressing ps button")
    while len(moves) < 2:
      moves = [move for move in [psmove.PSMove(i) for i in range(min(2, psmove.count_connected()))] if move.connection_type != psmove.Conn_USB]
  else:
    print("Requires 2 PS Move controllers, exiting...")
    exit()

for i in range(len(moves)):
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

shield2colour = {
  "none": (255, 255, 255),
  "fire": (255, 128, 128),
  "ice": (128, 128, 255),
  "reflect": (128, 255, 128),
}

class Wizard:
  health = 20
  move = None
  opponent = None
  shield = "none"
  shieldEffacy = 0
  shieldTimer = 0
  castTimer = 0
  damageTimer = 0
  dotDamage = 0
  dotPeriod = 0
  dotTicks = 0
  dotTimer = 0
  
  def __init__(self, move, opponent):
    self.move = move
    self.opponent = opponent
    move.wizard = self
  
  def applyDoT(self, damage, period, ticks):
    self.dotDamage = damage
    self.dotPeriod = period
    self.dotTicks = ticks
    self.dotTimer = period
    
  def damage(self, damage, element):
    if self.shield == "reflect" and self.opponent.shield != "reflect":
      self.opponent.damage(damage, element)
      return
    if self.shield == element:
      self.health -= int(float(damage)*max(1.0-self.shieldEffacy, 0.0))
    else:
      self.health -= damage
    self.damageTimer = .5

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
    if type(self.element) == tuple and type(self.damage) == tuple:
      for a, e in zip(self.damage, self.element):
        caster.opponent.damage(a, e)
    else:
      caster.opponent.damage(self.damage, self.element)
    print(caster.opponent.health)

class DamageOverTimeSpell(Spell):
  damage = 0
  period = 0
  ticks = 0

  def __init__(self, name, sequence, damage, period, ticks):
    Spell.__init__(self, name, sequence)
    self.damage = damage
    self.period = period
    self.ticks = ticks
    
  def cast(self, caster):
    caster.applyDoT(self.damage, self.period, self.ticks)
    caster.opponent.applyDoT(self.damage, self.period, self.ticks)

class DrainSpell(Spell):
  damage = 0
  element = None
  
  def __init__(self, name, sequence, damage, element):
    Spell.__init__(self, name, sequence)
    self.damage = damage
    self.element = element
    
  def cast(self, caster):
    caster.opponent.damage(self.damage, self.element)
    caster.health = min(20, caster.health + self.damage)

class ShieldSpell(Spell):
  element = None
  duration = 0.0
  effacy = 1.0
  
  def __init__(self, name, sequence, element, duration, effacy):
    Spell.__init__(self, name, sequence)
    self.element = element
    self.duration = duration
    self.effacy = effacy
    
  def cast(self, caster):
    caster.shield = self.element
    caster.shieldEffacy = self.effacy
    caster.shieldTimer = self.duration

class CounterSpell(Spell):
  def __init__(self, name, sequence):
    Spell.__init__(self, name, sequence)
    
  def cast(self, caster):
    caster.opponent.move.sequence = ""

class LifeSwitchSpell(Spell):
  def __init__(self, name, sequence):
    Spell.__init__(self, name, sequence)
    
  def cast(self, caster):
    caster.health, caster.opponent.health = caster.opponent.health, caster.health

spells = (
  DirectDamageSpell("Finger of Mild Discomfort", "LRUDUDSSS", "earth", 19),
  DirectDamageSpell("Fierce Candle", "RURURLS", "fire", 5),
  DirectDamageSpell("Severe Damp", "LULULRS", "ice", 5),
  LifeSwitchSpell("Always Greener", "DDDDDD"),
  #DamageOverTimeSpell("Elemental Sneeze", "SRLUD", 1, 2.0, 5),
  #DirectDamageSpell("Prismatic Spurt", "DURLS", ("fire", "ice"), (3, 2)),
  ShieldSpell("Aluminium Foil", "DRLUD", "reflect", 6.0, 1.0),
  DrainSpell("Life Sucks", "DDDS", 2, "earth"),
  CounterSpell("Kitchen Counter", "DUS"),
  #DirectDamageSpell("Mud Shot", "DUS", "earth", 2),
  DirectDamageSpell("Luke-Warm Blast", "RUR", "fire", 3),
  DirectDamageSpell("Light Drizzle", "LUL", "ice", 3),
  DirectDamageSpell("Jammy Dodger", "SU", "earth", 1),
  ShieldSpell("Hot Air", "RD", "fire", 12.0, 0.5),
  ShieldSpell("Ice Sheet", "LD", "ice", 6.0, 1.0),
)

while True:
  winner = None
  
  wizards = []
  wizards.append(Wizard(moves[0], None))
  wizards.append(Wizard(moves[1], wizards[0]))
  wizards[0].opponent = wizards[1]

  for i in range(len(moves)):
    move = moves[i]
    move.sequence = ""
    move.actionTimer = 0.5
    move.poll()

  while winner == None:
    for i in range(len(moves)):
      move = moves[i]
      move.poll()
      ax, ay, az = move.get_accelerometer_frame(psmove.Frame_SecondHalf)
      gx, gy, gz = move.get_gyroscope_frame(psmove.Frame_SecondHalf)

      move.actionTimer -= 0.01
      if move.actionTimer <= 0:
        action = ""
        max_g = max(0, abs(gx), abs(gy), abs(gz))
        max_a = max(0, abs(ax), abs(ay), abs(az))
        if az > 0.8 and ((gz > 11 and gz == max_g) or ax < -2):
          action = "L"
        elif az > 0.8 and ((gz < -11 and gz == -max_g) or ax > 2):
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
      if move.wizard.damageTimer > 0 and int(10*move.wizard.damageTimer)%2 == 0:
        colour = (0,0,0)
      elif len(move.sequence) > 0:
        if move.actionTimer <= 0:
          colour = shield2colour[move.wizard.shield]
        else:
          colour = action2colour[move.sequence[-1:]]
      else:
        colour = (255,128,0)
      colour = [int((c * move.wizard.health) / 20) for c in colour]
      move.set_leds(*colour)

      if move.wizard.damageTimer > 0:
        move.set_rumble(255)
      elif move.actionTimer > 0:
        move.set_rumble(128)
      else:
        move.set_rumble(0)
      move.update_leds()
  
    for wizard in wizards:
      wizard.castTimer -= 0.01
      wizard.shieldTimer -= 0.01
      wizard.damageTimer -= 0.01
      wizard.dotTimer -= 0.01
      if wizard.dotTicks > 0 and wizard.dotTimer < 0:
        wizard.damage(wizard.dotDamage, "fire")
        wizard.damage(wizard.dotDamage, "ice")
        wizard.dotTimer = wizard.dotPeriod
        wizard.dotTicks -= 1
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
  time.sleep(1)
