#!/bin/python3
from proboj import *
from weapons import *

class Hrac(Game):
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
  
  def inRange(self, range, entity):
    self.log(range, entity.xy.dist(self.pos))
    return entity.xy.dist(self.pos) <= range


  def make_turn(self):
    self.pos = self.player.xy
    self.mode = None

    nearestEnemy = self.getNearestEnemy(self.enemy_players)
    
    priorityWeapon = WeaponTommy

    if self.player.weapon != priorityWeapon:
      nearestWeapon = self.getNearestWeapon(filter(lambda i: i.type == "weapon", self.items), priorityWeapon)[0]
      if nearestWeapon.xy.dist(self.pos) > 7:
        return MoveTurn(nearestWeapon.xy)
      else:
        return PickUpTurn()
      
    nearestHealth = self.getNearestHealth(filter(lambda i: i.type == "health", self.items))
    if self.player.health < 30 and nearestHealth != None: self.mode = "health"
    elif self.player.health < 50 and nearestHealth and nearestHealth != None: self.mode = "health"
    elif self.player.health < 100 and nearestHealth != None and nearestHealth.xy.dist(self.pos) < 100: self.mode = "health"
    elif nearestEnemy and nearestEnemy[0].xy.dist(self.pos) <= 250: self.mode = "attack"
    elif len(nearestEnemy) == 1: self.mode = "attack"
    elif not nearestEnemy: self.mode = "spawn"
    elif self.player.xy.dist(XY(0,0)) > self.map.radius - 50: self.mode = "spawn"
    else: self.mode = "stay"


    if self.mode == "health":
      if self.inRange(7, nearestHealth):
        return PickUpTurn()
      else:
        return MoveTurn(nearestHealth.xy)
    elif self.mode == "attack":
      nearestEnemy = nearestEnemy[0]
      if self.inRange(self.player.weapon.stats.Range, nearestEnemy):
        return ShootTurn(nearestEnemy)
      else:     
        return MoveTurn(nearestEnemy.xy)
    elif self.mode == "retreat":
      nearestEnemy = nearestEnemy[0]
      return MoveTurn(XY(nearestEnemy.xy.x - self.pos.x, nearestEnemy.xy.y - self.pos.y))
    elif self.mode == "spawn":
      return MoveTurn(XY(0,0))
    elif self.mode == "stay":
      return MoveTurn(self.pos)
  

if __name__ == '__main__':
    


    g = Hrac()
    g.run()
    g.log(f"SOM f{g.player}")