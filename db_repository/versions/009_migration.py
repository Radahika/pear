from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
followers = Table('followers', pre_meta,
    Column('follower_id', INTEGER),
    Column('followed_id', INTEGER),
)

houses = Table('houses', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('housename', VARCHAR(length=64)),
)

house = Table('house', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
)

post = Table('post', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('title', String(length=20)),
)

user = Table('user', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('username', VARCHAR(length=64)),
    Column('password_hash', VARCHAR(length=128)),
    Column('email', VARCHAR(length=120)),
    Column('house_id', INTEGER),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('nickname', String(length=64)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['followers'].drop()
    pre_meta.tables['houses'].drop()
    post_meta.tables['house'].create()
    post_meta.tables['post'].create()
    pre_meta.tables['user'].columns['email'].drop()
    pre_meta.tables['user'].columns['house_id'].drop()
    pre_meta.tables['user'].columns['password_hash'].drop()
    pre_meta.tables['user'].columns['username'].drop()
    post_meta.tables['user'].columns['nickname'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['followers'].create()
    pre_meta.tables['houses'].create()
    post_meta.tables['house'].drop()
    post_meta.tables['post'].drop()
    pre_meta.tables['user'].columns['email'].create()
    pre_meta.tables['user'].columns['house_id'].create()
    pre_meta.tables['user'].columns['password_hash'].create()
    pre_meta.tables['user'].columns['username'].create()
    post_meta.tables['user'].columns['nickname'].drop()
