from mongoframes import *
from mongoframes.factory import *
from mongoframes.factory.blueprints import *
from mongoframes.factory.makers import *
from mongoframes.factory.makers.text import *
from mongoframes.factory.presets import *
from mongoframes.factory.quotas import *
from mongoframes.factory.quantities import *
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

blueprint = Blueprint(Story, {
    'author': Faker('user_name'),
    'title': Sequence('Story number {index}'),
    'body': Lorem('sentence', RandomQuantity(1, 3)),
    'votes': Lambda(lambda: 1)
    })

quota = Quota(blueprint, 10)

documents = factory.assemble(quota)
documents = factory.finish(blueprint, documents)
print(documents)