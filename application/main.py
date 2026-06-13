from app import app
from config import WEB_PORT



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=WEB_PORT)
