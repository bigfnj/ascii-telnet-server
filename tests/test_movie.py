# coding=utf-8

from ascii_telnet.ascii_movie import Movie


def write_movie(path, frames):
    lines = []
    for display_time, frame_lines in frames:
        lines.append(str(display_time))
        lines.extend(frame_lines)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_movie_load_parses_encoded_frames(tmp_path):
    movie_path = tmp_path / "movie.txt"
    write_movie(
        movie_path,
        [
            (2, ["FIRST"] + [""] * 12),
            (3, ["SECOND"] + [""] * 12),
        ],
    )

    movie = Movie(width=80, height=24)

    assert movie.load(str(movie_path)) is True
    assert movie.load(str(movie_path)) is False
    assert len(movie.frames) == 2
    assert [frame.display_time for frame in movie.frames] == [2, 3]
    assert len(movie.frames[0].data) == 13
    assert movie.frames[0].data[0].rstrip().endswith("FIRST")
    assert len(movie.frames[0].data[0]) == movie.left_margin + movie._frame_width


def test_movie_defaults_to_placeholder_frame_before_load():
    movie = Movie()

    assert len(movie.frames) == 1
    assert movie.frames[0].display_time == 1
    assert movie.frames[0].data == ["No movie yet loaded."]
