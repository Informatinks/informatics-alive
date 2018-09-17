from rmatics import create_app
from rmatics.websocket import socket


application = create_app()


if __name__ == '__main__':
    socket.run(
        application,
        host='0.0.0.0',
        port=6349,
        debug=True
    )
