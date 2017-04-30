from flask import Flask
from flask_socketio import SocketIO
import config

app = Flask(__name__,template_folder="templates",static_folder="static")
app.config['SECRET_KEY'] = 'secret'
async_mode	 = None
socketio = SocketIO(app,async_mode=async_mode)


from app import views