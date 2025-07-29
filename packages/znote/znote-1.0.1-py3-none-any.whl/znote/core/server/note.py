import __main__
import impmagic

@impmagic.loader(
    {'module': 'pony.orm', 'submodule': ['db_session', 'select']}
)
def get_note(user_id, workspace=None):
    notes_list = []

    with db_session:
        query = __main__.settings.orm.Note.select().where("n.creator_id == user_id", {"user_id": user_id})

        if workspace:
            query = query.where("n.workspace == workspace", {"workspace": workspace})

        result = query[:]

        return result

    return notes_list