from math import hypot

from pico2d import *

TUK_WIDTH, TUK_HEIGHT = 1280, 1024
FRAME_SIZE = 100
FRAME_COUNT = 8
FRAME_INTERVAL = 5
LOOP_DELAY = 0.01
MOVE_SPEED = 5


class Character:
    def __init__(self):
        self.x, self.y = TUK_WIDTH / 2, TUK_HEIGHT / 2
        self.facing = 'right'
        self.moving = False
        self.pressed_keys = set()
        self.frame = 0
        self.frame_tick = 0

    def update(self):
        dx = int(SDLK_RIGHT in self.pressed_keys) - int(SDLK_LEFT in self.pressed_keys)
        dy = int(SDLK_UP in self.pressed_keys) - int(SDLK_DOWN in self.pressed_keys)
        if dx:
            self.facing = 'right' if dx > 0 else 'left'
        self.moving = bool(dx or dy)
        length = hypot(dx, dy)
        if length:
            self.x += dx / length * MOVE_SPEED
            self.y += dy / length * MOVE_SPEED
        half_size = FRAME_SIZE / 2
        self.x = max(half_size, min(self.x, TUK_WIDTH - half_size))
        if self.frame_tick == 0:
            self.frame = (self.frame + 1) % FRAME_COUNT
        self.frame_tick = (self.frame_tick + 1) % FRAME_INTERVAL

    def draw(self, image):
        row = (0 if self.moving else 2) + (1 if self.facing == 'right' else 0)
        image.clip_draw(self.frame * FRAME_SIZE, row * FRAME_SIZE,
                        FRAME_SIZE, FRAME_SIZE, self.x, self.y)


def handle_events(character, events):
    for event in events:
        if event.type == SDL_QUIT:
            return False
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return False
        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN):
            character.pressed_keys.add(event.key)
        elif event.type == SDL_KEYUP:
            character.pressed_keys.discard(event.key)
    return True


def main():
    open_canvas(TUK_WIDTH, TUK_HEIGHT)
    tuk_ground = load_image('TUK_GROUND.png')
    image = load_image('animation_sheet.png')
    character = Character()
    hide_cursor()
    while handle_events(character, get_events()):
        character.update()
        clear_canvas()
        tuk_ground.draw(TUK_WIDTH // 2, TUK_HEIGHT // 2)
        character.draw(image)
        update_canvas()
        delay(LOOP_DELAY)
    close_canvas()


if __name__ == '__main__':
    main()
