# cron job
from ratings import AutoRatings
from bemodels import Rating
from google.appengine.ext import ndb
from bemodels import Profile
from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.logservice import logservice
from google.appengine.ext import ndb
import logging
import random

class Autogen(webapp.RequestHandler):
    
    def get(self):
        logging.getLogger().setLevel(logging.DEBUG)
        rater = AutoRatings()
        numUsers = 3
        spread = "40,80"
        ratings = rater.make_ratings(numUsers, spread, auto_user=True)
        try:
            for rating in ratings:
                data = {}           
                user_id = "zz_Female_08_30_1969_37568@berated.com" 
                p_key = ndb.Key(Profile, user_id)
                c_id = rating["ratedType"] + ":" + rating["ratedName"]
                c_key = ndb.Key(Rating, c_id, parent=p_key)
                data['key'] = c_key
                data['key'] = c_key
                data['createdAt'] = datetime.today().strftime('%Y%m%d')
                data["ratedType"] = rating["ratedType"]
                data["ratedName"] = rating["ratedName"]
                data["rating"] = int(rating["rating"])
                
                query = "SELECT * from Rating where ratedName='%s' and ratedType='%s'" % (data['ratedName'], data['ratedType'])
                gql_response = ndb.gql(query)
                count = 0
                
                for p in gql_response:
                    count += 1 # update existing object
                    print "%s %s, %d, %d, %d, %0.2f" % (p.ratedType, p.ratedName, p.rating, p.numRatings, p.cumulativeRating, p.averageRating)
                    data['numRatings'] = p.numRatings + 1
                    data['cumulativeRating'] = p.cumulativeRating + int(data['rating'])
                    data['averageRating'] = round(float( float(data['cumulativeRating']) / float(data['numRatings'])), 2)
                
                if count == 0: # create new rating object
                    data['numRatings'] = 1
                    data['cumulativeRating'] = int(rating['rating'])
                    data['averageRating'] = float(rating['rating'])
                    data['id'] = random.randrange(1, 1000000000)
                         
                # create Rating, 
                Rating(**data).put()
        except Exception as e:
            print e
        
app = webapp.WSGIApplication([('/autogen', Autogen)], debug=True)
 
def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(app)
 
if __name__ == "__main__":
    main() 