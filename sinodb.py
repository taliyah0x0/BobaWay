from db import DB


class SinoDB(DB):
  def __init__(self):
    super().__init__()
    self.connect()

  def get_user_by_username(self, username):
    return self.execute("SELECT * FROM admins WHERE username = %s", (username,))

  def get_user_by_id(self, id):
    return self.execute("SELECT * FROM admins WHERE id = %s", (id,))

  def create_user(self, username, password):
    return self.execute("INSERT INTO admins (username, password) VALUES (%s, %s)", (username, password))
  
  
