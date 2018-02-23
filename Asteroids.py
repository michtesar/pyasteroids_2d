import pyglet
from pyglet.window import key
from pyglet import gl
import math
import random

global LIVES
global ALIVE

LIVES = 3
ALIVE = True

SHIP_X = 0
SHIP_Y = 0

window = pyglet.window.Window(fullscreen=True)
window.set_mouse_visible(False)

# Keyboard setup
key = pyglet.window.key
keyboard = pyglet.window.key.KeyStateHandler()
window.push_handlers(keyboard)


def draw_circle(x, y, radius):
    iterations = 20
    s = math.sin(2 * math.pi / iterations)
    c = math.cos(2 * math.pi / iterations)

    dx, dy = radius, 0

    gl.glBegin(gl.GL_LINE_STRIP)
    for i in range(iterations + 1):
        gl.glVertex2f(x + dx, y + dy)
        dx, dy = (dx * c - dy * s), (dy * c + dx * s)
    gl.glEnd()


#  Foreground and background
background = pyglet.graphics.OrderedGroup(0)
foreground = pyglet.graphics.OrderedGroup(1)
top = pyglet.graphics.OrderedGroup(2)

# Background
background_image = pyglet.image.load('Images/darkPurple.png')
background_sprite = pyglet.sprite.Sprite(background_image, group=background)
background_sprite.scale = 5.6
background_sprite.x = window.width / 2 - background_sprite.width / 2
background_sprite.y = window.height / 2 - background_sprite.height / 2

# Background music
background_music = pyglet.media.load('Sounds/xfiles.wav')
looper = pyglet.media.SourceGroup(background_music.audio_format, None)
looper.loop = True
looper.queue(background_music)
player = pyglet.media.Player()
player.queue(looper)
player.play()

# Ship
ship_image = pyglet.image.load('Images/playerShip1_blue.png')
ship_image.anchor_x = ship_image.width // 2
ship_image.anchor_y = ship_image.height // 2
ship_sprite = pyglet.sprite.Sprite(ship_image, group=foreground)
ship_sprite.scale = 0.6
ship_sprite.x = window.width / 2 - ship_sprite.width / 2
ship_sprite.y = window.height / 2 - ship_sprite.height / 2

# Wrecks
wreck_image = pyglet.image.load('Images/playerShip1_damage2.png')
wreck_image.anchor_x = ship_image.width // 2
wreck_image.anchor_y = ship_image.height // 2
wreck_sprite = pyglet.sprite.Sprite(ship_image, group=foreground)
wreck_sprite.scale = 0.6
wreck_sprite.x = window.width / 2 - ship_sprite.width / 2
wreck_sprite.y = window.height / 2 - ship_sprite.height

# Asteroid images
asteroid_image = pyglet.image.load('Images/meteorBrown_big3.png')
asteroid_image.anchor_x = asteroid_image.width // 2
asteroid_image.anchor_y = asteroid_image.height // 2
asteroid_sprite = pyglet.sprite.Sprite(asteroid_image, group=foreground)
asteroid_sprite.scale = 1.0
asteroid_sprite.rotation = 0.0
asteroid_sprite.x = 100
asteroid_sprite.y = 70

# Laser
laser_image = pyglet.image.load('Images/laserBlue01.png')
laser_image.anchor_x = laser_image.width // 2
laser_image.anchor_y = laser_image.height // 2
laser_sprite = pyglet.sprite.Sprite(laser_image, group=top)
laser_sprite.scale = 0.5
laser_sprite.rotation = 0.0
laser_sprite.x = 100
laser_sprite.y = 70

# GUI
score_label = pyglet.text.Label(text="Score: 0", x=10, y=window.height-20, group=foreground)
lives_label = pyglet.text.Label(text="Lives: {0}".format(LIVES), x=window.width-70, y=window.height-20,
                                group=foreground)


def distance(a, b, wrap_size):
    """Distance in one direction (x or y)"""
    result = abs(a - b)
    if result > wrap_size / 2:
        result = wrap_size - result
    return result


def overlaps(a, b):
    """Returns true iff two space objects overlap"""
    distance_squared = (distance(a.x, b.x, window.width) ** 2 +
                        distance(a.y, b.y, window.height) ** 2)
    max_distance_squared = a.width + b.width ** 2
    return distance_squared < max_distance_squared


def overlaps_asteroids(a, b):
    """Returns true iff two space objects overlap"""
    distance_squared = (distance(a.x, b.x, window.width) ** 2 +
                        distance(a.y, b.y, window.height) ** 2)
    max_distance_squared = a.width + b.width ** 2
    return distance_squared < max_distance_squared


def asteroids(num_asteroids):
    asteroids_swarm = list()
    for _ in range(num_asteroids):
        asteroid_x = random.randint(40, window.width-40)
        asteroid_y = random.randint(40, window.height-40)
        new_asteroid = pyglet.sprite.Sprite(img=asteroid_image, x=asteroid_x, y=asteroid_y)
        new_asteroid.rotation = random.randint(0, 360)
        new_asteroid.scale = random.random() + 0.3
        asteroids_swarm.append(new_asteroid)
    return asteroids_swarm


global asteroid_swarm
asteroid_swarm = asteroids(random.randint(4, 10))


def spawn_asteroid(dt=0):
    global asteroid_swarm
    while True:
        asteroid_x = random.randint(40, window.width - 40)
        asteroid_y = random.randint(40, window.height - 40)
        new_asteroid = pyglet.sprite.Sprite(img=asteroid_image, x=asteroid_x, y=asteroid_y)
        if not overlaps_asteroids(new_asteroid, ship_sprite):
            break
    new_asteroid.scale = random.random()+0.4
    asteroid_swarm.append(new_asteroid)


global lasers
lasers = list()


def fire(dt):
    global lasers
    lasers = list()
    if keyboard[key.SPACE]:
        laser_sound = pyglet.media.load('Sounds/laser.wav')
        laser_sound.play()
        new_laser = pyglet.sprite.Sprite(img=laser_image, x=ship_sprite.x, y=ship_sprite.y)
        new_laser.rotation = ship_sprite.rotation
        lasers.append(new_laser)


pyglet.clock.schedule_interval(spawn_asteroid, 1)
pyglet.clock.schedule_interval(fire, 1/3)


def update(dt):
    global lasers

    if keyboard[key.RIGHT]:
        ship_sprite.update(rotation=ship_sprite.rotation + 200 * dt)
    elif keyboard[key.LEFT]:
        ship_sprite.update(rotation=ship_sprite.rotation - 200 * dt)
    elif keyboard[key.UP]:
        angle_radians = math.radians(90 - ship_sprite.rotation)
        force_x = math.cos(angle_radians) * 200 * dt
        force_y = math.sin(angle_radians) * 200 * dt
        ship_sprite.update(x=ship_sprite.x + force_x, y=ship_sprite.y + force_y)

    for asteroid in asteroid_swarm:
        angle_radians = math.radians(asteroid.rotation)
        force_x = math.cos(angle_radians) * 40 * dt
        force_y = math.sin(angle_radians) * 40 * dt
        asteroid.update(x=asteroid.x + force_x, y=asteroid.y + force_y)

    for laser in lasers:
        angle_radians = math.radians(90 - ship_sprite.rotation)
        force_x = math.cos(angle_radians) * 170
        force_y = math.sin(angle_radians) * 170
        laser.update(x=ship_sprite.x + force_x, y=ship_sprite.y + force_y)


pyglet.clock.schedule_interval(update, 1 / 120.0)


def on_draw():
    global LIVES, ALIVE, lasers

    if ALIVE:
        background_sprite.draw()
        ship_sprite.draw()
        score_label.draw()
        lives_label.draw()

        for laser in lasers:
            laser.draw()
            for ast in asteroid_swarm:
                asteroid_hit = overlaps_asteroids(ast, laser)
                if asteroid_hit:
                    print("HIT")

        for asteroid in asteroid_swarm:
            asteroid.draw()

            overlap = overlaps(ship_sprite, asteroid)

            if overlap:
                boom_sound = pyglet.media.load('Sounds/boom.wav')
                boom_sound.play()
                ship_sprite.update(x=window.width / 2, y=40, rotation=0)

                if LIVES > 0:
                    LIVES -= 1
                    lives_label.text = "Lives: {0}".format(LIVES)
                else:
                    ALIVE = False
    else:
        gameover_label = pyglet.text.Label(text="GAME OVER", x=window.width/2-130, y=window.height/2, group=foreground)
        gameover_label.font_size = 30
        gameover_label.draw()


window.push_handlers(
    on_text=update,
    on_draw=on_draw,
)

pyglet.app.run()
