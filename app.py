from flask import Flask
from flask import request
from flask_cors import CORS

from suggester.suggester import Suggester
from dao.mongodbdao import MongoDBDao

import json

import os
def env(key):
    value = os.environ.get(key)
    if not value:
        raise Exception(f"environment variable '{key}' not set!")
    return value

app = Flask(__name__)
CORS(app)

dao = MongoDBDao({
    "host": env("MONGODB_HOST"),
    "db": env("MONGODB_DB"),
    "words_by_length_collection": env("MONGODB_WORDS_BY_LENGTH_COLLECTION"),
    "username": env("MONGODB_USERNAME"),
    "password": env("MONGODB_PASSWORD"),
    "authSource": env("MONGODB_DB")
})

"""dao = MongoDBDao({
    "host": "127.0.0.1",
    "db": "default",
    "words_by_length_collection": "words_by_length",
    "username": "spellchecker_suggester",
    "password": "spellchecker_suggester",
    "authSource": "default"
})"""

suggester = Suggester(dao, min_sim=0.5, n_suggestions=2, n_near_rows=2)

@app.route('/corrections', methods=['GET'])
def corrections():
    args = request.args.to_dict()
    words = args.pop('query', None)
    if (words):
        words=words.lower().split(" ")
        print("got words:", words)
        suggestions = suggester.lookup_list(words)
        print("sending suggestions:", suggestions)
    
        #json_response = "[" + json.dumps(suggestions, ensure_ascii=False)[1:-1] + "]"
        #return json_response
        return json.dumps(suggestions, ensure_ascii=False)
    else:
        return "[]"

if __name__ == '__main__':
    #app.run(host='127.0.0.1', port=8080)
    app.run(host='0.0.0.0', port=env("SERVER_PORT"))
