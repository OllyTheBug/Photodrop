from flask import render_template, request, redirect, url_for, flash, send_from_directory, Blueprint, current_app
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient
from werkzeug.utils import secure_filename
import requests
import json
import base64
import imghdr
import os
from uuid import uuid4

# Local imports
from instaclone.db import add_user_to_datastore, usr_obj_from_datastore_by_id, add_photo_to_user, get_user_from_datastore_by_id, get_photos_from_user

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
    # log current user
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
    oauth_webapp_client.parse_request_body_response(
        json.dumps(token_response.json()))

# ------------------------ Get user info from Google. ------------------------ #
    userinfo_endpoint = get_google_cfg()['userinfo_endpoint']
    uri, headers, body = oauth_webapp_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # Check that the email is verified then pull user info.
    if userinfo_response.json().get("email_verified"):
        users_email = userinfo_response.json()["email"]
        pfp = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

# ----------- Create dict of user info to add to database document ----------- #
    user_dict = {
        'email': users_email,
        'pfp': pfp,
        'name': users_name
    }
    id = add_user_to_datastore(user_dict)

# ----------------------- Login user using flask-login ----------------------- #
    user = usr_obj_from_datastore_by_id(id)
    login_user(user)
    return redirect(url_for('views.render_index'))


@views.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.render_index'))

# ------------------------------- Route upload ------------------------------- #


@views.route('/photos', methods=['PUT'])
@login_required
def upload_file():
    # ------- Get caption, private status, and image in base64 from request ------ #
    r_json = request.get_json()
    photo_base64 = r_json['base64']
    caption = r_json['caption']
    private = r_json['private']
# ------------- Check that photo_base64 is not empty ------------- #
    if photo_base64 == '':
        return "Error: No photo uploaded.", 400
# ----------------------------- Parse image data ----------------------------- #
    # String is in the form "data:image/<ext>;base64,<image data>"
    try:
        filetype = photo_base64.split(';')[0].split('/')[1]
    except ValueError:
        return "Error: Invalid format.", 400
# ---------------------- Check that filetype is allowed ---------------------- #
    if filetype not in current_app.config['UPLOAD_TYPES']:
        return "Error: Filetype not allowed.", 400
# ---------------------- Convert base64 to image binary ---------------------- #
    image_data = photo_base64.split(';base64,')[1]
    image_data = image_data.encode('utf-8')
    image_data = base64.b64decode(image_data)
# -------------------------- Save image data to file ------------------------- #
    filename = str(uuid4()) + '.' + filetype
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'wb') as f:
        f.write(image_data)
# --------------- Verify filetype with imghdr to prevent fires --------------- #
    if imghdr.what(filepath) not in current_app.config['UPLOAD_TYPES']:
        return "Error: Filetype not allowed.", 400
    current_app.logger.info('Saved file to: ' + filepath)
# --------------------------- Add photo to database --------------------------- #
    add_photo_to_user(current_user.id, f'photos\\{filename}', private, caption)
# ---------------------------- return 200 --------------------------- #
    return 'Upload successful', 200


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
    # convert list of entities to list of dicts
    photos = [dict(photo) for photo in photos]
    return render_template('profile.html', photos=photos, user=current_user)

# ---------------------------- Route photo access ---------------------------- #

@views.route('/photos/<filename>', methods=['GET'])
def uploaded_file(filename):
    # send url for non-static folder uploads
    photo = send_from_directory('uploads', filename.rsplit('/')[-1])
    return photo

# --------------------------- Route photo deletion --------------------------- #


@views.route('/photos/<filename>', methods=['DELETE'])
@login_required
def delete_photo(url):
    current_app.logger.info(
        f'{current_user.name} is deleting photo {url}')
    # remove photo from database
    remove_photo_from_user(current_user.id, url)
    # delete photo from filesystem
    filename = url.rsplit('/')[-1]
    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return 'Photo deleted', 200

# ---------------------------- Route photo update ---------------------------- #
@views.route('/photos/<filename>', methods=['POST'])
@login_required
def update_photo(filename):
    current_app.logger.info(
        f'{current_user.name} is updating photo {filename}')
    index = request.args.get('index')
    r_json = request.form
    caption = r_json[f'caption{index}']
    private = r_json[f'private{index}']
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename.split('?')[0])
    update_photo_of_user(current_user.id, filepath, private, caption)
    return 'Photo updated', 200