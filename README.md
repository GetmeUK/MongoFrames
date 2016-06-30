<a href="http://mongoframes.com"><img width="188" src="http://mongoframes.com/images/github-splash.png" alt="MongoFrames logo"></a>

# MongoFrames

[![Build Status](https://travis-ci.org/GetmeUK/MongoFrames.svg?branch=master)](https://travis-ci.org/GetmeUK/MongoFrames)
[![Join the chat at https://gitter.im/GetmeUK/ContentTools](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/GetmeUK/MongoFrames?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

MongoFrames is a fast unobtrusive MongoDB ODM for Python designed to fit into a workflow not dictate one. Documentation is available at [MongoFrames.com](http://mongoframes.com) and includes:

- [A getting started guide](http://mongoframes.com/getting-started)
- [Tutorials/Snippets](http://mongoframes.com/snippets)
- [API documentation](http://mongoframes.com/api)

## Installation

We recommend you use [virtualenv](https://virtualenv.pypa.io) or [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io) to create a virtual environment for your install. There are several options for installing MongoFrames:

- `pip install MongoFrames` *(recommended)*
- `easy_install MongoFrames`
- Download the source and run `python setup.py install`

## Dependencies

- [blinker](https://pythonhosted.org/blinker/) >= 1.4
- [pymongo](https://api.mongodb.com) >= 3
- [pytest](http://pytest.org/) >= 2.8.7 *(only for testing)*

## 10 second example

```Python
from mongoframes import *

# Define some document frames (a.k.a models)
class Dragon(Frame):
    _fields = {'name', 'loot'}

class Item(Frame):
    _fields = {'desc', 'value'}

# Create a dragon and loot to boot
Item(desc='Sock', value=1).insert()
Item(desc='Diamond', value=100).insert()
Dragon(name='Burt', loot=Item.many()).insert()

# Have Burt boast about his loot
burt = Dragon.one(Q.name == 'Burt', projection={'loot': {'$ref': Item}})
for item in burt.loot:
    print('I have a {0.name} worth {0.value} crown'.format(item))
```

## Testing

To test the library you'll need to be running a local instance of MongoDB on the standard port.

To run the test suite: `py.test`
To run the test suite on each supported version of Python: `tox`

## Helpful organizations
MongoFrames is developed using a number of tools & services provided for free by nice folks at organizations committed to supporting open-source projects including [GitHub](https://github.com) and [Travis CI](https://travis-ci.org).
