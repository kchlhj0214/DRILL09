"""창을 띄우지 않고 방향 입력과 캐릭터 동작을 검증한다."""
import math
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import drill09_submission as game


def key_event(key, down=True):
    return SimpleNamespace(type=game.SDL_KEYDOWN if down else game.SDL_KEYUP, key=key)


class CharacterTests(unittest.TestCase):
    def setUp(self):
        self.boy = game.Character()

    def test_initial_idle(self):
        self.assertEqual((self.boy.x, self.boy.y), (640, 512))
        self.assertEqual(self.boy.facing, 'right')
        self.assertFalse(self.boy.moving)

    def test_all_eight_directions_have_equal_speed(self):
        for horizontal in [None, game.SDLK_LEFT, game.SDLK_RIGHT]:
            for vertical in [None, game.SDLK_UP, game.SDLK_DOWN]:
                if horizontal is None and vertical is None:
                    continue
                with self.subTest(horizontal=horizontal, vertical=vertical):
                    boy = game.Character()
                    boy.pressed_keys = {key for key in [horizontal, vertical] if key is not None}
                    boy.update()
                    self.assertAlmostEqual(math.hypot(boy.x - 640, boy.y - 512), 5)
                    self.assertEqual(boy.x < 640, horizontal == game.SDLK_LEFT)
                    self.assertEqual(boy.x > 640, horizontal == game.SDLK_RIGHT)
                    self.assertEqual(boy.y > 512, vertical == game.SDLK_UP)
                    self.assertEqual(boy.y < 512, vertical == game.SDLK_DOWN)
                    self.assertTrue(boy.moving)

    def test_vertical_and_idle_preserve_facing(self):
        for key, facing in [(game.SDLK_LEFT, 'left'), (game.SDLK_RIGHT, 'right')]:
            self.boy.pressed_keys = {key}
            self.boy.update()
            for keys in [{game.SDLK_UP}, {game.SDLK_DOWN}, set()]:
                self.boy.pressed_keys = keys
                self.boy.update()
                self.assertEqual(self.boy.facing, facing)

    def test_partial_release_and_repeated_keydown(self):
        game.handle_events(self.boy, [key_event(game.SDLK_RIGHT)] * 3 + [key_event(game.SDLK_UP)])
        self.boy.update()
        previous_x, previous_y = self.boy.x, self.boy.y
        game.handle_events(self.boy, [key_event(game.SDLK_RIGHT, False)])
        self.boy.update()
        self.assertEqual(self.boy.x, previous_x)
        self.assertEqual(self.boy.y, previous_y + 5)
        game.handle_events(self.boy, [key_event(game.SDLK_UP, False)])
        self.boy.update()
        self.assertFalse(self.boy.moving)

    def test_opposite_keys_cancel_and_resume(self):
        self.boy.pressed_keys = {game.SDLK_LEFT, game.SDLK_RIGHT, game.SDLK_UP, game.SDLK_DOWN}
        self.boy.update()
        self.assertEqual((self.boy.x, self.boy.y), (640, 512))
        self.assertFalse(self.boy.moving)
        game.handle_events(self.boy, [key_event(game.SDLK_DOWN, False)])
        self.boy.update()
        self.assertEqual((self.boy.x, self.boy.y), (640, 517))

    def test_all_corners_clamp_and_allow_return(self):
        for x, horizontal, inward in [(50, game.SDLK_LEFT, game.SDLK_RIGHT),
                                      (1230, game.SDLK_RIGHT, game.SDLK_LEFT)]:
            for y, vertical in [(50, game.SDLK_DOWN), (974, game.SDLK_UP)]:
                with self.subTest(x=x, y=y):
                    self.boy.x, self.boy.y = x, y
                    self.boy.pressed_keys = {horizontal, vertical}
                    for _ in range(20):
                        self.boy.update()
                    self.assertEqual((self.boy.x, self.boy.y), (x, y))
                    self.assertFalse(self.boy.moving)
                    self.boy.pressed_keys = {inward}
                    self.boy.update()
                    self.assertTrue(self.boy.moving)

    def test_overshoot_and_wall_sliding(self):
        self.boy.x, self.boy.y = 1229, 973
        self.boy.pressed_keys = {game.SDLK_RIGHT, game.SDLK_UP}
        self.boy.update()
        self.assertEqual((self.boy.x, self.boy.y), (1230, 974))
        self.boy.y = 512
        self.boy.update()
        self.assertEqual(self.boy.x, 1230)
        self.assertGreater(self.boy.y, 512)
        self.assertTrue(self.boy.moving)

    def test_mouse_ignored_and_focus_loss_stops_movement(self):
        game.handle_events(self.boy, [SimpleNamespace(type=game.SDL_MOUSEMOTION, x=0, y=0)])
        self.assertEqual((self.boy.x, self.boy.y), (640, 512))
        game.handle_events(self.boy, [key_event(game.SDLK_LEFT)], focused=False)
        self.boy.update()
        self.assertEqual((self.boy.x, self.boy.y), (640, 512))

    def test_exit_events(self):
        for event in [key_event(game.SDLK_ESCAPE), SimpleNamespace(type=game.SDL_QUIT)]:
            self.assertFalse(game.handle_events(self.boy, [event]))

    def test_animation_rows(self):
        for moving, facing, row in [(True, 'left', 0), (True, 'right', 1),
                                    (False, 'left', 2), (False, 'right', 3)]:
            self.boy.moving, self.boy.facing = moving, facing
            image = Mock()
            self.boy.draw(image)
            self.assertEqual(image.clip_draw.call_args.args, (0, row * 100, 100, 100, 640, 512))

    def test_idle_frame_timing_and_wrap(self):
        for tick in range(1, 81):
            self.boy.update()
            self.assertEqual(self.boy.frame, (tick // 5) % 8)

    def test_animation_change_restarts_and_holds_first_frame(self):
        self.boy.frame = 6
        self.boy.pressed_keys = {game.SDLK_LEFT}
        self.boy.update()
        self.assertEqual(self.boy.frame, 0)
        for _ in range(4):
            self.boy.update()
            self.assertEqual(self.boy.frame, 0)
        self.boy.update()
        self.assertEqual(self.boy.frame, 1)

    def test_canvas_closes_on_image_error(self):
        with patch.object(game, 'open_canvas'), patch.object(game, 'close_canvas') as close:
            with patch.object(game, 'load_image', side_effect=RuntimeError('이미지 오류')):
                with self.assertRaises(RuntimeError):
                    game.main()
            close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
