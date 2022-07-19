from flask import Flask, flash
from flask_login import LoginManager


from uuid import uuid4

import os

from instaclone.db import user_from_db_to_obj

# ---------------------------------------------------------------------------- #
#                       Initialization and configuration                       #
# ---------------------------------------------------------------------------- #
# ---------------------------- App initialization ---------------------------- #
app = Flask(__name__)

# --------------------- Secret key for session management -------------------- #
secret_key = uuid4().hex
app.secret_key = secret_key



# ---------------------------------------------------------------------------- #
#                               Webapp functions                               #
# ---------------------------------------------------------------------------- #

# ------------------------------ Upload settings ----------------------------- #
app.config['UPLOAD_TYPES'] = set(['bmp', 'png', 'jpg', 'jpeg', 'gif', 'tiff'])
app.config['UPLOAD_FOLDER'] = '.\\uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# -------------------- To allow local testing without SSL -------------------- #
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# ----------------------- Login manager initialization ----------------------- #
app.config['TESTING'] = False
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return user_from_db_to_obj(user_id)



