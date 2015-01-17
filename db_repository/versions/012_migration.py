from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
house = Table('house', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('housename', VARCHAR(length=64)),
)

followers = Table('followers', post_meta,
    Column('follower_id', Integer),
    Column('followed_id', Integer),
)

houses = Table('houses', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('housename', String(length=64)),
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
    pre_meta.tables['house'].drop()
    post_meta.tables['followers'].create()
    post_meta.tables['houses'].create()
    post_meta.tables['user'].columns['email'].create()
    post_meta.tables['user'].columns['password_hash'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['house'].create()
    post_meta.tables['followers'].drop()
    post_meta.tables['houses'].drop()
    post_meta.tables['user'].columns['email'].drop()
    post_meta.tables['user'].columns['password_hash'].drop()
