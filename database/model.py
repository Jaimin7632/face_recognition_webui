from peewee import *

database = SqliteDatabase('resources/database_sqllite.db')


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    name = CharField()
    email = CharField(null=True)
    enrol_date = DateTimeField(null=True)


class Entry(BaseModel):
    user = ForeignKeyField(User, backref='entry', on_delete='CASCADE')
    time = DateTimeField()

class Camera(BaseModel):
    camera_path = CharField()
    date= DateTimeField(null=True)
    status = BooleanField(default=True)