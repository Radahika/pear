from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
event = Table('event', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('title', String(length=64)),
    Column('description', String(length=140)),
    Column('timestamp', DateTime),
    Column('house_id', Integer),
)

message = Table('message', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('message', String(length=500)),
    Column('timestamp', DateTime),
    Column('house_id', Integer),
    Column('user_id', Integer),
)

chore = Table('chore', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('title', String(length=64)),
    Column('description', String(length=140)),
    Column('status', Boolean, default=ColumnDefault(False)),
    Column('timestamp', DateTime),
    Column('user_id', Integer),
    Column('house_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['event'].create()
    post_meta.tables['message'].create()
    post_meta.tables['chore'].columns['house_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['event'].drop()
    post_meta.tables['message'].drop()
    post_meta.tables['chore'].columns['house_id'].drop()
