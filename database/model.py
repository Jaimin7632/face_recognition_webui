from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime, Boolean
from sqlalchemy.dialects.mysql import INTEGER

import config

if config.USE_MSSQL_DATABASE:
    # MsSQL
    engine = create_engine(f'mssql+pymssql://{config.mssql_user}:{config.mssql_password}@{config.mssql_host}/{config.database_name}')
else:
    engine = create_engine(f'sqlite:///resources/{config.database_name}.db')

meta = MetaData()

User = Table(
    'user', meta,
    Column('id', INTEGER, primary_key=True, autoincrement=True),
    Column('name', String),
    Column('email', String,nullable=True),
    Column('enrol_date', DateTime, nullable=True)
)

Entry = Table(
    'entry', meta,
    Column('id', INTEGER, primary_key=True, autoincrement=True),
    Column('name', String),
    Column('time', DateTime)
)

Camera = Table(
    'camera', meta,
    Column('id', INTEGER, primary_key=True, autoincrement=True),
    Column('camera_path', String),
    Column('date', DateTime, default=datetime.now()),
    Column('status', Boolean, default=True),
)
