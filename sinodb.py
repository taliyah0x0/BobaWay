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

  def get_character_id(self, hanzi):
    """Get the character ID for a given hanzi, creating it if it doesn't exist"""
    # First try to get existing character
    result = self.execute("SELECT id FROM characters WHERE hanzi = %s", (hanzi,))
    if result:
      return result[0][0]
    else:
      # Create new character and return its ID
      self.execute("INSERT INTO characters (hanzi) VALUES (%s)", (hanzi,))
      return self.execute("SELECT id FROM characters WHERE hanzi = %s", (hanzi,))[0][0]

  def get_hanzi_by_id(self, hanzi_id):
    """Get the hanzi character for a given ID"""
    result = self.execute("SELECT hanzi FROM characters WHERE id = %s", (hanzi_id,))
    return result[0][0] if result else None

  def get_entry_by_hanzi_and_roman(self, language, hanzi, roman):
    """Get entry by hanzi and romanization"""
    return self.execute(f"SELECT c.hanzi_id FROM {language} l JOIN characters c ON l.hanzi_id = c.id WHERE c.hanzi = %s AND l.roman = %s", (hanzi, roman))
  
  def create_translation_entry(self, language, hanzi, roman):
    """Create a new translation entry using character ID"""
    hanzi_id = self.get_character_id(hanzi)
    return self.execute(f"INSERT INTO {language} (hanzi_id, roman) VALUES (%s, %s)", (hanzi_id, roman))
  
  def update_translation_entry(self, language, hanzi_id, original_roman, new_roman):
    """Update a translation entry using character ID"""
    return self.execute(f"UPDATE {language} SET roman = %s WHERE hanzi_id = %s AND roman = %s", (new_roman, hanzi_id, original_roman))
  
  def delete_translation_entry(self, language, hanzi_id, roman):
    """Delete a translation entry using character ID"""
    return self.execute(f"DELETE FROM {language} WHERE hanzi_id = %s AND roman = %s", (hanzi_id, roman))
  
  def fetch_all_entries(self, language):
    """Fetch all entries with hanzi and romanization using JOIN"""
    result = self.execute(f"SELECT l.hanzi_id, c.hanzi, l.roman FROM {language} l JOIN characters c ON l.hanzi_id = c.id ORDER BY c.hanzi, l.roman")
    return [{'code': row[0], 'hanzi': row[1], 'roman': row[2]} for row in result]

  def get_romanization_mapping(self, language):
    """Get romanization mapping with hanzi arrays using JOIN"""
    query = f"""SELECT 
    l.roman AS romanization,
    ARRAY_AGG(c.hanzi ORDER BY c.hanzi) AS hanzi_array,
    COUNT(c.hanzi) AS character_count
    FROM {language} l
    JOIN characters c ON l.hanzi_id = c.id
    GROUP BY l.roman
    ORDER BY l.roman;
    """
    return self.execute(query)