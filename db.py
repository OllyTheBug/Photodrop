from google.cloud import firestore

from instaclone.models import User


db = firestore.Client(project='instaclone-356500')

def user_from_db_to_obj(email):
    user_dict = get_user_from_db(email)
    return User(user_dict['email'], user_dict['name'], user_dict['pfp'])

def get_user_from_db(email):
    doc_ref = db.collection('users').document(email)
    return doc_ref.get().to_dict()
    

def add_user_to_db(user_dict):
    # Add the user to the database or overwrite if already exists
    doc_ref = db.collection('users').document(user_dict['email'])
    doc_ref.set(user_dict)
    return doc_ref.get().to_dict()

def add_photo_to_user(user_email, url):
    # Get user document by email
    doc_ref = db.collection('users').document(user_email)
    # Update photos object with new photo
    doc_ref.update({'photos': firestore.ArrayUnion([url])})
    return doc_ref.get().to_dict()