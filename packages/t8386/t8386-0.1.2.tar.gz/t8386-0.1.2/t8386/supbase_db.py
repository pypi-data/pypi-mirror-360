import os
from supabase import create_client, Client

from dotenv import load_dotenv
load_dotenv()

class SupabseDB:
  _supabase: Client = None

  def __init__(self, url: str = None, key: str = None):
    if not url:
      url = os.getenv("SUPABASE_URL")
    if not key:
      key = os.getenv("SUPABASE_KEY")
    self._supabase = create_client(url, key)
  
  def get_data(self, table: str):
    return self._supabase.table(table).select("*").execute()
  
  def insert_data(self, table: str, data: dict):
    return self._supabase.table(table).insert(data).execute()
  
  def update_data(self, table: str, data: dict, key_eq: str):
    id = data[key_eq]
    return self._supabase.table(table).update(data).eq(key_eq, id).execute()
  
  def delete_data(self, table: str, key_eq: str, key_eq_value: str):
    return self._supabase.table(table).delete().eq(key_eq, key_eq_value).execute()