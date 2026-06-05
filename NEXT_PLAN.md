# SSH Movie Jukebox + Creator Tools Plan

Status: planned, not implemented.

Baseline:

- Latest committed baseline before this plan: `c083c54 Modernize Python package and test coverage`
- Branch: `master`
- Remote default: `origin/master`
- AIU status at planning time: clean
- Test command: `.venv/bin/python -m pytest`

## Resume Prompt

Use this when picking up in a new session:

```text
Resume the SSH Movie Jukebox + Creator Tools plan for ascii-telnet-server. Read AGENTS.md first, confirm git status and AIU status, then implement NEXT_PLAN.md. Start with the SSH Movie Jukebox: bundled + local movie catalog, --movie, --list-movies, --random, --movie-dir, and README/tests/AIU updates. Then implement creator tools as separate follow-up features.
```

## Summary

Build two separate but compatible feature tracks:

- SSH Movie Jukebox: make movies playable by name from a bundled plus local catalog, so a normal SSH command can stream playback without knowing file paths.
- Creator Tools: add tooling for maintaining the existing text movie format first, then add GIF-to-movie conversion as a separate optional feature.

Target SSH usage:

```bash
ssh -t host 'ascii-telnet-server --stdout --movie sw1'
ssh -t host 'ascii-telnet-server --stdout --random'
ssh host 'ascii-telnet-server --list-movies'
```

Do not implement restricted SSH accounts or sshd `ForceCommand` in this phase. The chosen SSH model is normal remote shell command execution.

## Feature 1: SSH Movie Jukebox

Add a movie catalog resolver:

- Bundled movies live under package data, for example `ascii_telnet/movies/*.txt`.
- Keep existing `sample_movies/` as repo examples and development fixtures.
- Support host-local movies from `--movie-dir PATH` and `ASCII_TELNET_MOVIE_DIR`.
- Movie names are filename stems, for example `sw1`, `short_intro`, `rick_roll`.
- Local movies override bundled movies on name collisions.

Extend `ascii-telnet-server`:

- Keep `-f/--file` for explicit paths.
- Add `--movie NAME`.
- Add `--list-movies`.
- Add `--random`.
- Add `--movie-dir PATH`.
- Make `--file`, `--movie`, and `--random` mutually exclusive playback sources.
- Keep `--stdout --movie NAME` as the recommended SSH path.

Expected public commands:

```bash
ascii-telnet-server --stdout --movie sw1
ascii-telnet-server --standalone --movie sw1
ascii-telnet-server --list-movies
ascii-telnet-server --random
ascii-telnet-server --movie-dir /opt/ascii-movies --movie my_movie
ASCII_TELNET_MOVIE_DIR=/opt/ascii-movies ascii-telnet-server --stdout --movie my_movie
```

## Feature 2: Creator Text Tools

Add a separate creator CLI console script named `ascii-telnet-movie`.

Commands:

```bash
ascii-telnet-movie list
ascii-telnet-movie validate PATH
ascii-telnet-movie normalize INPUT --output OUTPUT
ascii-telnet-movie preview PATH
```

Behavior:

- `list` prints catalog movie names using the same resolver as playback.
- `validate` checks the current encoded text movie format: 14-line frame chunks, integer display-time line, and 13 visual lines per frame.
- `normalize` writes canonical UTF-8 text with complete 14-line frames.
- `preview` uses the existing stdout playback path for an explicit file.

## Feature 3: Optional GIF Conversion

Implement after the text tools, not as part of the first jukebox change.

Add optional dependency group:

```bash
pip install -e ".[creator]"
```

Command:

```bash
ascii-telnet-movie gif INPUT.gif --output OUTPUT.txt --width 67 --height 13 --fps 15
```

Behavior:

- Use Pillow as an optional dependency only.
- Convert GIF frames to grayscale ASCII.
- Map GIF frame durations to 15 FPS display-time units.
- Clamp frame display time to at least 1.
- Emit the existing 14-line frame format.
- Output must pass `ascii-telnet-movie validate`.

## Test Plan

Catalog tests:

- Lists bundled movies.
- Resolves bundled movie by name.
- Resolves local movie from `--movie-dir`.
- Resolves local movie from `ASCII_TELNET_MOVIE_DIR`.
- Local movie overrides bundled movie with same name.
- Invalid movie names and missing movies fail clearly.

CLI tests:

- `--movie`, `--file`, `--random`, and `--list-movies` argument behavior.
- SSH-style stdout command routes to `run_stdout`.
- Existing `-f/--file` behavior still works.

Creator text tests:

- Valid movie passes validation.
- Incomplete frame, non-integer delay, and wrong frame height fail validation.
- Normalize emits canonical UTF-8 text with complete 14-line frames.

GIF conversion tests:

- Small generated GIF converts to valid movie text.
- Frame duration metadata is clamped to at least 1.
- Output validates with the same validator.

Regression:

- `.venv/bin/python -m pytest` passes.
- `.venv/bin/python -m pip install -e ".[dev]"` passes.
- Optional `.[creator]` install passes when GIF conversion is included.
- AIU status is clean before final response.

## Implementation Notes

- Update `pyproject.toml` package data so bundled movies are included in editable and built installs.
- Prefer standard-library `importlib.resources` for bundled movie discovery.
- Add tests before or alongside catalog resolver implementation.
- Update README with SSH examples once `--movie`, `--random`, and `--list-movies` exist.
- Update AI_UNDERSTANDING sidecars for every tracked source/test/config file changed.

