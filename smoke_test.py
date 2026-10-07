"""실제 pico2d 캔버스와 SDL 이벤트로 실행한다: python smoke_test.py"""
import ctypes
from unittest.mock import patch

import character_runs_esc as game


def run_smoke_test(exit_type):
    original_get_events = game.get_events
    original_draw = game.Character.draw
    states = []
    schedule = {
        1: [(game.SDL_KEYDOWN, game.SDLK_LEFT)],
        15: [(game.SDL_KEYDOWN, game.SDLK_UP)],
        30: [(game.SDL_KEYUP, game.SDLK_LEFT)],
        45: [(game.SDL_KEYUP, game.SDLK_UP)],
        60: [(game.SDL_KEYDOWN, game.SDLK_RIGHT)],
        75: [(game.SDL_KEYUP, game.SDLK_RIGHT)],
        90: [(exit_type, game.SDLK_ESCAPE)],
    }
    tick = 0

    def next_events():
        nonlocal tick
        for event_type, key in schedule.get(tick, []):
            event = game.SDL_Event()
            event.type = event_type
            if event_type in (game.SDL_KEYDOWN, game.SDL_KEYUP):
                event.key.keysym.sym = key
                event.key.repeat = 0
            assert game.SDL_PushEvent(ctypes.byref(event)) == 1
        tick += 1
        return original_get_events()

    def record_draw(character, image):
        original_draw(character, image)
        states.append((character.x, character.y, character.facing,
                       character.moving, character.frame))

    # 운영체제의 다른 창 포커스와 무관하게 합성 입력을 검증한다.
    with patch.object(game, 'get_events', next_events), \
            patch.object(game.Character, 'draw', record_draw), \
            patch.object(game, 'SDL_GetKeyboardFocus', return_value=True):
        game.main()

    assert len(states) == 90, len(states)
    assert states[0][:4] == (640, 512, 'right', False)
    assert states[14][0] < states[0][0]
    assert states[29][0] < states[14][0] and states[29][1] > states[14][1]
    assert states[44][0] == states[29][0] and states[44][1] > states[29][1]
    assert states[44][2] == 'left'
    assert states[59][2:4] == ('left', False)
    assert states[74][2:4] == ('right', True)
    assert states[89][2:4] == ('right', False)
    assert len({state[4] for state in states[45:60]}) > 1
    print('실제 캔버스 90프레임, SDL 입력, 네 애니메이션 상태, 종료 검증 통과')


if __name__ == '__main__':
    run_smoke_test(game.SDL_KEYDOWN)
    run_smoke_test(game.SDL_QUIT)
