# mongoframes

[![Join the chat at https://gitter.im/GetmeUK/MongoFrames](https://badges.gitter.im/GetmeUK/MongoFrames.svg)](https://gitter.im/GetmeUK/MongoFrames?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

**mongoframes** is a lightweight Python ODM (object document manager) for
MongoDB based on top of
[PyMongo](https://api.mongodb.org/python/current/), it was originally
created as a replacement for MongoEngine at Getme. We found we frequently wrote
code to circumvent the MongoEngine internals (accessing pymongo directly) to
achieve acceptable performance.