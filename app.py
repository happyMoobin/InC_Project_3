from flask import *
import main
import user
import bucket
import admin

app = Flask(__name__)
app.secret_key = 'bsdajvkbakjbfoehihewrpqkldn21pnifninelfbBBOIQRqnflsdnljneoBBOBi2rp1rp12r9uh'

app.register_blueprint(main.blueprint)
app.register_blueprint(user.blueprint)
app.register_blueprint(bucket.blueprint)
app.register_blueprint(admin.blueprint)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
