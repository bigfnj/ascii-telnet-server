# coding=utf-8

import pytest

from ascii_telnet.ascii_movie import Frame, Movie
from ascii_telnet.ascii_player import VT100Player


class CapturingPlayer(VT100Player):
    def __init__(self, movie):
        super().__init__(movie)
        self.buffers = []

    def draw_frame(self, screen_buffer):
        self.buffers.append(screen_buffer.read())


def make_movie():
    movie = Movie(width=20, height=8)
    frame = Frame(display_time=1)
    frame.data = ["HELLO"]
    movie.frames = [frame]
    movie.top_margin = 2
    return movie


def test_load_frame_writes_vt100_buffer_and_timebar():
    player = CapturingPlayer(make_movie())

    player._load_frame(player._movie.frames[0], 1)

    assert len(player.buffers) == 1
    assert player.buffers[0].startswith(VT100Player.CLEARSCRN.encode())
    assert b"\x1b[2;1HHELLO\r\n" in player.buffers[0]
    assert b"\x1b[8;1H<" in player.buffers[0]


def test_move_cursor_rejects_out_of_bounds_coordinates(capsys):
    player = CapturingPlayer(make_movie())

    assert player._move_cursor(1, 1) == b"\x1b[1;1H"
    assert player._move_cursor(0, 1) == b""
    assert player._move_cursor(21, 1) == b""
    assert player._move_cursor(1, 9) == b""
    assert "coordinates out of range" in capsys.readouterr().err


def test_base_draw_frame_requires_override():
    player = VT100Player(make_movie())

    with pytest.raises(NotImplementedError):
        player.draw_frame(None)
