# user creation
import sys
import time
import random
import collections
from random import randrange
from datetime import timedelta
from datetime import datetime

DEBUG = sys.flags.debug

AGE_DISTRIBUTION = { "10-20": 10,
                     "20-30": 35,
                     "30-40": 60,
                     "40-50": 80,
                     "50-80": 100
                    }

ZIP_DISTRIBUTION = { "00000": 20,
                     "20000": 40,
                     "40000": 60,
                     "60000": 80,
                     "80000": 100
                    }

GENDER_DISTRIBUTION = { "Female": 40,
                        "Male": 85,
                        "Unknown": 100
                       }

class User():
    def __init__(self):
        self.birthDate = self.get_birthDate()
        self.gender = self.get_gender()
        self.zip = self.get_zip()
        self.name = "zz_%s_%s_%s" % (self.gender, self.birthDate, self.zip)
        self.email = self.name + "@berated.com"
        if DEBUG: print self.name
        
    def get_birthDate(self):
        age = "30-40"
        if DEBUG: print "get_birthDate"
        r = random.randrange(0,100)
        od = collections.OrderedDict(sorted(AGE_DISTRIBUTION.items()))
        for k,v in od.iteritems():
            if r <= v:
                age = k
                break
        p = age.split("-")
        age = int(p[0]) + random.randrange(0,int(p[1])-int(p[0]))
        if DEBUG: print age
        bd = self.random_date(age)
        return bd
       
    def random_date(self, years=30, from_date=None):
        if from_date is None:
            from_date = datetime.now()
        try:
            from_date = from_date.replace(year=from_date.year - years)
            from_date += timedelta(days = random.randrange(365))
            p = str(from_date).split()
            p2 = str(p[0]).split("-")
            from_date = "%s/%s/%s" % (p2[1], p2[2], p2[0])
        except Exception as e:
            print e
        finally:
            return from_date
        
    def get_gender(self):
        if DEBUG: print "get_gender"
        gender = "Male"
        r = random.randrange(0,100)
        od = collections.OrderedDict(sorted(GENDER_DISTRIBUTION.items()))
        for k,v in od.iteritems():
            if r <= v:
                gender = k
                break
        if DEBUG: print gender
        return gender

    def get_zip(self):
        if DEBUG: print "get_zip"
        r = random.randrange(0,100)
        od = collections.OrderedDict(sorted(ZIP_DISTRIBUTION.items()))
        for k,v in od.iteritems():
            if r <= v:
                zip = random.randrange(int(k), int(k) + 20000 - 1)
                if zip < 10000:
                    zip = "0%d" % zip
                break
        if DEBUG: print zip
        return str(zip)
    
if __name__ == '__main__':
    User()