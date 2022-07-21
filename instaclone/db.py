from unicodedata import name
from google.cloud import firestore

from instaclone.models import User


db = firestore.Client(project='instaclone-356500')

# User_ID {
#     email,
#     id,
#     name,
#     pfp,
#     photos{
#         caption,
#         private,
#         url
#     }
# }


# ---------------------------------------------------------------------------- #
#                                User Management                               #
# ---------------------------------------------------------------------------- #

# -------------------------------- User access ------------------------------- #
def user_obj_from_db_by_email(email):
    user_dict = get_user_from_db_by_email(email)
    if user_dict:
        return User(user_dict['id'], user_dict['email'], user_dict['name'], user_dict['pfp'])
    else:
        None


def user_obj_from_db_by_id(id):
    user_dict = get_user_from_db_by_id(id)
    if user_dict:
        return User(user_dict['id'], user_dict['email'], user_dict['name'], user_dict['pfp'])
    else:
        return None


def get_user_from_db_by_email(email):
    doc_ref = db.collection('users').where('email', '==', email)
    return doc_ref.get()[0].to_dict()


def get_user_from_db_by_id(id):
    doc_ref = db.collection('users').document(id)
    return doc_ref.get().to_dict()

# ------------------------------- User creation/update ------------------------------ #

def add_user_to_db(user_dict):
    # Add the user to the database or overwrite if already exists
    doc_ref = db.collection('users').document(user_dict['id'])
    doc_ref.set(user_dict)
    return doc_ref.get().to_dict()

# ------------------------------- User Deletion ------------------------------ #

def delete_user_from_db(user_id):
    # Get user document by id
    doc_ref = db.collection('users').document(user_id)
    # Delete user
    doc_ref.delete()
    return 0


# ------------------------------ User and Photos ----------------------------- #

def add_photo_to_user(user_id, url, private, caption):
    # Get user document by email
    doc_ref = db.collection('users').document(user_id)
    # Update photos object with new photo and private status
    try:
        doc_ref = doc_ref.update({
            'photos': firestore.ArrayUnion([{'url': url, 'private': private, 'caption': caption}])})
        return 0
    except Exception as e:
        print(e)
        return -1


def get_photos_from_user(user_id):
    # Get user document by id
    doc_ref = db.collection('users').document(user_id)
    # Get photos object
    return doc_ref.get().to_dict()['photos']

# ------------------------------ Photo Deletion ------------------------------ #

def remove_photo_from_user(user_id, url):
    # Get user document by id
    doc_ref = db.collection('users').document(user_id)
    # Remove photo from photos object
    try:
        doc_ref = doc_ref.update({
            'photos': firestore.ArrayRemove([{'url': url}])})
        return 0
    except Exception as e:
        print(e)
        return -1

# ------------------------------- Photo Update ------------------------------- #

def update_photo_of_user(user_id, url, private, caption):
    # Get user document by id
    doc_ref = db.collection('users').document(user_id)
    # Update photo object with new private status and caption
    try:
        doc_ref = doc_ref.update({
            'photos': firestore.ArrayUnion([{'url': url, 'private': private, 'caption': caption}])})
        return 0
    except Exception as e:
        print(e)
        return -1