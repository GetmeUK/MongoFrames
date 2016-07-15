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
        'body',
        'comments'
        }


class Comment(SubFrame):

    _fields = {
        'author',
        'body'
        }


# Remove any existing data for the collection

Story.get_collection().drop()
User.get_collection().drop()


# Create a factory
factory = Factory(presets=[
    Preset('body', Lorem('sentence', Random(1, 3)))
    ])

# Make 100 users
user_bp = Blueprint(User, {
    'username': Unique(Faker('user_name'))
    })
user_docs = factory.assemble(user_bp, 100)
factory.populate(user_bp, user_docs)

# Make 1,000 stories with up to 20 commends against each
comment_bp = Blueprint(Comment, {
    'author': Reference(User, 'username', [u['username'] for u in user_docs])
    })
story_bp = Blueprint(Story, {
    'author': Reference(User, 'username', [u['username'] for u in user_docs]),
    'title': Sequence('Story number {index}'),
    'comments': ListOf(
        SubFactory(comment_bp, presets=factory.presets),
        Gauss(3, 10)
        )
    })
story_docs = factory.assemble(story_bp, 1000)
factory.populate(story_bp, story_docs)


# Select data in the database and print it out

stories = Story.many(projection={
    'author': {'$ref': User},
    'comments': {
        '$sub': Comment,
        'author': {'$ref': User}
        }
    }
)

most_comments = 0
total_comments = 0

for story in stories:
    print('#', story.title)
    print(story.body)
    print('by', story.author.username)
    print('comments', len(story.comments))
    for comment in story.comments:
        print(comment.body, 'by', comment.author.username)

    if len(story.comments) > most_comments:
        most_comments = len(story.comments)
    total_comments += len(story.comments)

    print('---')

print('Most comments on a story', most_comments)
print('Average comments per story', float(total_comments) / len(stories))

# @@
# - image maker (e.g folder of product, accommodation, people images)
