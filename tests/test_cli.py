# coding=utf-8

import pytest

import ascii_telnet_server


def test_parser_defaults_to_local_non_privileged_server():
    args = ascii_telnet_server.build_parser().parse_args(["-f", "movie.txt"])

    assert args.tcpserv is True
    assert args.interface == ascii_telnet_server.DEFAULT_INTERFACE
    assert args.port == ascii_telnet_server.DEFAULT_PORT


def test_parser_stdout_mode():
    args = ascii_telnet_server.build_parser().parse_args(["--stdout", "-f", "movie.txt"])

    assert args.tcpserv is False


def test_main_rejects_missing_movie_file():
    with pytest.raises(SystemExit) as excinfo:
        ascii_telnet_server.main(["--stdout", "-f", "does-not-exist.txt"])

    assert excinfo.value.code == 2


def test_main_runs_stdout_mode(monkeypatch, tmp_path):
    movie = tmp_path / "movie.txt"
    movie.write_text("1\n" + "\n".join([""] * 13) + "\n", encoding="utf-8")
    calls = []

    monkeypatch.setattr(ascii_telnet_server, "run_stdout", lambda filename: calls.append(filename))

    assert ascii_telnet_server.main(["--stdout", "-f", str(movie)]) == 0
    assert calls == [str(movie)]


def test_main_runs_server_mode(monkeypatch, tmp_path):
    movie = tmp_path / "movie.txt"
    movie.write_text("1\n" + "\n".join([""] * 13) + "\n", encoding="utf-8")
    calls = []

    def fake_server(interface, port, filename):
        calls.append((interface, port, filename))

    monkeypatch.setattr(ascii_telnet_server, "run_tcp_server", fake_server)

    assert ascii_telnet_server.main(["-f", str(movie), "-i", "0.0.0.0", "-p", "2525"]) == 0
    assert calls == [("0.0.0.0", 2525, str(movie))]
