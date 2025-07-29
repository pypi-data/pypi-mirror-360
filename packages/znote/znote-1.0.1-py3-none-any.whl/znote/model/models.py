from pony.orm import Required, Optional, PrimaryKey, LongStr
from datetime import datetime
import __main__


def Table(db, type_db="sqlite"):
    class User(db.Entity):
        id = PrimaryKey(int, auto=True)
        username = Required(str, unique=True)
        password_hash = Required(str)
        created_at = Required(datetime)
        workspace = Required(str, default="default")
        active_workspace = Required(str, default="default")

    class Note(db.Entity):
        id = PrimaryKey(int, auto=True)
        title = Required(str)
        content = Required(str)
        created_at = Required(datetime)
        updated_at = Required(datetime)
        creator_id = Required(int)
        editor_id = Required(int)
        protected = Optional(str)
        shared_with = Optional(str)  # Liste d’IDs ou noms d’utilisateurs
        workspace = Required(str)