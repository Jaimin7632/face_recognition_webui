from .model import *


def init_database():
    """
    init when server start(ex. frontend_templates, backend)
    :return:
    """
    if not database.table_exists(User):
        database.create_tables([User])
    if not database.table_exists(Entry):
        database.create_tables([Entry])
    if not database.table_exists(Camera):
        database.create_tables([Camera])
        add_camera('0')



def add_camera(camera_path):
    camera = Camera.create(camera_path=camera_path)
    return True, camera.id

def get_active_camera_list():
    cameras = Camera.select().objects()
    return True, [camera.camera_path for camera in cameras]

def add_user(**kargs):
    try:
        user = User.create(**kargs)
        user.save()
        return True, user.id
    except Exception as e:
        return False, str(e)


def get_person_details_from_id(id):
    try:
        person = User.get(User.id == id)
        return True, [person.name, person.email, person.enrol_date]
    except Exception as e:
        return False, "No record found for id"


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
