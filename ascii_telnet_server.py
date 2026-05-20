# coding=utf-8
#!/usr/bin/env python3

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Copyright (c) 2008, Martin W. Kirst All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  Redistributions of source code must retain the above copyright notice,
#  this list of conditions and the following disclaimer.
#  Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
#  TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#  PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
#  TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
  ASCII art movie Telnet player.
  Version         : 0.1

  Can stream an ~20 minutes ASCII movie via Telnet emulation
  as stand alone server or via xinetd daemon.
  Tested with Python 3.10+

  Original art work : Simon Jansen ( http://www.asciimation.co.nz/ )
  Telnetification
  & Player coding   : Martin W. Kirst ( https://github.com/nitram509/ascii-telnet-server )
  Python3 Update: Ryan Jarvis

"""
import argparse
import os
import sys

from ascii_telnet.ascii_movie import Movie
from ascii_telnet.ascii_player import VT100Player
from ascii_telnet.ascii_server import TelnetRequestHandler, ThreadedTCPServer


DEFAULT_INTERFACE = "127.0.0.1"
DEFAULT_PORT = 2323


def run_tcp_server(interface, port, filename):
    """
    Start a TCP server that a client can connect to that streams the output of
     Ascii Player

    Args:
        interface (str):  bind to this interface
        port (int): bind to this port
        filename (str): file name of the ASCII movie
    """
    TelnetRequestHandler.filename = filename
    with ThreadedTCPServer((interface, port), TelnetRequestHandler) as server:
        server.serve_forever()


def run_stdout(filepath, output=None):
    """
    Stream the output of the Ascii Player to STDOUT
    Args:
        filepath (str): file path of the ASCII movie
    """
    output = output or sys.stdout

    def draw_frame_to_stdout(screen_buffer):
        output.write(screen_buffer.read().decode("iso-8859-15"))

    movie = Movie()
    movie.load(filepath)
    player = VT100Player(movie)
    player.draw_frame = draw_frame_to_stdout
    player.play()


def build_parser():
    parser = argparse.ArgumentParser(
        prog="ascii-telnet-server",
        description="Stream an encoded ASCII movie as VT100 output.",
    )
    parser.add_argument(
        "--standalone",
        dest="tcpserv",
        action="store_true",
        help="run as a standalone multi-threaded TCP server",
    )
    parser.add_argument(
        "--stdout",
        dest="tcpserv",
        action="store_false",
        help="write VT100 output to stdout, for example under xinetd/systemd socket activation",
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="filename",
        metavar="FILE",
        required=True,
        help="text file containing the ASCII movie",
    )
    parser.add_argument(
        "-i",
        "--interface",
        default=DEFAULT_INTERFACE,
        help="interface to bind in standalone mode; use 0.0.0.0 to expose it publicly",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=DEFAULT_PORT,
        type=int,
        metavar="PORT",
        help="port to bind in standalone mode",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=True,
        help="print startup messages",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="suppress startup messages",
    )
    parser.set_defaults(tcpserv=True)
    return parser


def main(argv=None):
    parser = build_parser()
    options = parser.parse_args(argv)

    if not os.path.exists(options.filename):
        parser.error("file not found: {0}".format(options.filename))

    try:
        if options.tcpserv:
            if options.verbose:
                print("Running TCP server on {0}:{1}".format(options.interface, options.port))
                print("Playing movie {0}".format(options.filename))
            run_tcp_server(options.interface, options.port, options.filename)
        else:
            run_stdout(options.filename)
    except KeyboardInterrupt:
        print("Ascii Player Quit.")
        return 130
    return 0


# Backward-compatible names for callers using the original script API.
runTcpServer = run_tcp_server
runStdOut = run_stdout


if __name__ == "__main__":
    sys.exit(main())
