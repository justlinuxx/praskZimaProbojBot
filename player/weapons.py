import enum

from dataclasses import dataclass

@dataclass
class WeaponStats:
    Range: float
    Damage: int
    ReloadTime: int
    AmmoCapacity: int


@dataclass
class WeaponNone:
    stats = WeaponStats(0, 0, 0, 0)
@dataclass
class WeaponKnife:
    stats = WeaponStats(10, 34, 0, 1)
@dataclass
class WeaponPistol:
    stats = WeaponStats(20 * 5, 5, 2, 10)
@dataclass
class WeaponTommy:
    stats = WeaponStats(20 * 10, 8, 4, 25)


weaponTypes = {
    0: WeaponNone,
    1: WeaponKnife,
    2: WeaponPistol,
    3: WeaponTommy
}

itemTypes = {
    0: "weapon",
    1: "health"
}
