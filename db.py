import os
import psycopg2

DB_URL = os.environ['DATABASE_URL']

class DB:
  def __init__(self):
    self.conn = None
    self.cur = None

  def __del__(self):
    self.close()
    
  def connect(self):
      try:
          conn = psycopg2.connect(DB_URL)
          self.conn = conn
          self.cur = conn.cursor()
      except psycopg2.Error as e:
          print(f"Error connecting to the database: {e}")
      
  def close(self):
    if self.cur:
      self.cur.close()
      self.cur = None
    if self.conn:
      self.conn.close()
      self.conn = None
      
  def execute(self, query, params=None):
    if not self.conn:
      self.connect()
      
    try:
      if params:
        self.cur.execute(query, params)
      else:
        self.cur.execute(query)
        
      # save if successful
      self.conn.commit()
      if query.startswith("SELECT"):
        return self.cur.fetchall()
      return None
    except psycopg2.Error as e:
      # rollback if error
      self.conn.rollback()
      print(f"Error executing query: {e}")
      raise
      
      
      