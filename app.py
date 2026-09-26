from flask import Flask
from database import init_database
from routes import register_routes

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'buena-vista-gas-secret-key-2026'

init_database()
register_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
