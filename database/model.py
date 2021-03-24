import pymysql
from peewee import *

import config

if config.USE_MYSQL_DATABASE:
    conn = pymysql.connect(host=config.mysql_host, user=config.mysql_user,
                           password=config.mysql_password)
    try:
        conn.cursor().execute('CREATE DATABASE Face_recognition')
    except Exception:
        pass
    conn.close()
    database = MySQLDatabase('Face_recognition', host=config.mysql_host, user=config.mysql_user,
                             password=config.mysql_password)
else:
    database = SqliteDatabase('resources/database_sqllite.db')


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    name = CharField()
    email = CharField(null=True)
    enrol_date = DateTimeField(null=True)


class Entry(BaseModel):
    name = CharField()  # ForeignKeyField(User, backref='entry', on_delete='CASCADE')
    time = DateTimeField()


class Camera(BaseModel):
    camera_path = CharField()
    date = DateTimeField(null=True)
    status = BooleanField(default=True)