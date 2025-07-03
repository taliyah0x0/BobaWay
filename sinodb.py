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
    return self.execute(f"SELECT * FROM {language} WHERE hanzi = %s AND roman = %s", (hanzi, roman))
  
  def create_translation_entry(self, language, hanzi, roman):
    return self.execute(f"INSERT INTO {language} (hanzi, roman) VALUES (%s, %s)", (hanzi, roman))
  
  def update_translation_entry(self, language, hanzi, original_roman, new_roman):
    return self.execute(f"UPDATE {language} SET roman = %s WHERE hanzi = %s AND roman = %s", (new_roman, hanzi, original_roman))
  
  def delete_translation_entry(self, language, hanzi, roman):
    return self.execute(f"DELETE FROM {language} WHERE hanzi = %s AND roman = %s", (hanzi, roman))
  
  def fetch_all_entries(self, language):
    return self.execute(f"SELECT hanzi, roman FROM {language}")

  def get_romanization_mapping(self, language):
    query = f"""SELECT 
    roman AS romanization,
    ARRAY_AGG(hanzi ORDER BY hanzi) AS hanzi_array,
    COUNT(hanzi) AS character_count
    FROM {language}
    GROUP BY roman
    ORDER BY roman;
    """
    return self.execute(query)