from model import *


def add_user(**kargs):
    try:
        user = User.create(**kargs)
        user.save()
        return True, user.id
    except Exception as e:
        return False, str(e)


def remove_user(id):
    try:
        ret = User.delete().where(User.id == id).execute()
        if ret > 0:
            return True, "successfully removed"
        else:
            return False, "No record found for this id"
    except Exception as e:
        return False, str(e)


def add_entry(**kargs):
    try:
        entry = Entry.create(**kargs)
        entry.save()
        return True, entry.id
    except Exception as e:
        return False, str(e)


def search_entry(id=None, starttime=None, endtime=None, limit=None):
    try:
        conditions = []
        if id is not None:
            conditions.append(User.id == id)
        if starttime:
            conditions.append(Entry.time >= starttime)
        if endtime:
            conditions.append(Entry.time <= endtime)
        if limit:
            entries = Entry.join(User).select().where(*conditions).limit(limit).objects()
        else:
            entries = Entry.join(User).select().where(*conditions).objects()

        data = [[entry.id, entry.User.id, entry.time] for entry in entries]
        return True, data

    except Exception as e:
        return False, str(e)
