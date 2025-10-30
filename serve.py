#!/usr/bin/env python3
"""
Simple local server helper for the lyric site.
- Serves the current directory on an available port (default 8000, falls back if in use)
- Opens the default browser to the served URL
- Use this for local testing. GitHub Pages still requires pushing to GitHub (static host).

Run: python serve.py
"""
import http.server
import socketserver
import socket
import webbrowser
import contextlib
import sys
from pathlib import Path

PORT_START = 8000
HOST = '0.0.0.0'

def find_free_port(start=8000, host='127.0.0.1'):
    port = start
    while port < 65535:
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                port += 1
    raise RuntimeError('No free port found')

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    start_port = PORT_START
    host_for_browser = 'localhost'
    try:
        port = find_free_port(start=start_port, host=host_for_browser)
    except RuntimeError:
        print('No free port found. Exiting.')
        sys.exit(1)

    handler = QuietHandler
    # Serve from the script's directory (project root)
    web_dir = Path(__file__).parent.resolve()
    try:
        # Python 3.7+: can set directory on handler
        httpd = socketserver.TCPServer((HOST, port), lambda *args, **kwargs: handler(*args, directory=str(web_dir), **kwargs))
    except TypeError:
        # fallback for older versions — chdir
        cwd = Path.cwd()
        try:
            import os
            os.chdir(str(web_dir))
            httpd = socketserver.TCPServer((HOST, port), handler)
        finally:
            os.chdir(str(cwd))

    url = f'http://{host_for_browser}:{port}/'
    print(f'Serving {web_dir} at {url}\nPress Ctrl+C to stop.')
    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
        httpd.server_close()
