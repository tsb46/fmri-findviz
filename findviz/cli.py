import os
import socket
import webbrowser

from threading import Timer

from findviz import create_app


def find_free_port():
    """Find an available port on the system."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # Bind to any available port
        return s.getsockname()[1]  # Return the port number


def open_browser(port):
    """Open the web browser to the Flask app."""
    webbrowser.open_new(f"http://127.0.0.1:{port}")


def main():
    app = create_app()

    # Dynamically find an available port
    port = find_free_port()

    # only open browser after server has started (give 1 sec)
    Timer(1, open_browser, args=(port,)).start()

    # Run the Flask app on the available port
    app.run(debug=False, port=port)
