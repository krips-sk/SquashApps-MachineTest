from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid
#import celicom.
#from .app.cura.user.service.user_service import save_new_user, get_all_users, get_a_user
#ßimport subprocess

#subprocess.call('/Users/mani/test/flask/web/run', shell=True)

# configuration
DEBUG = True



# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app)


if __name__ == '__main__':
    app.run()