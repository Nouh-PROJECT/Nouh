from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, name, user_id):
        self.id = id
        self.name = name
        self.user_id = user_id
    