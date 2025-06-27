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
  
  def get_master_key(self):
    return self.execute("SELECT password FROM admins WHERE username = %s", ("master",))[0][0]

  def get_entry_by_hanzi_and_roman(self, language, hanzi, roman):
    return self.execute("SELECT * FROM %s WHERE hanzi = %s AND roman = %s", (language, hanzi, roman))
  
  def create_translation_entry(self, language, hanzi, roman):
    return self.execute("INSERT INTO %s (hanzi, roman) VALUES (%s, %s)", (language, hanzi, roman))
  
  def update_translation_entry(self, language, hanzi, roman):
    return self.execute("UPDATE %s SET roman = %s WHERE hanzi = %s", (language, roman, hanzi))
  
  def delete_translation_entry(self, language, hanzi, roman):
    return self.execute("DELETE FROM %s WHERE hanzi = %s AND roman = %s", (language, hanzi, roman))