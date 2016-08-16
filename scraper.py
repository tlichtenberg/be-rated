# the idea here is to get stuff out of web pages 
# and put them into text files for be-rated.appspot.com 

# for https://www.randomlists.com/things
# names = soup.findAll("span", { "class" : "name" })
# refresh in a loop and get again
# mydivs.text

from bs4 import BeautifulSoup
import requests
import time
import sys
from optparse import OptionParser

DEBUG = sys.flags.debug

class Scraper():
    
    def __init(self, thing="things", num=1):
       
        self.files = {  "things": "things.txt",
                        "people": "persons.txt",
                        "companies": "businesses.txt",
                        "places": "places.txt",
                        "concepts": "concepts.txt"
                      }
        
        try:
            self.thing = thing
            self.num = num
            self.filename = self.files[self.thing]
            if not self.filename:
                print "got no filename for %s" % self.thing
                sys.exit(-1)
            else:
                print "get %s %s into (%s)" % (self.num, self.thing, self.filename)
            self.file = open(options.file, "a")            
            do_the_thing()
        finally:
            self.file.close()
            
    def do_the_thing(self):
        if self.thing == "things":
            self.get_random_things()
        elif self.thing == "people":
            self.get_random_people()
        elif self.thing == "companies":
            self.get_random_companies()
        elif self.thing == "concepts":
            self.get_random_concepts()
        elif self.thing == "places":
            self.get_random_places()

    def get_random_things(self):
        for i in range(self.num):
            url = "https://www.randomlists.com/things"
            r = requests.get(url)
            soup = BeautifulSoup(r.text)
            names = soup.findAll("span", { "class" : "name" })
            for name in names:
                n = str(name.contents[0].capitalize())
                p = n.split()
                s = ""
                for i in range(len(p)):
                    s += p[i].capitalize()
                    if i < len(p): s += " "
                if s == "Tv": s = "TV"
                if DEBUG: print s
                f_out.write(s + "\n")
            time.sleep(1)
            
    def get_random_people(self):
        print "get_random_people"
        
    def get_random_places(self):
        print "get_random_places"
        
    def get_random_companies(self):
        print "get_random_companies"
        
    def get_random_concepts(self):
        print "get_random_concepts"
                
if __name__ == '__main__':
    s = Scraper("things", 1)
