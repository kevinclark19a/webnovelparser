
from wsgiref.simple_server import make_server


def __app(environ, start_response):
    pass


def start():
    with make_server('', 8000, __app) as httpd:
        httpd.serve_forever()