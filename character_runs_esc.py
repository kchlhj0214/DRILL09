from pico2d import *

TUK_WIDTH, TUK_HEIGHT = 1280, 1024
FRAME_SIZE = 100
FRAME_COUNT = 8
FRAME_INTERVAL = 5
LOOP_DELAY = 0.01
MOVE_SPEED = 5
open_canvas(TUK_WIDTH, TUK_HEIGHT)
tuk_ground = load_image('TUK_GROUND.png')
character = load_image('animation_sheet.png')


# fill here

running = True

def handle_events():
    # fill here
    global running, x, y

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_MOUSEMOTION:
            x, y = event.x, TUK_HEIGHT - 1 - event.y
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
            


running = True
frame = 0
x, y = TUK_WIDTH // 2, TUK_HEIGHT // 2
hide_cursor()
frame_rate = 0

while running:
    clear_canvas()
    tuk_ground.draw(TUK_WIDTH // 2, TUK_HEIGHT // 2)
    character.clip_draw(frame * FRAME_SIZE, FRAME_SIZE, FRAME_SIZE, FRAME_SIZE, x, y)
    update_canvas()
    handle_events()
    if frame_rate % FRAME_INTERVAL == 0:
        frame = (frame + 1) % FRAME_COUNT
    frame_rate = (frame_rate + 1) % FRAME_INTERVAL
    delay(LOOP_DELAY)


close_canvas()
