import random

from pymongo import MongoClient

from mongoframes import *
from mongoframes.factory import *
from mongoframes.factory.blueprints import *
from mongoframes.factory.makers import *
from mongoframes.factory.makers.text import *
from mongoframes.factory.presets import *
from mongoframes.factory.quotas import *


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
        'votes',
        'score'
        }


class Comments(Frame):

    _fields = {
        'author',
        'story',
        'body',
        'votes'
        }


class Vote(SubFrame):

    _fields = {
        'user',
        'up'
        }


# Remove any existing data for the collection

Comments.get_collection().drop()
Story.get_collection().drop()
User.get_collection().drop()


# Create a factory

factory = Factory()

voter_blueprint = Blueprint(Vote, {
    'user': Unique(Faker('user_name')),
    'up': Faker('boolean', chance_of_getting_true=25)
    })

story_blueprint = Blueprint(Story, {
    'author': Unique(Faker('user_name')),
    'title': Sequence('Story number {index}'),
    'body': Lorem('sentence', RandomQuota(1, 3)),
    'votes': SubFactory(voter_blueprint),
    'score': Lambda(lambda: random.randint(0, 10))
    })

documents = factory.assemble(story_blueprint, 10)
documents = factory.finish(story_blueprint, documents)
print(documents)

# Consider support for:
# - Look to drop quota's as a class, id doesn't do anything, move quantities in
#   that module.
# - image maker (e.g folder of product, accommodation, people images)