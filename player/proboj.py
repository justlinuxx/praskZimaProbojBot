import json
import math
import sys
from abc import abstractstaticmethod
from typing import List

from weapons import weaponTypes, itemTypes


class XY:
    """
    Trieda, ktorá reprezentuje bod/vektor v 2D.
    """
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    @classmethod
    def from_json(cls, data: dict):
        return cls(data.get('x'), data.get('y'))

    def dist(self, other) -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt((dx*dx)+(dy*dy))

    def __str__(self):
        return f"XY({self.x}, {self.y})"


class Wall:
    """
    Trieda, ktorá reprezentuje stenu na mape. Je to úsečka
    medzi bodmi *A* a *B*.
    """
    def __init__(self, data: dict):
        self.a = XY.from_json(data.get('a'))
        self.b = XY.from_json(data.get('b'))

    def __str__(self):
        return f"Wall({self.a}, {self.b})"


class Map:
    """
    Trieda, ktorá reprezentuje mapu. Mapa je kruh.
    Tiež sa na nej môžu nachádazať steny.

    * radius - polomer mapy
    * walls - zoznam stien
    """

    def __init__(self, data: dict):
        self.radius = data.get('radius')
        self.walls = []
        for wall in data.get('walls'):
            self.walls.append(Wall(wall))

    @classmethod
    def read_map(cls):
        map_json = input()
        input()
        return Map(json.loads(map_json))


class Player:
    """
    Player je trieda, ktorá reprezentuje vášho hráča v hre.

    * id - ID hráča
    * xy - pozícia hráča
    * health - zostávajúce body života
    * weapon - vybavená zbraň
    * loaded_ammo - zostávajúce náboje
    * reload_cooldown - zostávajúci počet kôl, po ktoré nemožno strielať (prebíja sa zbraň)
    """
    def __init__(self, data):
        self.id = data.get('id')
        self.xy = XY(data.get('x'), data.get('y'))
        self.health = data.get('health')
        self.weapon = weaponTypes[data.get('weapon')]
        self.laoded_ammo = data.get('laoded_ammo')
        self.reload_cooldown = data.get('reload_cooldown')

    @classmethod
    def read_player(cls, data: dict):
        return cls(data)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def __str__(self):
        return f"Player({self.id}, {self.xy})"


class EnemyPlayer:
    """
    EnemyPlayer je trieda, ktorá reprezentuje nepriateľského hráča v hre.
    O ňom máme už len obmedzené informácie.

    * id - ID hráča
    * xy - pozícia hráča
    * weapon - vybavená zbraň
    """
    def __init__(self, data):
        self.xy = XY(data.get('x'), data.get('y'))
        self.id = data.get('id')
        self.weapon = weaponTypes[data.get('weapon')]

    @classmethod
    def read_player(cls, data: dict):
        return cls(data)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def __str__(self):
        return f"EnemyPlayer({self.id}, {self.xy})"


class Item:
    """
    Item je trieda, ktorá reprezentuje veci, ktoré môžeme zbierať zo zeme a použiť.

    * XY - pozícia itemu
    * type - typ item (lekárnička, zbraň)
    * weapon - typ zbrane
    """
    def __init__(self, data):
        self.xy = XY(data.get('x'), data.get('y'))
        self.type = itemTypes[data.get('type')]
        if self.type == 'weapon':
            self.weapon = weaponTypes[data.get('weapon')]

    @classmethod
    def read_item(cls, data: dict):
        return cls(data)

    def __str__(self):
        return f"Item({self.xy}, {self.type})"


class Turn:
    def print(self):
        print(".")


class MoveTurn(Turn):
    """
    MoveTurn je trieda, ktorá preprezentuje ťah pohybu.

    * XY - pozícia, ktorej smerom sa hráč pohne
    """
    def __init__(self, goal: XY):
        self.goal = goal

    def print(self):
        print(f"MOVE {self.goal.x} {self.goal.y}")
        print(".")

    def __str__(self):
        return f"MOVE {self.goal}"

class ShootTurn(Turn):
    """
    ShootTurn je trieda, ktorá preprezentuje ťah strieľania.

    * target - neprateľský hráč, na ktorého bude váš hráč strielať
    """
    def __init__(self, target: EnemyPlayer):
        self.target = target

    def print(self):
        print(f"SHOOT {self.target.id}")
        print(".")

    def __str__(self):
        return f"SHOOT {self.target}"

class PickUpTurn(Turn):
    """
    PickUpTurn je trieda, ktorá preprezentuje ťah zodvyhnutia itemu zo zeme.
    Zo zeme zodvyhne najbližší item.
    """
    def print(self):
        print(f"PICKUP")
        print(".")
    def __str__(self):
        return "PICK UP"

class DropTurn(Turn):
    """
    DropTurn je trieda, ktorá preprezentuje ťah vyhodenia zbrane.
    Vyhodí aktuálne vybavenú zbraň hráča.
    """
    def print(self):
        print(f"DROP")
        print(".")

    def __str__(self):
        return "DROP"

class ReloadTurn(Turn):
    """
    ReloadTurn je trieda, ktorá preprezentuje ťah prebitia zbrane.
    Prebije vybavenú zbraň hráča.
    """
    def print(self):
        print(f"RELOAD")
        print(".")

    def __str__(self):
        return "TACTICAL RELOAD"

class YapTurn(Turn):
    """
    YapTurn je trieda, ktorá preprezentuje ťah povedania hlášky.

    * yap_clip - id hlášky, ktorú mafián povie..
    """
    def __init__(self, yap_clip: int):
        self.clip = yap_clip

    def print(self):
        print(f"YAP {self.clip}")
        print(".")

    def __str__(self):
        return f"YAPPING {self.clip}"


class Game:
    """
    Game je trieda, ktorá preprezenuje celú hru.

    * map - objekt Mapy
    * player - váš hráč
    * enemy_player - zoznam neprateľských hráčov, ktorých vidíte
    * items - zoznam všetkých vecí, ktoré vidíte
    """

    def __init__(self):
        self.map = Map.read_map()
        self.player: Player
        self.enemy_players: List[EnemyPlayer]
        self.items: List[Item]

    @staticmethod
    def log(*args):
        """
        Vypíše dáta do logu. Syntax je rovnaká ako print().
        """
        print(*args, file=sys.stderr)

    def _send_turn(self, turn: Turn):
        turn.print()

    def _read_state(self):
        data = json.loads(input())
        self.map.radius = data.get('radius')
        self.player = Player.read_player(data.get('player'))
        self.items = [Item(item) for item in data.get('visible_items')]
        self.enemy_players = [EnemyPlayer(p) for p in data.get('visible_players')]
        input()

    def make_turn(self) -> Turn:
        raise NotImplementedError()

    def run(self):
        while True:
            self._read_state()
            turn = self.make_turn()
            self.log(turn)
            self._send_turn(turn)


if __name__ == "__main__":
    print("PROBOOOOJ")
