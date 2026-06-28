from app import app
from config import WEB_PORT
from wsgiref.simple_server import make_server


def server(wsgi_app):
    serverd = make_server("", WEB_PORT, wsgi_app)
    print(f'Serving HTTP on port {WEB_PORT}...')
    serverd.serve_forever()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=WEB_PORT)
    #server(app)