# import google cloud datastore
from google.cloud import datastore
from instaclone.models import User
# Initialize datastore client
db = datastore.Client()
# -------------------------------- User ------------------------------- #
def add_user_to_datastore(user_dict):
    # check whether user exists
    user = get_user_from_datastore_by_email(user_dict['email'])
    if user is None:
        # add user to datastore
        key = db.key('User')
        entity = datastore.Entity(key)
        entity.update(user_dict)
        db.put(entity)
        return entity.key.id
    else:
        return user.id


def get_user_from_datastore_by_id(id):
    # Get user from datastore by datastore id
    # returns None if user does not exist
    # returns datastore entity if user exists
    key = db.key('User', int(id))
    result = db.get(key)
    if result is None:
        return None
    if len(result) == 0:
        return None
    return result

def get_user_from_datastore_by_email(email):
    # Get user from datastore by email
    # returns None if user does not exist
    # returns datastore entity if user exists
    query = db.query(kind='User')
    query.add_filter('email', '=', email)
    results = list(query.fetch())
    if len(results) == 0:
        return None
    return results[0]

def usr_obj_from_datastore_by_id(id): 
    # Get user from datastore by datastore id
    key = db.key('User', int(id))
    result = db.get(key)
    if result is None:
        return None
    if len(result) == 0:
        return None
    user = User(result.id, result['email'], result['name'], result['pfp'])
    return user

def usr_obj_from_datastore_by_email(email):
    # Get user from datastore by email
    query = db.query(kind='User')
    query.add_filter('email', '=', email)
    results = list(query.fetch())
    if len(results) == 0:
        return None
    user = User(results[0].id, results[0]['email'], results[0]['name'], results[0]['pfp'])
    return user

def get_all_users():
    query = db.query(kind='User')
    results = list(query.fetch())
    return results

# -------------------------------- Photo creation ------------------------------- #
def add_photo_to_user(user_id,url,private,caption):
    # get user from datastore
    entity = get_user_from_datastore_by_id(user_id)
    # add photo to "photos" list in user entity
    if 'photos' not in entity:
        entity['photos'] = [{'url':url,'private':private,'caption':caption}]
    else:
        entity['photos'].append({'url':url,'private':private,'caption':caption})
    # update datastore
    db.put(entity)
    # return dict of updated user
    return dict(entity)
# ------------------------------- Photo access ------------------------------- #
def get_photos_from_user(user_id):
    # get user from datastore
    entity = get_user_from_datastore_by_id(user_id)
    # entity to dict
    entity_dict = dict(entity)
    # return photos list
    return entity_dict['photos']

def get_public_photos_from_user(user_id):
    # get user from datastore
    entity = get_user_from_datastore_by_id(user_id)
    # entity to dict
    entity_dict = dict(entity)
    # return photos list
    return [photo for photo in entity_dict['photos'] if photo['private'] == 'False']

def get_all_public_photos():
    all_users = get_all_users()
    all_public_photos = []
    for user in all_users:
        all_public_photos.extend(get_public_photos_from_user(user.id))
    return all_public_photos

# ------------------------------ Photo deletion ------------------------------ #

def delete_photo_from_user(user_id,photo_url):
    # get user from datastore
    entity = get_user_from_datastore_by_id(user_id)
    # remove photo from "photos" list in user entity
    entity['photos'] = [photo for photo in entity['photos'] if photo['url'] != photo_url]
    # update datastore
    db.put(entity)
    # return dict of updated user
    return dict(entity)

# ------------------------------- Photo update ------------------------------- #
def update_photo_of_user(user_id,photo_url,caption,private):
    # get user from datastore
    entity = get_user_from_datastore_by_id(user_id)
    # update photo in "photos" list in user entity
    for photo in entity['photos']:
        if photo['url'] == photo_url:
            photo['caption'] = caption
            photo['private'] = private
    # update datastore
    db.put(entity)
    # return dict of updated user
    return dict(entity)

