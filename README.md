ASCII art movie Telnet player
=============================

Streams ASCII art movies as VT100 terminal output over a TCP socket or stdout.
The standalone server is useful for a local telnet-style demo; stdout mode can
be used by classic service managers such as xinetd or by scripts that want raw
terminal frames.

Screenshot:

<img src="screenshots/example.gif?raw=true" width=500>

Wanna see it in action? Just watch https://asciinema.org/a/3132


Tested with Python 3.10+

Original art work : Simon Jansen [http://www.asciimation.co.nz/](http://www.asciimation.co.nz/)  
Telnetification & Player coding : Martin W. Kirst  
Python3 Update: Ryan Jarvis

Install for development
-----------------------

Create a virtual environment, install the package in editable mode, and run the
tests:

    $ python3 -m venv .venv
    $ . .venv/bin/activate
    $ python -m pip install -e ".[dev]"
    $ python -m pytest

From Windows PowerShell with this repository in WSL:

    PS> wsl -e bash -lc "cd /home/bigfnj/projects/ascii-telnet-server && .venv/bin/python -m pytest"


Command line
------------

After installation, run:

    $ ascii-telnet-server --help
    usage: ascii-telnet-server [-h] [--standalone] [--stdout] -f FILE
                               [-i INTERFACE] [-p PORT] [-v] [-q]

    Stream an encoded ASCII movie as VT100 output.

    options:
      -h, --help            show this help message and exit
      --standalone          run as a standalone multi-threaded TCP server
      --stdout              write VT100 output to stdout, for example under
                            xinetd/systemd socket activation
      -f FILE, --file FILE  text file containing the ASCII movie
      -i INTERFACE, --interface INTERFACE
                            interface to bind in standalone mode; use 0.0.0.0
                            to expose it publicly
      -p PORT, --port PORT  port to bind in standalone mode
      -v, --verbose         print startup messages
      -q, --quiet           suppress startup messages

Standalone mode binds to `127.0.0.1:2323` by default.


Run as stand alone server
-------------------------

Run the console script with a sample movie file:

    $ ascii-telnet-server --standalone -f sample_movies/sw1.txt
    Running TCP server on 127.0.0.1:2323
    Playing movie sw1.txt
   
Then connect from another terminal:

    $ telnet 127.0.0.1 2323

To expose the demo publicly on the traditional telnet port, opt in explicitly:

    $ sudo ascii-telnet-server --standalone -i 0.0.0.0 -p 23 -f sample_movies/sw1.txt


Run to stdout
-------------

Stdout mode writes the raw VT100 frame stream:

    $ ascii-telnet-server --stdout -f sample_movies/short_intro.txt

From Windows PowerShell with this repository in WSL:

    PS> wsl -e bash -lc "cd /home/bigfnj/projects/ascii-telnet-server && .venv/bin/ascii-telnet-server --stdout -f sample_movies/short_intro.txt"


Legacy xinetd program
---------------------

If you still use xinetd, place this configuration into `/etc/xinetd.d/telnet`
and adjust paths for your installation:

    # default: on
    # description: An telnet service playing an ASCII movie, Star Wars Episode 4 
    service telnet
    {
            disable         = no
            socket_type     = stream
            protocol        = tcp
            port            = 23
            user            = root
            wait            = no
            instances       = 10
    
            log_type        = FILE /var/log/asciiplayer
            log_on_success  += PID HOST DURATION
            log_on_failure  = HOST
            server          = /opt/asciiplayer/.venv/bin/ascii-telnet-server
            server_args     = --stdout -f /opt/asciiplayer/sw1.txt
    }
