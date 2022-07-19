# import pymongo
# from instaclone.models import User
# # -------------------------- Database initialization ------------------------- #
# MONGO_URI = "mongodb://ollythebug:qttZbrURvlEIWwZt@pport.2v20v.mongodb.net/?retryWrites=true&w=majority"
# dbclient = pymongo.MongoClient(MONGO_URI)
# db = dbclient.strings
# user_collection = db.users
# # ---------------------------------------------------------------------------- #
# #                              Database functions                              #
# # ---------------------------------------------------------------------------- #
# # --------------------------- Add user to database --------------------------- #
# def add_user(user_dict):
   
#     # Add the user to the database
#     inserted = user_collection.insert_one(user_dict)
#     _id = inserted.inserted_id
#     return _id

# def insert_string(string):
#     db.strings.insert_one({"string": string})
#     return db.strings.find_one({"string": string})

# # --------------------------- Get user from database ------------------------- #
# def user_from_db_to_obj(_id):
#     user = user_collection.find_one({"_id": _id})
#     return User(user["email"], user["name"], user["picture"])