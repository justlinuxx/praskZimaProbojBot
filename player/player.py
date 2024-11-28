#!/bin/python3
from proboj import *
from weapons import *
from math import ceil, sqrt

class Hrac(Game):
  turn = -1

  def getPosAfterMove(self, myPos, destination, invert = False):
    diffX = myPos.x - destination.x
    diffY = myPos.y - destination.y
    distance = sqrt(diffX**2 + diffY**2)
    if distance == 0:
      return destination
    ratio = 20/distance
    if not invert:
      return XY(myPos.x - diffX*ratio, myPos.y - diffY*ratio)
    return XY(myPos.x + diffX*ratio, myPos.y + diffY*ratio)
  
  def getNearestEnemy(self, enemies):
    distOfNearestEnemy = 99999
    nearestEnemy = []
    for enemy in enemies:
      enemyPos: XY = enemy.xy
      distanceFromPlayer = enemyPos.dist(self.pos)
      if distanceFromPlayer < distOfNearestEnemy:
        distOfNearestEnemy = distanceFromPlayer
        nearestEnemy = [enemy]

    return nearestEnemy

  def getNearestWeapon(self, weapons, typeOfWeapon = None):
    distOfNearestWeapon = 99999
    nearestWeapon = []
    for weapon in weapons:
      weaponPos: XY = weapon.xy
      distFromPlayer = weaponPos.dist(self.pos)
      if (weapon.weapon == typeOfWeapon or typeOfWeapon == None) and distFromPlayer < distOfNearestWeapon:
        distOfNearestWeapon = distFromPlayer
        nearestWeapon = [weapon]
    return nearestWeapon

  def getNearestHealth(self, healthItems):
    distOfNearestHealth = 99999
    nearestHealth = None
    for healthItem in healthItems:
      weaponPos: XY = healthItem.xy
      distFromPlayer = weaponPos.dist(self.pos)
      if distFromPlayer < distOfNearestHealth:
        distOfNearestHealth = distFromPlayer
        nearestHealth = healthItem
    return nearestHealth
  
  def getNotNearestHealth(self, healthItems,noPos):
    distOfNearestHealth = 99999
    nearestHealth = None
    for healthItem in healthItems:
      weaponPos: XY = healthItem.xy
      distFromPlayer = weaponPos.dist(self.pos)
    if distFromPlayer < distOfNearestHealth and (round(noPos.x) != round(weaponPos.x)) and round(noPos.y) != round(weaponPos.y):
        distOfNearestHealth = distFromPlayer
        nearestHealth = healthItem
    return nearestHealth
  
  def inRange(self, range, entity):
    self.log(range, entity.xy.dist(self.pos))
    return entity.xy.dist(self.pos) <= range
  
  def willSurvive(self, healthItem, currentHealth, enemy):
    return currentHealth - (ceil((healthItem.xy.dist(self.pos)-6) / 20)+1) * enemy.weapon.stats.Damage > 0


  def make_turn(self):
    self.turn+=1

    self.pos = self.player.xy
    self.mode = None
    nearestEnemy = self.getNearestEnemy(self.enemy_players)
    
    priorityWeapon = WeaponTommy

    if self.player.weapon == WeaponNone or self.player.weapon != priorityWeapon:
      nearestWeapon = self.getNearestWeapon(filter(lambda i: i.type == "weapon", self.items), priorityWeapon)
      if nearestWeapon:
        nearestWeapon = nearestWeapon[0]
        if nearestWeapon.xy.dist(self.pos) > 7:
          return MoveTurn(nearestWeapon.xy)
        else:
          return PickUpTurn()
      else:
        nearestWeapon = self.getNearestWeapon(filter(lambda i: i.type == "weapon", self.items))
        nearestWeapon[0]
        if nearestWeapon.xy.dist(self.pos) > 7:
          return MoveTurn(nearestWeapon.xy)
        else:
          return PickUpTurn()

        
    if self.turn < 10 and self.pos.dist(XY(0,0)) < 200:
      return MoveTurn(self.getPosAfterMove(self.pos, XY(0,0), invert=True))
    nearestHealth = self.getNearestHealth(filter(lambda i: i.type == "health", self.items))
    
    if self.player.health < 30 and nearestHealth != None: self.mode = "heal"
    elif nearestHealth != None and self.player.health < 100 and nearestEnemy and self.willSurvive(nearestHealth, self.player.health, nearestEnemy[0]) and not self.willSurvive(nearestHealth, self.player.health - nearestEnemy[0].weapon.stats.Damage*2, nearestEnemy[0]): self.mode = "heal"
    elif nearestHealth != None and self.player.health < 100 and nearestEnemy and not self.willSurvive(nearestHealth, self.player.health, nearestEnemy[0]): self.mode = "retreat" 
    elif self.player.health < 100 and nearestHealth != None and nearestHealth.xy.dist(self.pos) < 100 and nearestEnemy and nearestEnemy[0].xy.dist(self.pos) > 250: self.mode = "heal"
    elif nearestEnemy and nearestEnemy[0].xy.dist(self.pos) <= 250: self.mode = "attack"
    elif len(self.enemy_players) == 1: self.mode = "attack"
    elif not nearestEnemy: self.mode = "spawn"
    elif self.player.xy.dist(XY(0,0)) > self.map.radius - 25: self.mode = "spawn"
    else: self.mode = "stay"


    if self.mode == "heal":
      self.log("heal")
      if self.inRange(7, nearestHealth):
        return PickUpTurn()
      else:
        return MoveTurn(nearestHealth.xy)
    if self.mode == "reachHealth":
      self.log("reachHEalth")
      if self.getPosAfterMove(self.pos, nearestHealth.xy).dist(nearestEnemy[0].xy) >= nearestEnemy[0].weapon.stats.Range+20 and self.pos.dist(nearestEnemy[0].xy) > 50+nearestEnemy[0].weapon.stats.Range:
        return MoveTurn(nearestHealth.xy)
      elif self.getNotNearestHealth(filter(lambda i: i.type == "health", self.items), nearestHealth.xy):
        return MoveTurn(self.getNotNearestHealth(filter(lambda i: i.type == "health", self.items), nearestHealth.xy).xy)
    if self.mode == "attack":
      self.log("attack")
      nearestEnemy = nearestEnemy[0]
      if self.inRange(self.player.weapon.stats.Range, nearestEnemy):
        return ShootTurn(nearestEnemy)
      else:     
        return MoveTurn(nearestEnemy.xy)
    if self.mode == "retreat":
      self.log("retrat")
      pos = self.getPosAfterMove(self.pos, nearestEnemy[0].xy, invert=True)
      if pos.dist(XY(0,0)) > self.map.radius-25:
        return ShootTurn(nearestEnemy[0])
      return MoveTurn(pos)
    if self.mode == "spawn":
      self.log("spawn")
      return MoveTurn(XY(0,0))
    if self.mode == "stay":
      self.log("stay")
      return YapTurn(0)
    return YapTurn(0)

if __name__ == '__main__':
    g = Hrac()
    g.run()
    g.log(f"SOM f{g.player}")