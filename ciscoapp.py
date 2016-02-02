from bottle import route, run, request
from pymongo import MongoClient
from pymongo.errors import InvalidId
from bson.objectid import ObjectId
import json
from bottle import error

client = MongoClient('localhost', 27017)
db = client.cisco
collection = db.objstore

@error(405)
def error404(error): 
    return 'THE URL IS INCORRECT !'
         
@error(404)
def error404(error):
    return 'FILE NOT FOUND !'

@route('/')  
def hello():
    return "WELCOME !"

@route('/api/objects', method='POST') 
def objects_create():
    try:
        result = request.json
        id = collection.insert(result) 
        result["uid"] = str(result.pop("_id"))
    except ValueError:
        result = {
            "verb": "POST",  
            "url": "%s" % (request.url),
            "message": "Not a JSON object"
        }
    except TypeError:
        result = {
            "verb": "POST",
            "url": "%s" % (request.url),
            "message": "Please specify proper JSON object"
        }
    except:
        result = {
            "verb": "POST",
            "url": "%s" % (request.url),
            "message": "Unknown exception occurred"
        }
    return json.dumps(result)

@route('/api/objects', method='GET')
def objects_show():
    try:
        result = []
        for element in collection.find():
            uid = str(element.pop("_id"))
            result.append({
                "url": "%s/%s" % (request.url, uid)
            })
    except e:
        result = {
            "verb": "GET",
            "url": "%s" % (request.url),
            "message": "Unknown exception occurred"
        }
    return json.dumps(result)


@route('/api/objects/<uid>', method='GET')
def objects_show(uid):
    try:
        result = collection.find_one({"_id": ObjectId(uid)})
        if result:
            result["uid"] = str(result.pop("_id"))
        else:
            result = {
                "verb": "GET",
                "url": "%s/%s" % (request.url, uid),
                "message": "Collection is empty"
            }
            
    except InvalidId:
        result = {
            "verb": "GET",
            "url": "%s/%s" % (request.url, uid),
            "message": "Input ID is invalid"
        }
    except:
        result = {
            "verb": "GET",
            "url": "%s/%s" % (request.url, uid),
            "message": "Unknown exception occurred"
        }
    return json.dumps(result)

@route('/api/objects/<uid>', method='DELETE')
def objects_delete(uid):
    try:
        wr = collection.remove( {"_id": ObjectId(uid)});
        nRemoved = wr[u'n']
        if nRemoved == 0:
            return {
                "verb": "DELETE",
                "url": "%s/%s" % (request.url, uid),
                "message": "UID does not exist !"
            }
    except InvalidId:
            return {
                "verb": "GET",
                "url": "%s/%s" % (request.url, uid),
                "message": "Input ID is invalid"
            }
    except:
        return {
            "verb": "DELETE",
            "url": "%s/%s" % (request.url, uid),
            "message": "Unknown exception occurred"
        }
    return ""


@route('/api/objects/<uid>', method='PUT')
def objects_save(uid):
    try:
        result = collection.find_one({"_id": ObjectId(uid)})
        if result:
            result = request.json
            collection.update({"_id": ObjectId(uid)}, result)
            result["uid"] = str(uid)
        else:
            result = {
                "verb": "GET",
                "url": "%s/%s" % (request.url, uid),
                "message": "Collection is empty"
            }
    except InvalidId:
        result = {
            "verb": "PUT",
            "url": "%s/%s" % (request.url, uid),
            "message": "Input ID is invalid"
        }
    except ValueError:
        result = {
            "verb": "PUT",
            "url": "%s/%s" % (request.url, uid),
            "message": "Not a JSON object"
        }
    except:
        result = {
            "verb": "PUT",
            "url": "%s/%s" % (request.url, uid),
            "message": "Unknown exception occurred"
       }
    return json.dumps(result)

run(host='0.0.0.0', port=80, debug=True)