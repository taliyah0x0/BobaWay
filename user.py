from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, attributes):
        self.id = attributes[0]
        self.username = attributes[1]
        self.password = attributes[2]
        