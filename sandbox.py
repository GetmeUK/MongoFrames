from mongoframes import *
from mongoframes.factory import Factory
from mongoframes.factory.blueprints import Blueprint
from mongoframes.factory.makers import  Sequence
from mongoframes.factory.presets import Preset
from mongoframes.factory.quotas import Quota
from pymongo import MongoClient


# Set up a connection

Frame._client = MongoClient('mongodb://localhost:27017/mongoframes_factory')


# Defines some Frames to create fake data for

class User(Frame):

    _fields = {
        'username'
        }


class Story(Frame):

    _fields = {
        'author',
        'title',
        'url',
        'body',
        'votes'
        }


class Comments(Frame):

    _fields = {
        'author',
        'story',
        'body',
        'votes'
        }


# Remove any existing data for the collection

Comments.get_collection().drop()
Story.get_collection().drop()
User.get_collection().drop()


# Create a factory

factory = Factory()

blueprint = Blueprint(User, {
    'username': Sequence('user-')
    })

quota = Quota(blueprint, 10)

documents = factory.assemble(quota)

print(documents)