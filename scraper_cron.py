# cron job
from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.logservice import logservice
from google.appengine.ext import ndb
import logging
import random
import uuid
from bemodels import Thing
from bs4 import BeautifulSoup
import requests
import string
import random
import time
import cgi
import urllib2

class ScraperCron(webapp.RequestHandler):
    
    def get(self):
        try:
            self.options = [  
                              "people",
                              "companies",
                              "products",
                              "other"
                            ]
            
            self.thing = random.choice(self.options)
            self.num = random.randrange(40,80) # 60)                   
            print "get %s %s" % (self.num, self.thing)                       
            self.do_the_thing()
        except Exception as e:
            print "exception: ", e
            
    def do_the_thing(self):
        if self.thing == "people":
            self.get_random_people()
        elif self.thing == "companies":
            self.get_random_companies()
        elif self.thing == "other":
            self.get_random_other()
        elif self.thing == "products":
            self.get_random_products()
            
    def get_random_people(self):
        print "get_random_people"
        url = "http://www.posh24.com/celebrities"
        things = []
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        _, params = cgi.parse_header(req.headers.get('Content-Type', ''))
        encoding = params.get('charset', 'utf-8')
        the_page = response.read().decode(encoding)
        txt = the_page.encode('utf-8')
        soup = BeautifulSoup(txt, from_encoding='utf-8')
        items = soup.findAll("div", {"class": "name" })
        final_items = random.sample(items, self.num)
        for item in final_items:
            txt = item.text.strip()
            print txt
            thing = Thing(
                          category = "Other",
                          name = txt
                          )
            things.append(thing)
        ndb.put_multi(things)
        
        # test getting a random thing back
        #q = Thing.query(Thing.category == 'people')
        #item_keys = q.fetch(1000000,keys_only=True)
        #random_keys = random.sample(item_keys, 1)
        #items = ndb.get_multi(random_keys)
        #for item in items:
        #    print item.name

    def get_random_products(self):        
        print "get_random_products"
        things = []
        url = "http://www.walmart.com/Value-of-the-Day"
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        _, params = cgi.parse_header(req.headers.get('Content-Type', ''))
        encoding = params.get('charset', 'utf-8')
        the_page = response.read().decode(encoding)
        txt = the_page.encode('utf-8')
        soup = BeautifulSoup(txt, from_encoding='utf-8')
        items = soup.findAll("span", {"class": "js-product-title" })
        final_items = random.sample(items, self.num)
        for item in final_items:
            txt = item.text
            if txt.endswith("."):
                txt = txt[:txt.rindex(" ")]
            print txt
            thing = Thing(
                          category = "Other",
                          name = txt
                          )
            things.append(thing)
        ndb.put_multi(things)
        
        
    def get_random_companies(self):
        print "get_random_companies"
        things = []
        letter = random.choice(string.letters).upper()
        url = "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=%s&pagesize=200" % letter
        try:
            #r = requests.get(url)    
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            _, params = cgi.parse_header(req.headers.get('Content-Type', ''))
            encoding = params.get('charset', 'utf-8')
            the_page = response.read().decode(encoding)
            txt = the_page.encode('utf-8')
            soup = BeautifulSoup(txt, from_encoding='utf-8')            
        except Exception as e:
            print "bs exception", e    
            return
        names = soup.findAll("a", { "target" : "_blank" })
        print "found %d targets on %s" % (len(names), url)
        if len(names) > 0:
            for i in range(self.num):                                 
                name = random.choice(names)
                try:
                    x = str(name.contents[0].encode('utf-8'))
                    print x
                    thing = Thing(
                                  category = "Business",
                                  name = x
                                  )
                    things.append(thing)
                except Exception as e:
                    print "my exception", e
        else:
            print "got nothing"
            return
            #time.sleep(1)
        # batch put
        ndb.put_multi(things)
        
    def get_random_other(self):
        things = []
        words = []
        print "get_random_other"
        url = "http://creativitygames.net/random-word-generator/randomwords/8"
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        _, params = cgi.parse_header(req.headers.get('Content-Type', ''))
        encoding = params.get('charset', 'utf-8')
        the_page = response.read().decode(encoding)
        txt = the_page.encode('utf-8')
        soup = BeautifulSoup(txt, from_encoding='utf-8')
        for i in range(1,9):
            item = soup.find("li", {"id": "randomword_%d" % i })
            words.append(item.text)
        for word in words:
            print word.capitalize()
            thing = Thing(
                          category = "Other",
                          name = word.capitalize()
                          )
            things.append(thing)
        ndb.put_multi(things)
        
app = webapp.WSGIApplication([('/scraper', ScraperCron)], debug=True)
 
def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(app)
 
if __name__ == "__main__":
    main() 