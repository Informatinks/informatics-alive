import short_url
from flask import current_app


_instance = short_url.UrlEncoder()


def init_app(app):
    global _instance
    _instance = short_url.UrlEncoder(
        alphabet=app.config.get('URL_ENCODER_ALPHABET')
    )


def encode(n):
    return _instance.encode_url(n)


def decode(url):
    return _instance.decode_url(url)
