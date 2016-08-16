# ratings, to be tested, extended, etc ...
import sys
import random
import collections
import argparse
from users import User
from bemodels import Thing
from google.appengine.ext import ndb

DEBUG = sys.flags.debug

PERSONALITY_TYPES = { "Negative": 45,
                      "Positive": 55
                    }

# number of stars - probability
NEGATIVE_DISTRIBUTIONS = { "1": 15,
                          "2": 35,
                          "3": 75,
                          "4": 90,
                          "5": 100
                         }

# number of stars - probability
POSITIVE_DISTRIBUTIONS = { "1": 10,
                           "2": 25,
                           "3": 65,
                           "4": 85,
                           "5": 100
                         }

# group likelihoods
RATING_GROUPS = { "TYPE_A": { "Business": 15, "Other": 25, "Person": 65, "Place": 70, "Product": 100 },
                  "TYPE_B": { "Business": 15, "Other": 25, "Person": 55, "Place": 60, "Product": 100 },
                  "TYPE_C": { "Business": 10, "Other": 40, "Person": 80, "Place": 85, "Product": 100 },
                  "TYPE_D": { "Business": 30, "Other": 35, "Person": 50, "Place": 60, "Product": 100 }
                }

# equal choice of others
#OTHERS = [ "Concepts", "Foods","Genres", "Musics"]

#GENRES = ["Romance", "Erotica", "Mystery", "Comedy", "Science Fiction", "Horror", "Drama"]

#MUSICS = ["Pop", "Rock", "Country", "Hip Hop", "Rap", "Jazz", "Blues", "World", "Classical"]

#FOODS = ["Fruit", "Vegetables", "Chicken", "BBQ", "Seafood", "Steak", "Sushi", "Pizza", "Beer", "Wine", "Milk", "Water",
#         "Peanut Butter", "Oranges", "Apples", "Nectarines", "Tangerines", "Plums", "Grapes", "Pretzels", "Spaghetti",
#         "Macaroni and CHeese", "Cheddar CHeese", "American Cheese", "Swiss Cheese", "Coffee", "Tea", "Beer", "Wine"]

class AutoRatings():
    def __init__(self):
        self.dummy_var = 47
        #self.persons = open("persons.txt", "r").readlines() # ["Jennifer Aniston"]
        #self.products = open("things.txt", "r").readlines() # ["Mr. Clean"]
        #self.businesses = open("businesses.txt", "r").readlines() # ["Exxon"]
        #self.places = open("places.txt", "r").readlines() # ["Lisbon"]
        #self.concepts = open("concepts.txt", "r").readlines()
        
    def make_ratings(self, num=1, spread="1", auto_user=False):
        ratings = []        
        spread = spread.split(",")
        min_spread = int(spread[0])
        if len(spread) == 1:
            max_spread = min_spread + 1
        else:
            max_spread = int(spread[1])
            
        for i in range(num):
            self.user = User()
            if auto_user:
                self.user.name = "zz_Female_08_30_1969_37568"   # same old user
            self.userEmail = "zz_Female_08_30_1969_37568@berated.com" 
            num_ratings = random.randrange(min_spread, max_spread)
            for j in range(num_ratings):
                self.personality_type = self.get_personality_type()
                self.rating_group = self.get_rating_group()
                self.ratedType, self.ratedName = self.get_selection()
                self.rating = self.get_rating()
                print "%-27s\t%-8s\t%-27s\t\t%s" % (self.user.name, self.ratedType, self.ratedName, self.rating)
                new_rating = {}
                new_rating["userName"] = self.user.name
                new_rating["userEmail"] = self.userEmail
                new_rating["gender"] = "Female"
                new_rating["birthDate"] = "08/30/1969"
                new_rating["zipCode"] = "37568"
                new_rating["ratedType"] = self.ratedType
                new_rating["ratedName"] = self.ratedName
                new_rating["rating"] = self.rating
                ratings.append(new_rating)
                
        return ratings
        
    def get_personality_type(self):
        if DEBUG: print "get_personality_type"
        personality_type = "Positive"
        r = random.randrange(0,100)
        od = collections.OrderedDict(sorted(PERSONALITY_TYPES.items()))
        for k,v in od.iteritems():
            if r <= v:
                personality_type = k
                break
        if DEBUG: print personality_type
        return personality_type
        
    def get_rating_group(self):
        if DEBUG: print "get_rating_group"
        groups = sorted(RATING_GROUPS.keys())
        group = random.choice(groups)
        if DEBUG: print group
        return group
        
    def get_selection(self):
        if DEBUG: print "get_selection"
        ratedType = "Product"
        ratedName = "Exxon"
        choices = RATING_GROUPS[self.rating_group]
        r = random.randrange(0,100)
        od = collections.OrderedDict(sorted(choices.items()))
        for k,v in od.iteritems():
            if r <= v:
                ratedType = k
                break
        if DEBUG: print ratedType
        if ratedType == "Product":
            ratedName = self.get_from_datastore("Product")
            #ratedName = random.choice(self.products).strip()
        elif ratedType == "Person":
            ratedName = self.get_from_datastore("Person")
            #ratedName = random.choice(self.persons).strip()
        elif ratedType == "Business":
            ratedName = self.get_from_datastore("Business")
            #ratedName = random.choice(self.businesses).strip()
        elif ratedType == "Place":
            ratedName = self.get_from_datastore("Places")  # Places, not Place
            #ratedName = random.choice(self.places).strip()
        elif ratedType == "Other":
            ratedName = self.get_from_datastore("Other")
            #choice = random.choice(OTHERS)
            #if choice == "Concepts":
            #    ratedName = random.choice(self.concepts).strip()
            #elif choice == "Foods":
            #    ratedName = random.choice(FOODS)
            #elif choice == "Genres":
            #    ratedName = random.choice(GENRES)
            #elif choice == "Musics":
            #    ratedName = random.choice(MUSICS)
        if DEBUG: print ratedType, ratedName
        return ratedType, ratedName
    
    def get_from_datastore(self, ratedType):
        # test getting a random thing back
        q = Thing.query(Thing.category == ratedType)
        item_keys = q.fetch(1000000,keys_only=True)
        random_keys = random.sample(item_keys, 1)
        items = ndb.get_multi(random_keys)
        #for item in items:
        #    print item.name
        return items[0].name
        
    def get_rating(self):
        rating = "3"
        if DEBUG: print "get_rating"
        r = random.randrange(0,100)
        if self.personality_type == "Positive":
            od = collections.OrderedDict(sorted(POSITIVE_DISTRIBUTIONS.items()))
        else:
            od = collections.OrderedDict(sorted(NEGATIVE_DISTRIBUTIONS.items()))
        for k,v in od.iteritems():
            #print r, k,v
            if r <= v:  # in this case, the key is the value
                rating = k
                break
        
        if DEBUG: print rating
        return rating

if __name__ == '__main__':
    """
       python ratings.py
    """
    r = AutoRatings()
    r.make_ratings()