import pgzrun

WIDTH = 800
HEIGHT = 600
TITLE = "Tiny Dugeon"

BLACK = (0, 0, 0)

player = None


def draw():
    screen.fill(BLACK)
    if player:
        player.draw()


def init_game():
    global player
    player = Actor("player")
    player.pos = (WIDTH // 2, HEIGHT // 2)


init_game()

pgzrun.go()
