from pymongo import MongoClient

import datetime

class MongoDBDao():

    def __init__(self, config):

        conf_copy = dict(config)
        db = conf_copy.pop("db")
        words_by_length_collection_name = conf_copy.pop("words_by_length_collection")
        
        
        #DEBUG
        #details_collection_name = conf_copy.pop("details_collection")
        #/DEBUG
        

        self.client = MongoClient(**conf_copy)
        self.db = self.client[db]
        self.words_by_length_collection = self.db[words_by_length_collection_name]
        
        
        #DEBUG
        #self.details_collection = self.db[details_collection_name]
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
        #print("GOT",list(res))
        """lengths = []
        for l in list(res):
            #print(l["len"])
            lengths.append(l["len"])"""
        lengths = [l["len"] for l in res]
        return lengths
    
    
    
    
    
    
    
    """
    DEBUG
    """
    def get_all(self):
        d = {}
        for l in self.words_by_length_collection.find({}):
            d[l["len"]]=l["words"]
        return d
        
    def delete_all(self):
        self.words_by_length_collection.delete_many({})
    
    def get_all_locations(self):
        s = set()
        for l in self.details_collection.find({}, {"location":1}):
            s.add(l["location"])
        return s
    
    def quick_tokenize(self):
        db_content = self.details_collection.find({}, {"title":1, "text":1})
        
        s = set()
        for l in self.details_collection.find({}, {"location":1}):
            s.add(l["location"])
        return s