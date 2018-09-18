from flask import (
    g,
)
from flask_socketio import (
    join_room,
    SocketIO,
)

from rmatics.view import load_user


socket = SocketIO()


def user_room(user_id):
    return f'user:{user_id}'


def notify_all(*args, **kwargs):
    socket.emit(*args, **kwargs)


def notify_user(user_id, *args, **kwargs):
    kwargs['room'] = user_room(user_id)
    socket.emit(*args, **kwargs)


@socket.on('connect')
def connect():
    load_user()
    if g.user:
        join_room(user_room(g.user.id))
