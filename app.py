from flask import *
import main
import user
import bucket
import admin
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = 'bsdajvkbakjbfoehihewrpqkldn21pnifninelfbBBOIQRqnflsdnljneoBBOBi2rp1rp12r9uh'

app.register_blueprint(main.blueprint)
app.register_blueprint(user.blueprint)
app.register_blueprint(bucket.blueprint)
app.register_blueprint(admin.blueprint)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
