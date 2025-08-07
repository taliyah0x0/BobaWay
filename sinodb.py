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
    return self.execute(f"SELECT l.hanzi_id FROM {language} l JOIN characters c ON l.hanzi_id = c.id WHERE c.hanzi = %s AND l.roman = %s", (hanzi, roman))
  
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

  # Words management methods
  def get_character_with_romanizations(self, character_id, language):
    """Get character details with romanizations for a specific language"""
    character_result = self.execute("SELECT id, hanzi FROM characters WHERE id = %s", (character_id,))
    if not character_result:
      return None
    
    character_id, hanzi = character_result[0]
    romanizations = self.execute(f"SELECT roman FROM {language} WHERE hanzi_id = %s ORDER BY roman", (character_id,))
    
    return {
      'id': character_id,
      'character': hanzi,
      'romanizations': [r[0] for r in romanizations] if romanizations else []
    }

  def create_word(self, romanization, language, character_ids):
    """Create a new word entry"""
    return self.execute(
      "INSERT INTO words (romanization, language, characters) VALUES (%s, %s, %s) RETURNING id", 
      (romanization, language, character_ids)
    )

  def get_words(self, language=None, limit=None, offset=None):
    """Get words with character details"""
    base_query = """
      SELECT w.id, w.romanization, w.language, w.characters
      FROM words w
    """
    
    conditions = []
    params = []
    
    if language:
      conditions.append("w.language = %s")
      params.append(language)
    
    if conditions:
      base_query += " WHERE " + " AND ".join(conditions)
    
    base_query += " ORDER BY w.id DESC"
    
    if limit:
      base_query += " LIMIT %s"
      params.append(limit)
    
    if offset:
      base_query += " OFFSET %s" 
      params.append(offset)
    
    words_result = self.execute(base_query, params)
    
    words = []
    for word_row in words_result:
      word_id, romanization, word_language, character_ids = word_row
      
      # Get character details
      character_details = []
      if character_ids:
        placeholders = ','.join(['%s'] * len(character_ids))
        char_query = f"SELECT id, hanzi FROM characters WHERE id IN ({placeholders}) ORDER BY array_position(%s, id)"
        char_result = self.execute(char_query, character_ids + [character_ids])
        character_details = [{'id': r[0], 'character': r[1]} for r in char_result]
      
      words.append({
        'id': word_id,
        'romanization': romanization,
        'language': word_language,
        'characters': character_ids,
        'character_details': character_details
      })
    
    return words

  def update_word(self, word_id, romanization, language, character_ids):
    """Update an existing word"""
    return self.execute(
      "UPDATE words SET romanization = %s, language = %s, characters = %s WHERE id = %s",
      (romanization, language, character_ids, word_id)
    )

  def delete_word(self, word_id):
    """Delete a word"""
    return self.execute("DELETE FROM words WHERE id = %s", (word_id,))

  def check_duplicate_word(self, romanization, language, character_ids):
    """Check for duplicate words"""
    result = self.execute(
      "SELECT COUNT(*) FROM words WHERE romanization = %s AND language = %s AND characters = %s",
      (romanization, language, character_ids)
    )
    return result[0][0] > 0 if result else False

  def get_all_languages(self):
    """Get all available languages"""
    return ['shanghainese', 'korean', 'taiwanese', 'vietnamese']