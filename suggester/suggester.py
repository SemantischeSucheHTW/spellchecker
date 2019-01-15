import numpy as np
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance, damerau_levenshtein_distance

class Suggester:
 
    def __init__(self, dao, min_sim, n_suggestions, n_near_rows=2, min_word_length=4):
        self.dao = dao
        
        #what is the minimal similarity for a suggestions
        self.min_sim = min_sim
        
        #how many suggestions are allowed?
        self.n_suggestions = n_suggestions
        
        #how many letters are allowed to be added / subtracted (example: n=2 hello -> hell or helloo)
        self.n_near_rows = n_near_rows
        
        #what is the minimum word length for a correction?
        self.min_word_length = min_word_length
        
        #if sim_func is "normalized_damerau_levenshtein":
        #    self.sim_func = dist_to_sim(normalized_damerau_levenshtein_distance)
        #if sim_func is "jaro_winkler":
        #if sim_func.__name__ is "normalized_damerau_levenshtein_distance":
        #    self.sim_func = dist_to_sim(sim_func)
        #else
        #    raise Exception('similarity function not available')
    
    
    #looks up, which near rows can even exist and returns a list of the valid ones
    #n - how near
    #n_letters - length of the "central" row
    #possible_indices - which word lengths do even exist?
    def get_near_rows(n, n_letters, possible_indices):
        res = []
        offset_near_rows = list(range(n_letters-n, n_letters+n+1))
        offset_near_rows = np.intersect1d(offset_near_rows, possible_indices)

        return offset_near_rows
    
    #returns a list of [similarity, word]
    #returns an empty list, if there are no words similar enough
    def lookup(self, input_string, sim_func):
        n_letters = len(input_string)

        #contains the row indices, that are relevant for the lookup
        i_lookup_rows = Suggester.get_near_rows(self.n_near_rows, n_letters, self.dao.getPossibleWordLengths())

        #get the relevant rows for the lookup #+ their distance regarding the length of the words
        lookup_rows = []
        for i in i_lookup_rows:
            row_index_dist = abs(n_letters-i)
            #lookup_rows.append((row_index_dist, lookup_list[i]))
            list_for_length = self.dao.getListForLength(int(i))
            if (list_for_length):
                lookup_rows.append(list_for_length)

        #determine the distance between the given word and every word from the relevant rows
        sims_with_words = []
        for lookup_row in lookup_rows:
            for w in lookup_row:
                sim = sim_func(w, input_string)
                if sim >= self.min_sim:
                    sims_with_words.append((sim, w))

        dtype = [('sim', float), ('word', object)]

        sims = np.array(sims_with_words, dtype)
        sorted_sims_with_words = np.sort(sims, order='sim')
        
        """if len(sorted_sims_with_words)<=self.n_suggestions:
            return list(sorted_sims_with_words)
        return list(sorted_sims_with_words[-self.n_suggestions:])"""
        
        #for some reason, dtype does not work on lists
        ## and also we need to convert the tuples into lists, so json can serialize them
        result = []
        for element in sorted_sims_with_words:
            result.append([element[0], element[1]])

        if len(result)<=self.n_suggestions:
            return result
        return result[-self.n_suggestions:]
    
    
    
    def dist_to_sim(dist_func):
        return lambda x, y: 1-dist_func(x, y)
    
    def normalized_damerau_levenshtein_lookup(self, input_string):
        return self.lookup(input_string=input_string, \
                           sim_func=Suggester.dist_to_sim(normalized_damerau_levenshtein_distance))
    
    
    def damerau_levenshtein_lookup(self, input_string):
        return self.lookup(input_string=input_string, \
                           sim_func=damerau_levenshtein_distance)
    
    
    def highest_value_unique(similarities):
        return len(np.argwhere(np.array(similarities)==similarities[np.argmax(similarities)]).reshape(-1))==1
    
    #looks for similar words for the given wordlist
    #corrections are only suggested, if the respective word needs a corrections (i.e. is written differently than in one of the documents)
    #returns list of dicts {"word":"w1", "suggestions":["s1", "s2"]}
    def lookup_list(self, wordlist):
        #dict with: word->List((similarity, correction))
        results = []
        for word in wordlist:
            
            #the word needs to have a minimum length
            if len(word) >= self.min_word_length:
                
                #lookup_res is a List((similarity, correction))
                lookup_res = self.normalized_damerau_levenshtein_lookup(input_string=word)
            
                #only extend the dictionary when there is a result and the word needs to be corrected (i.e. the similarity is not 1)
                if lookup_res and not (lookup_res[-1][0] == 1):
                    
                    suggested_words = []
                    
                    #check whether the highest value is higher than all others -> if yes: only keep that one
                    similarities = [el[0] for el in lookup_res]
                    if Suggester.highest_value_unique(similarities):
                        suggested_words.append(lookup_res[np.argmax(similarities)][1])
                    else:
                        #only keep the words
                        for sim_word in lookup_res:
                            suggested_words.append(sim_word[1])
                    
                    
                    #write suggested words only in result
                    results.append({"word":word, "suggestions":suggested_words})
        return results