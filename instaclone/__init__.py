from flask import Flask, flash
from flask_login import LoginManager


from uuid import uuid4

import os

from instaclone.db import user_obj_from_db_by_email

# ---------------------------------------------------------------------------- #
#                       Initialization and configuration                       #
# ---------------------------------------------------------------------------- #
# ---------------------------- App initialization ---------------------------- #
app = Flask(__name__)

# --------------------- Secret key for session management -------------------- #
secret_key = "testing secret key"
app.secret_key = secret_key



# ---------------------------------------------------------------------------- #
#                               Webapp functions                               #
# ---------------------------------------------------------------------------- #

# ------------------------------ Upload settings ----------------------------- #
app.config['UPLOAD_TYPES'] = set(['bmp', 'png', 'jpg', 'jpeg', 'gif', 'tiff'])
app.config['UPLOAD_FOLDER'] = 'instaclone\\uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# -------------------- To allow local testing without SSL -------------------- #
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# ----------------------- Login manager initialization ----------------------- #
app.config['TESTING'] = False
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return user_obj_from_db_by_email(user_id)



