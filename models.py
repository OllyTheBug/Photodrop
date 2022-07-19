from flask_login import UserMixin

# Uses email as the id because each account is tied to a google account
class User(UserMixin):
    def __init__(self, email, name, picture):
        self.email = email
        self.name = name
        self.picture = picture
    def is_authenticated(self):
        return False
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.email

