from flask import render_template, request, redirect, url_for, flash, send_from_directory, Blueprint, current_app
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient
from werkzeug.utils import secure_filename
import requests
import json
import os
from uuid import uuid4

# Local imports
from instaclone.db import add_photo_to_user, add_user_to_db, user_obj_from_db_by_id, get_photos_from_user
from instaclone.helpers import check_filetype
from instaclone.models import User

views = Blueprint('views', __name__)

# ---------------------------------------------------------------------------- #
#                        Google authentication functions                       #
# ---------------------------------------------------------------------------- #

# ---------- Google login config DO NOT COMMIT TO PUBLIC REPOSITORY ---------- #
GOOGLE_CLIENT_ID = "797500935739-h3mv5fr7rfvbhkbttql6p07pc0575vqr.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

def get_google_cfg():
    try:
        GOOGLE_CFG = requests.get(GOOGLE_DISCOVERY_URL).json()
    except:
        GOOGLE_CFG = None
        flash('Error: Could not get Google configuration.')
    return GOOGLE_CFG

oauth_webapp_client = WebApplicationClient(GOOGLE_CLIENT_ID)

# ---------------------------------------------------------------------------- #
#                                  Route views                                 #
# ---------------------------------------------------------------------------- #

# -------------------------------- Route index ------------------------------- #
@views.route('/')
def render_index():
    #log current user
    return render_template('index.html', user=current_user)

# --------------------------- Route login and oauth -------------------------- #


@views.route('/login')
def login():
    google_cfg = get_google_cfg()
    # Get the authorization URL from the provider.
    auth_endpoint = google_cfg['authorization_endpoint']
    # Build request to get auth code.
    request_uri = oauth_webapp_client.prepare_request_uri(
        auth_endpoint,
        redirect_uri=request.base_url + "/callback",
        # Scope to get profile info and email
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@views.route('/login/callback')
def callback():
    # Get authorization code Google sent back.
    code = request.args.get('code')
    token_endpoint = get_google_cfg()['token_endpoint']
    # Build request to get access token.
    token_url, headers, body = oauth_webapp_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(token_url, headers=headers, data=body,
                                   auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET))
    # Parse token response.
    oauth_webapp_client.parse_request_body_response(json.dumps(token_response.json()))
    
# ------------------------ Get user info from Google. ------------------------ #
    userinfo_endpoint = get_google_cfg()['userinfo_endpoint']
    uri, headers, body = oauth_webapp_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # Check that the email is verified then pull user info.
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        pfp = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

# ----------- Create dict of user info to add to database document ----------- #
    user_dict = {
        'id' : unique_id,
        'email': users_email,
        'pfp': pfp,
        'name': users_name
    }
    add_user_to_db(user_dict)

# ----------------------- Login user using flask-login ----------------------- #
    user = user_obj_from_db_by_id(unique_id)
    login_user(user, remember=True)
    return redirect(url_for('views.render_index'))

@views.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.render_index'))

# ------------------------------- Route upload ------------------------------- #


@views.route('/upload', methods=['PUT'])
@login_required
def upload_file():
# ---------------------- Check whether file is submitted --------------------- #
    if 'file' not in request.files:
        flash('No file part')
        current_app.logger.error('No file part')
        return redirect(request.url)

# ------------------- Check whether file is unnamed somehow ------------------ #
    file = request.files['file']
    if file.filename == '': 
        flash('no file selected for uploading')
        current_app.logger.error('No file selected for uploading')
        return redirect(request.url)

# ----------------------- Sanitize filename and upload ----------------------- #
    if file and check_filetype(file.filename):
        current_app.logger.info('File is allowed')
        # Generate a unique filename
        filename = secure_filename(file.filename).split('.')[0] + '_' + str(uuid4().hex) + '.' + file.filename.split('.')[1]
        file.save(os.path.join('instaclone/uploads', filename)) 
        # check whether upload is private
        if request.args.get('private') == 'true':
            private = True
        else:
            private = False
        # add file to db
        url = url_for('views.uploaded_file', filename=filename)
        add_photo_to_user(current_user.id, url, private)
        return redirect(url_for('views.uploaded_file',
                                filename=filename))


@views.route('/upload', methods=['GET'])
@login_required
def upload_form():
    current_app.logger.info(current_user)
    return render_template('upload.html', user=current_user)

# Route user profile
@login_required
@views.route('/profile', methods=['GET'])
def profile():
    current_app.logger.info(f'{current_user.name} is viewing their profile')
    photos = get_photos_from_user(current_user.id)
    return render_template('profile.html', photos=photos, user=current_user)

# ------------------------------ TODO: Implement ----------------------------- #
@views.route('/photos/<filename>')
def uploaded_file(filename):
    # send url for non-static folder uploads
    photo = send_from_directory('uploads', filename.rsplit('/')[-1])
    return photo
    pass
