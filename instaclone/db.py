# import google cloud datastore
from google.cloud import datastore
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



def get_user_from_datastore_by_email(email):
    # Get user from datastore by email
    query = db.query(kind='User')
    query.add_filter('email', '=', email)
    results = list(query.fetch())
    if len(results) == 0:
        return None
    return results[0]

def usr_obj_from_datastore_by_id(id): 
    # Get user from datastore by id
    query = db.query(kind='User')
    query.add_filter('id', '=', id)
    results = list(query.fetch())
    if len(results) == 0:
        return None
    user = User(results[0].id, results[0]['email'], results[0]['name'], results[0]['pfp'])
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

# -------------------------------- Photo access ------------------------------- #


from instaclone.models import User


