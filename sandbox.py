from mongoframes import *
from mongoframes.factory import *
from mongoframes.factory.makers import DateBetween, Sequence
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

# assemble
# populate


# Produce fake documents using the factory


# Factorys
# Blueprints
    # Associations
# Quotas
# Makers

