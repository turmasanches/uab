from app import criar_app
from config import Config

app = criar_app()

if __name__ == '__main__':
    app.run(debug=Config.DEBUG_MODE, host='0.0.0.0', port=5000)
