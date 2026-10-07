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
        self.pressed_keys = set()
        self.frame = 0
        self.frame_tick = 0

    def update(self):
        dx = int(SDLK_RIGHT in self.pressed_keys) - int(SDLK_LEFT in self.pressed_keys)
        self.x += dx * MOVE_SPEED
        if self.frame_tick == 0:
            self.frame = (self.frame + 1) % FRAME_COUNT
        self.frame_tick = (self.frame_tick + 1) % FRAME_INTERVAL

    def draw(self, image):
        image.clip_draw(self.frame * FRAME_SIZE, FRAME_SIZE,
                        FRAME_SIZE, FRAME_SIZE, self.x, self.y)


def handle_events(character, events):
    for event in events:
        if event.type == SDL_QUIT:
            return False
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return False
        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
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
