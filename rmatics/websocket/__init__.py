from flask import (
    g,
)
from flask_socketio import (
    join_room,
    SocketIO,
)

from rmatics.utils.decorators import do_not_execute, deprecated
from rmatics.view import load_user


socket = SocketIO()


@deprecated()
@do_not_execute(return_value=None)
def user_room(user_id):
    return f'user:{user_id}'


@deprecated()
@do_not_execute(return_value=None)
def notify_all(*args, **kwargs):
    socket.emit(*args, **kwargs)


@deprecated()
@do_not_execute(return_value=None)
def notify_user(user_id, *args, **kwargs):
    kwargs['room'] = user_room(user_id)
    socket.emit(*args, **kwargs)


@socket.on('connect')
@deprecated()
@do_not_execute(return_value=None)
def connect():
    load_user()
    if g.user:
        join_room(user_room(g.user.id))
