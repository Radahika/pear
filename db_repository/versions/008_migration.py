from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
houses = Table('houses', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('housename', VARCHAR(length=64)),
    Column('user_id', INTEGER),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String(length=64)),
    Column('password_hash', String(length=128)),
    Column('email', String(length=120)),
    Column('house_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['houses'].columns['user_id'].drop()
    post_meta.tables['user'].columns['house_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['houses'].columns['user_id'].create()
    post_meta.tables['user'].columns['house_id'].drop()
