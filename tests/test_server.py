# coding=utf-8

import errno
from io import BytesIO

import pytest

from ascii_telnet.ascii_server import TelnetRequestHandler, ThreadedTCPServer


class FakePlayer:
    def __init__(self):
        self.stopped = False

    def stop(self):
        self.stopped = True


class BrokenPipeWriter:
    def write(self, _data):
        raise BrokenPipeError(errno.EPIPE, "broken pipe")


class ResetWriter:
    def write(self, _data):
        raise ConnectionResetError(errno.ECONNRESET, "connection reset")


class OtherErrorWriter:
    def write(self, _data):
        raise OSError(errno.EIO, "io error")


def make_handler(writer):
    handler = object.__new__(TelnetRequestHandler)
    handler.wfile = writer
    handler.player = FakePlayer()
    return handler


def test_threaded_server_uses_daemon_threads_and_reusable_address():
    assert ThreadedTCPServer.daemon_threads is True
    assert ThreadedTCPServer.allow_reuse_address is True


@pytest.mark.parametrize("writer", [BrokenPipeWriter(), ResetWriter()])
def test_draw_frame_stops_player_on_disconnect(writer):
    handler = make_handler(writer)

    handler.draw_frame(BytesIO(b"frame"))

    assert handler.player.stopped is True


def test_draw_frame_reraises_unexpected_socket_errors():
    handler = make_handler(OtherErrorWriter())

    with pytest.raises(OSError):
        handler.draw_frame(BytesIO(b"frame"))
