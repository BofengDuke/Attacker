from app import app
from app import socketio

# app.run(debug=True)
socketio.run(app,port=5000,debug=True)

