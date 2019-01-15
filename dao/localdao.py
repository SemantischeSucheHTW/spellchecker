from pymongo import MongoClient

import datetime

class LocalDAO():

    def __init__(self, config):

        conf_copy = dict(config)
        db = conf_copy.pop("db")
        words_by_length_collection_name = conf_copy.pop("words_by_length_collection")
        
        
        #DEBUG
        details_collection_name = conf_copy.pop("details_collection")
        #/DEBUG
        

        self.client = MongoClient(**conf_copy)
        self.db = self.client[db]
        self.words_by_length_collection = self.db[words_by_length_collection_name]
        
        
        #DEBUG
        self.details_collection = self.db[details_collection_name]
        #/DEBUG
        
    def getListsForLengths(self, lengths_list):
        lists=[]
        for length in lengths_list:
            wordlist = self.words_by_length_collection.find_one({"len":length})
            if (wordlist):
                lists.append(wordlist["words"])
        return lists
    
    def getListForLength(self, length):
        wordlist = self.words_by_length_collection.find_one({"len":length})
        if (wordlist):
            return wordlist["words"]
        return None
    
    def getPossibleWordLengths(self):
        res = self.words_by_length_collection.find({}, {"len":1})
        lengths = [l["len"] for l in res]
        return lengths