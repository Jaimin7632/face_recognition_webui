from .model import *


def init_database():
    """
    init when server start(ex. web, backend)
    :return:
    """
    meta.create_all(engine)


def add_camera(camera_path):
    camera = Camera.insert().values(camera_path=camera_path)
    conn = engine.connect()
    result = conn.execute(camera)
    conn.close()
    return True, result.inserted_primary_key[0]


def remove_camera(id):
    query = Camera.delete().where(Camera.c.id == int(id))
    conn = engine.connect()
    result = conn.execute(query)
    conn.close()
    return True, result.rowcount


def get_active_camera_list():
    query = Camera.select()
    conn = engine.connect()
    result = conn.execute(query)
    result = list(result)
    conn.close()
    return True, result


def add_person(**kargs):
    try:
        query = User.insert().values(**kargs)
        conn = engine.connect()
        result = conn.execute(query)
        conn.close()
        return True, result.inserted_primary_key[0]
    except Exception as e:
        return False, str(e)


def get_enrolled_persons():
    try:
        query = User.select()
        conn = engine.connect()
        result = conn.execute(query)
        result = list(result)
        conn.close()
        return True, result
    except Exception as e:
        return False, e


def get_person_details_from_id(id):
    try:
        query = User.select().where(User.c.id == int(id))
        conn = engine.connect()
        result = conn.execute(query)
        result = list(result)
        conn.close()
        return True, result[0]
    except Exception as e:
        return False, "No record found for id"


def remove_user(id):
    try:
        query = User.delete().where(User.c.id == int(id))
        conn = engine.connect()
        result = conn.execute(query)
        conn.close()
        if result.rowcount > 0:
            return True, "successfully removed"
        else:
            return False, "No record found for this id"
    except Exception as e:
        return False, str(e)


def add_entry(**kargs):
    try:
        query = Entry.insert().values(**kargs)
        conn = engine.connect()
        result = conn.execute(query)
        conn.close()
        return True, result.inserted_primary_key[0]
    except Exception as e:
        return False, str(e)


def search_entry(id=None, name=None, starttime=None, endtime=None, limit=100):
    try:
        if id is None:
            conditions = []
            if name is not None:
                conditions.append(Entry.c.name == name)
            if starttime:
                conditions.append(Entry.c.time >= starttime)
            if endtime:
                conditions.append(Entry.c.time <= endtime)

            if limit is not None:
                if conditions:
                    query = Entry.select().where(*conditions).order_by(Entry.c.time.desc()).limit(limit)
                else:
                    query = Entry.select().order_by(Entry.c.time.desc()).limit(limit)

            else:
                if conditions:
                    query = Entry.select().where(*conditions).order_by(Entry.c.time.desc())
                else:
                    query = Entry.select().order_by(Entry.c.time.desc())
        else:
            query = Entry.select().where(Entry.c.id == int(id))

        conn = engine.connect()
        result = conn.execute(query)
        result = list(result)
        conn.close()

        return True, result

    except Exception as e:
        return False, str(e)
