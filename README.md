# mongoframes

**mongoframes** is a lightweight Python ODM (object document manager) for
MongoDB based on top of
[PyMongo](https://api.mongodb.org/python/current/), it was originally
created as a replacement for MongoEngine at Getme. We found we frequently wrote
code to circumvent the MongoEngine internals (accessing pymongo directly) to
achieve acceptable performance.