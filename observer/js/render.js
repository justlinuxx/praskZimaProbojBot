/**
 * @typedef Map
 * @prop {number} radius
 * @prop {Wall[]} walls
 */

/**
 * @typedef Position
 * @prop {number} x
 * @prop {number} y
 */

/**
 * @typedef Wall
 * @prop {Position} a
 * @prop {Position} b
 */

/**
 * @typedef Shooting
 * @prop {Position} attacker
 * @prop {Position} target
 */

/**
 * @typedef Frame
 * @prop {number} radius
 * @prop {MapItem[]} items
 * @prop {Player[]} players
 * @prop {Shooting[]} shootings
 */

/**
 * @typedef MapItem
 * @prop {number} x
 * @prop {number} y
 * @prop {number} type
 * @prop {number} weapon
 */

/**
 * @typedef Player
 * @prop {number} x
 * @prop {number} y
 * @prop {number} id
 * @prop {string} name
 * @prop {number} health
 * @prop {number} weapon
 * @prop {number} score
 * @prop {number} loaded_ammo
 * @prop {number} reload_cooldown
 */

class Renderer {
    constructor() {
        var width = window.innerWidth;
        var height = window.innerHeight;

        this.canvas = new Konva.Stage({
            container: "js-canvas",
            width: width,
            height: height,
        })
        this.playerLayers = {}
        this.mapLayer = new Konva.Layer()
        this.scoreboardLayer = new Konva.Layer()
        this.scoreboardLayer.x(width - 205)
        this.scoreboardLayer.y(5)
        this.itemGroup = new Konva.Group()
        this.mapLayer.add(this.itemGroup)
        this.shootingGroup = new Konva.Group()
        this.mapLayer.add(this.shootingGroup)

        this.canvas.add(this.mapLayer)
        this.canvas.add(this.scoreboardLayer)
        this.howlers = {}
    }

    /** @type {Player[]} players */
    renderScoreboard(players) {
        this.scoreboardLayer.removeChildren()
        const WEAPONS = ["", "KNIFE", "PISTOL", "TOMMY"]

        players.sort((a, b) => b.score - a.score)
        for (let i = 0; i < players.length; i++) {
            let group = new Konva.Group()
            let Y = 35*i
            let r = new Konva.Rect({
                x: 0,
                y: Y,
                width: 200,
                height: 30,
                fill: "black",
            })
            group.add(r)

            let name = new Konva.Text({
                x: 5,
                y: Y+3,
                text: players[i].name,
                fontSize: 16,
                fontStyle: "bold",
                fontFamily: 'Arial',
                fill: 'white',
            });
            group.add(name)

            let score = new Konva.Text({
                x: 200-18,
                y: Y+4,
                text: players[i].score,
                fontSize: 24,
                fontStyle: "bold",
                align: "right",
                fontFamily: 'Arial',
                fill: 'white',
            });
            score.x(200 - 5 - score.getTextWidth())
            group.add(score)

            let hp = new Konva.Text({
                x: 5,
                y: Y+19,
                text: players[i].health + " HP, " + WEAPONS[players[i].weapon],
                fontSize: 10,
                fontFamily: 'Arial',
                fill: 'white',
            });
            group.add(hp)

            if (players[i].health <= 0) {
                group.opacity(0.1)
            }

            this.scoreboardLayer.add(group)
        }
    }

    /** @type {Map} map */
    loadMap(map) {
        this.map = map
        this.mapBorder = new Konva.Circle({
            x: 0,
            y: 0,
            radius: this.map.radius,
            stroke: 'red',
            strokeWidth: 2
        })
        this.mapLayer.add(this.mapBorder)

        for (const wall of this.map.walls) {
            let wallObject = new Konva.Line({
                points: [wall.a.x, wall.a.y, wall.b.x, wall.b.y],
                stroke: "white"
            })
            this.mapLayer.add(wallObject)
        }
    }


    /** @type {Player} player */
    getPlayerLayer(player) {
        if (!this.playerLayers.hasOwnProperty(player.id)) {
            let group = new Konva.Group()
            let circle = new Konva.Circle({
                x: 0, y: 0, radius: 5,
                stroke: "white",
                fill: "black",
            })

            let name = new Konva.Text({
                x: 0,
                y: -16,
                text: player.name,
                fontSize: 10,
                fontStyle: "bold",
                fontFamily: 'Arial',
                fill: 'white',
            });
            name.x(name.getTextWidth() / -2)

            let healthbar_box = new Konva.Rect({
                width: 30,
                height: 5,
                x: -15,
                y: 10,
                stroke: "white",
                strokeWidth: 1,
            })

            group._healthbar = new Konva.Rect({
                width: 30,
                height: 5,
                x: -15,
                y: 10,
                fill: "green",
            })

            group.add(group._healthbar)
            group.add(healthbar_box)
            group.add(circle)
            group.add(name)

            this.mapLayer.add(group)
            this.playerLayers[player.id] = group
        }

        return this.playerLayers[player.id]
    }

    /** @type {Player} player */
    renderPlayer(player) {
        let layer = this.getPlayerLayer(player)
        if (player.health <= 0) {
            layer.opacity(0.1)
        } else {
            layer.opacity(1)
        }

        layer._healthbar.width(30 * (player.health / 100))

        new Konva.Tween({
            node: layer,
            duration: game.frameSpeed / 1000,
            x: player.x,
            y: player.y,
        }).play()
    }

    /** @type {MapItem[]} items */
    renderItems(items) {
        this.itemGroup.removeChildren()
        for (const item of items) {
            let i = new Konva.Circle({
                x: item.x,
                y: item.y,
                radius: 3,
                fill: item.type === 0 ? "yellow" : "cyan",
            })
            this.itemGroup.add(i)
        }
    }

    /** @type {Shooting[]} shootings */
    renderShootings(shootings) {
        this.shootingGroup.removeChildren()
        for (const shooting of shootings) {
            let line = new Konva.Line({
                points: [shooting.attacker.x, shooting.attacker.y, shooting.target.x, shooting.target.y],
                stroke: "red",
                strokeWidth: 1,
            })
            this.shootingGroup.add(line)
        }
    }

    /** @type {Frame} frame */
    render(frame) {
        this.mapBorder.radius(frame.radius)
        for (const player of frame.players) {
            this.renderPlayer(player)
        }

        this.renderItems(frame.items)
        this.renderScoreboard(frame.players)
        this.renderShootings(frame.shootings)
        for (const yap of frame.yaps) {

            if (yap in this.howlers) continue;
            this.howlers[yap] = new Howl({
                src: [`yaps/${yap}.mp3`]
            });
        }
        this.playYap(frame.yaps)

        let xPositions = frame.players.filter(p => p.health > 0).map(p => p.x).sort()
        let yPositions = frame.players.filter(p => p.health > 0).map(p => p.y).sort()

        let width = Math.max(Math.abs(xPositions[xPositions.length - 1] - xPositions[0] + 150), 500)
        let height = Math.max(Math.abs(yPositions[yPositions.length - 1] - yPositions[0] + 150), 500)
        let centerX = (xPositions[xPositions.length - 1] + xPositions[0]) / 2
        let centerY = (yPositions[yPositions.length - 1] + yPositions[0]) / 2

        let s = Math.min(this.canvas.width() / width, this.canvas.height() / height)
        new Konva.Tween({
            node: this.mapLayer,
            duration: game.frameSpeed / 1000,
            x: this.canvas.width()/2 - centerX * s,
            y: this.canvas.height()/2 - centerY * s,
            scaleX: s,
            scaleY: s,
        }).play()
    }

        playYap(yaps) {
            for (const yap of yaps) {
                const howler = this.howlers[yap];
                if (howler.playing()) {
                    continue
                }
                howler.play();
            }
        }
}
