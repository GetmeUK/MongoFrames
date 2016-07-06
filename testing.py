from mongoframes import *
from pymongo import MongoClient

Frame._client = MongoClient('mongodb://localhost:27017/mongoframes_test')


class Dragon(Frame):

    _fields = {
        'name',
        'item'
        }


class Item(SubFrame):

    _fields = {
        'desc',
        'previous_owner',
        'subby'
        }

class SubItem(SubFrame):

    _fields = {
        'foo'
        }

dragons = Dragon.many(projection={
    'item': {
        '$sub': Item,
        'previous_owner': {'$ref': Dragon},
        'subby': {'$sub': SubItem}
        }
    })

for dragon in dragons:
    print(dragon.name)
    if dragon.item:
        print(dragon.item.previous_owner.name)
        print(dragon.item.subby.foo)