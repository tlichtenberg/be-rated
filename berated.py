#!/usr/bin/env python

"""
berated.py -- BeRated server-side Python App Engine API;
    uses Google Cloud Endpoints

$Id: berated.py,v 1.00 2015/09/25 $

created by tlichtenberg on 2015 sep 5

"""

__author__ = 'lichtenberg.tom@gmail.com (Tom Lichtenberg)'


from datetime import datetime
import random
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from bemodels import ConflictException
from bemodels import Profile
from bemodels import ProfileForm
from bemodels import BooleanMessage
from bemodels import Rating
from bemodels import RatingForm
from bemodels import RatingForms
from bemodels import RatingQueryForm
from bemodels import RatingQueryForms
from bemodels import Browse
from bemodels import BrowseRatingsForm
from bemodels import BrowseRatingsForms
from bemodels import AutoRatingForm
from bemodels import Thing

import collections
from uuid import uuid1
from utils import getUserId
from ratings import AutoRatings
import ratings
from users import User
from operator import itemgetter

from settings import WEB_CLIENT_ID

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
MEMCACHE_ANNOUNCEMENTS_KEY = "RECENT_ANNOUNCEMENTS"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

DEFAULTS = {
    "ratedType": "Product",
    "ratedName": "Mr. Clean",
    "rating": 5,
}

OPERATORS = {
            'EQ':   '=',
            'GT':   '>',
            'GTEQ': '>=',
            'LT':   '<',
            'LTEQ': '<=',
            'NE':   '!='
            }

FIELDS =    {
            'RATED_TYPE': 'ratedType(Person,Product,Business,Place,Other)',
            'RATED_NAME': 'ratedName',
            'SORT_BY': 'sortBy(High,Low,Name,Num)',
            'LIMIT': 'limit(0=show all)',
            }

RATING_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeRatingKey=messages.StringField(1),
)

RATING_POST_REQUEST = endpoints.ResourceContainer(
    RatingForm,
    websafeRatingKey=messages.StringField(1),
)

AUTO_RATING_POST_REQUEST = endpoints.ResourceContainer(
    AutoRatingForm,
    websafeRatingKey=messages.StringField(1),
)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@endpoints.api(name='berated', version='v1', 
    allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
    scopes=[EMAIL_SCOPE])
class BeRatedApi(remote.Service):
    """Rating API v0.1"""

# - - - Rating objects - - - - - - - - - - - - - - - - -

    def _copyRatingToForm(self, rating, displayName):
        """Copy relevant fields from Rating to RatingForm."""
        cf = RatingForm()
        for field in cf.all_fields():
            if hasattr(rating, field.name):
                setattr(cf, field.name, getattr(rating, field.name))
            elif field.name == "websafeKey":
                setattr(cf, field.name, rating.key.urlsafe())
        cf.check_initialized()
        print cf
        return cf
    
    def _copyBrowseRatingToForm(self, rating, displayName):
        """Copy relevant fields from Browse to BrowseRatingsForm."""
        cf = BrowseRatingsForm()
        for field in cf.all_fields():
            if hasattr(rating, field.name):
                setattr(cf, field.name, getattr(rating, field.name))
            elif field.name == "websafeKey":
                setattr(cf, field.name, rating.key.urlsafe())
        cf.check_initialized()
        print cf
        return cf

    def _createRatingObject(self, request):
        """Create or update Rating object, returning RatingForm/request."""
        # preload necessary data items
        user_id = self._create_anonymous_user()

        if not request.ratedName:
            raise endpoints.BadRequestException("Rating 'ratedName' field required")
        if not request.rating:
            raise endpoints.BadRequestException("Rating 'ratings' field required")

        # copy RatingForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        print "incoming data: %s" % data
        data['raterId'] = request.raterId = user_id
        data['createdAt'] = datetime.today().strftime('%Y%m%d')
        
        # generate Profile Key based on user ID and Rating
        # ID based on Profile key get Rating key from ID
        p_key = ndb.Key(Profile, user_id)
        c_id = request.ratedType + ":" + request.ratedName
        c_key = ndb.Key(Rating, c_id, parent=p_key)
        data['key'] = c_key
        print "outgoing data: %s" % data
        
        self._updateRatingObject(data)
        
        # TODO: does the object already exist in the Datastore?
        # If so, get its numRatings and cumRatings values, calculate aveRating
        # Store all that back into the database
        # requires deleting everything, starting over, changing the datastore type

        # create Rating, 
        #key = Rating(**data).put()
        #print key

        return request

    def _updateRatingObject(self, data):
        """
            get from datastore. if it already exists
            increment numRatings, cumulativeRating and recalculate averageRating
            then store/update in the db
            else, if it doesn't already exist, write it in with
            numRating=1, cumulativeRating=rating and averageRating=rating and id=random()
        """
        print "_updateRatingObject with data %s" % data
        query = "SELECT * from Rating where ratedName='%s' and ratedType='%s'" % (data['ratedName'], data['ratedType'])
        gql_response = ndb.gql(query)
        count = 0
        
        for p in gql_response:
            print "got a gql response, updating entry"
            count += 1
            print p
            print "%s %s, %d, %d, %d, %0.2f" % (p.ratedType, p.ratedName, p.rating, p.numRatings, p.cumulativeRating, p.averageRating)
            data['numRatings'] = p.numRatings + 1
            data['cumulativeRating'] = p.cumulativeRating + data['rating']
            data['averageRating'] = round(float( float(data['cumulativeRating']) / float(data['numRatings'])), 2)
        
        if count == 0:
            print "creating new entry"
            data['numRatings'] = 1
            data['cumulativeRating'] = data['rating']
            data['averageRating'] = float(data['rating'])
            data['id'] = random.randrange(1, 1000000000)
        
        key = Rating(**data).put()
        
    def _get_condition(self, query_string):
        if query_string.find("WHERE") > 0:
            return "AND"
        else:
            return "WHERE"
        
    def _create_gql_query(self, filters, user_id=None):
        sort_by = "High"  # default sorting
        limit = 100    
        query = "SELECT * from Rating"
        special_filters = 0
        
        inequality_filter, filters = self._formatFilters(filters)         
        for filtr in filters:          
            print "*** ", filtr, filtr['field']
            if str(filtr["field"]) == "ratedType(Person,Product,Business,Place,Other)":                             
                operator = str(filtr["operator"])
                condition = self._get_condition(query)
                if filtr["value"] in ["Person", "Product", "Business", "Place", "Other"]:
                    special_filters += 1 
                    query += " %s ratedType %s '%s'" % (condition, operator, filtr["value"])
            elif str(filtr["field"]) == "ratedName":
                if filtr["value"] and filtr["value"] != " ":
                    special_filters += 1  
                    operator = str(filtr["operator"])
                    condition = self._get_condition(query)
                    query += " %s ratedName %s '%s'" % (condition, operator, filtr["value"])
            elif str(filtr["field"]) == "sortBy(High,Low,Name,Num)":
                sort_by = filtr["value"] # this just gets returned
            elif str(filtr["field"]) == "limit(0=show all)":
                try:
                    limit = int(filtr["value"])
                except Exception as e:
                    print e   
                    
               
           
        print "special_filters = %d" % special_filters         
        if special_filters == 0: # if there are no filters other than limit or sort, get from today
           query += " where createdAt = '%s'" % datetime.today().strftime("%Y%m%d") 
           query += " limit %d" % limit  
        """
        else:
            if sort_by == "High":
                condition = self._get_condition(query)
                query += " %s averageRating >= 3.0" % condition
            elif sort_by == "Low":
                condition = self._get_condition(query)
                query += " %s averageRating < 3.0" % condition
            elif sort_by == "Name":
                #condition = self._get_condition(query)
                #query += " %s ratedName <= '%s'" % (condition, "D")  # ??
                print "TBD"
            elif sort_by == "Num":
                condition = self._get_condition(query)
                query += " %s numRatings >= 2" % condition # ??   
        """   
                        
        print "* * * gql query: %s" % query
        return query, limit, sort_by
    
    def _process_gql_response(self, gql_response, sort_by, limit=0):
        print limit
        got = {}
        for p in gql_response:
            print "%s %s, %d, %d, %d, %0.2f" % (p.ratedType, p.ratedName, p.rating, p.numRatings, p.cumulativeRating, p.averageRating)
            key = p.ratedType + "," + p.ratedName
            if got.has_key(key):
                #print "already have key: %s" % key
                got[key]["cumulative_rating"] = p.cumulativeRating
                got[key]["num_ratings"] = p.numRatings     
                got[key]['ave_rating'] = p.averageRating        
            else:
                new_key = p.ratedType + "," + p.ratedName
                #print "making new key: %s" % key
                got[new_key] = {}
                got[new_key]["cumulative_rating"] = p.cumulativeRating
                got[new_key]["num_ratings"] = p.numRatings
                got[key]['ave_rating'] = p.averageRating 
          
        got = collections.OrderedDict(sorted(got.items()))

        new_list = []
        #if limit == -1:
        #    print "limiting results to >1 numRatings"
        for k,v in got.iteritems():
            b = BrowseRatingsForm()
            p = k.split(",")
            b.ratedType = p[0]
            b.ratedName = p[1]
            b.averageRating = v['ave_rating']
            b.numRatings = v["num_ratings"]
            #if limit == -1: # special case for Top lists where we want > 1 ratings for an item to display
            #    if b.numRatings > 1:
            #        new_list.append(b)
            #else:
            new_list.append(b)
         
        print "* * * sort_by = %s" % sort_by
                        
        # TODO: re-sort 
        if sort_by == "High":
            results = sorted(new_list, key=lambda x: x.averageRating, reverse=True)
        elif sort_by == "Low":
            results = sorted(new_list, key=lambda x: x.averageRating, reverse=False)
        elif sort_by == "Name":
            results = sorted(new_list, key=lambda x: x.ratedName, reverse=False)
        elif sort_by == "Num":
            results = sorted(new_list, key=lambda x: x.numRatings, reverse=True)
        else:
            results = new_list
            
        # impose limit on return, truncated results to the first N in the array
        # we don't "limit" the GQL query, just the presentation of results
        if limit > 0:
            results = results[:limit]
            
        return results

    @endpoints.method(RatingForm, RatingForm, path='berated',
            http_method='POST', name='createRating')
    def createRating(self, request):
        """Create new Rating."""
        return self._createRatingObject(request)


    @endpoints.method(RATING_POST_REQUEST, RatingForm,
            path='berated/{websafeRatingKey}',
            http_method='PUT', name='updateRating')
    def updateRating(self, request):
        """Update Rating w/provided fields & return w/updated info."""
        print "deprecated"

    @endpoints.method(RatingQueryForms, BrowseRatingsForms,
            path='getRatingsCreated',
            http_method='POST', name='getRatingsCreated')
    def getRatingsCreated(self, request):
        """Return Ratings created by user."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id =  getUserId(user)
        #prof = ndb.Key(Profile, user_id).get()
        
        query, limit, sort_by = self._create_gql_query(request.filters, user_id)     
        gql_response = ndb.gql(query)
        results = self._process_gql_response(gql_response, sort_by, limit)
                  
        return BrowseRatingsForms(
            items=[self._copyBrowseRatingToForm(browse, getattr(browse, 'ratedName')) for browse in results]
        )
        
    @endpoints.method(RatingQueryForms, BrowseRatingsForms,
            path='browseRatings',
            http_method='POST',
            name='browseRatings')
    def browseRatings(self, request):
        """Query for Ratings."""
        query, limit, sort_by = self._create_gql_query(request.filters)     
        gql_response = ndb.gql(query)
        #print "gql_response: %s" % gql_response
        results = self._process_gql_response(gql_response, sort_by, limit)
        print results          
        return BrowseRatingsForms(
            items=[self._copyBrowseRatingToForm(browse, getattr(browse, 'ratedName')) for browse in results]
        )

    def _formatFilters(self, filters):
        """Parse, check validity and format user supplied filters."""
        formatted_filters = []
        inequality_field = None

        for f in filters:
            filtr = {field.name: getattr(f, field.name) for field in f.all_fields()}

            try:
                filtr["field"] = FIELDS[filtr["field"]]
                filtr["operator"] = OPERATORS[filtr["operator"]]
            except KeyError:
                raise endpoints.BadRequestException("Filter contains invalid field or operator.")

            # Every operation except "=" is an inequality
            if filtr["operator"] != "=":
                # check if inequality operation has been used in previous filters
                # disallow the filter if inequality was performed on a different field before
                # track the field on which the inequality operation is performed
                if inequality_field and inequality_field != filtr["field"]:
                    raise endpoints.BadRequestException("Inequality filter is allowed on only one field.")
                else:
                    inequality_field = filtr["field"]

            formatted_filters.append(filtr)
        return (inequality_field, formatted_filters)


# - - - Profile objects - - - - - - - - - - - - - - - - - - -

    def _copyProfileToForm(self, prof):
        """Copy relevant fields from Profile to ProfileForm."""
        # copy relevant fields from Profile to ProfileForm
        pf = ProfileForm()
        for field in pf.all_fields():
            if hasattr(prof, field.name):
                setattr(pf, field.name, getattr(prof, field.name))
        pf.check_initialized()
        return pf

    def _getProfileFromUser(self):
        """Return user Profile from datastore, creating new one if non-existent."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # get Profile from datastore
        user_id = getUserId(user)
        print "user_id: %s" % user_id
        p_key = ndb.Key(Profile, user_id)
        print "p_key: %s" % p_key
        profile = p_key.get()
        print "profile: %s" % profile
        
        # create new Profile if not there
        if not profile:
            print "profile is None?"
            profile = Profile(
                key = p_key,
                displayName = user.nickname(),
                mainEmail= user.email(),
                gender = "not specified",
                birthDate = datetime.today().strftime('%m/%d/%Y'),
                zipCode = "00000",
            )
            profile.put()

        return profile      # return Profile

    def _doProfile(self, save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        # get user Profile
        prof = self._getProfileFromUser()
        print "prof in _doProfile: %s" % prof

        # if saveProfile(), process user-modifiable fields
        if save_request:
            for field in ('displayName', 'gender', 'zipCode', 'birthDate'):
                if hasattr(save_request, field):
                    print "has_attr: %s" % field
                    val = getattr(save_request, field)
                    if val:
                        print "setattr for %s, %s" % (field, str(val))
                        setattr(prof, field, str(val))
            print "save it"
            prof.put()

        # return ProfileForm
        return self._copyProfileToForm(prof)

    @endpoints.method(message_types.VoidMessage, ProfileForm,
            path='profile', http_method='GET', name='getProfile')
    def getProfile(self, request):
        """Return user profile."""
        return self._doProfile()
        
    @endpoints.method(ProfileForm, ProfileForm,
            path='profile', http_method='POST', name='saveProfile')
    def saveProfile(self, request):
        """Update & return user profile."""
        return self._doProfile(request)
    

        
    @endpoints.method(AUTO_RATING_POST_REQUEST, RatingForm,
            path='autoRatings',
            http_method='POST',
            name='autoRatings')
    def autoRatings(self, request):
        # copy RatingForm/ProtoRPC Message into dict
        params = {field.name: getattr(request, field.name) for field in request.all_fields()}
        numUsers = params["numUsers"]
        spread = params["spread"]
        
        profiles_seen = []
        rater = AutoRatings()
        ratings = rater.make_ratings(numUsers, spread, auto_user=True)
        for rating in ratings:
            data = {}           
            user_id = data['raterId'] = rating["userEmail"]    
            p_key = ndb.Key(Profile, user_id) or str(uuid.uuid1().get_hex()) # if None
            if user_id not in profiles_seen:
                profile = Profile(
                    key = p_key,
                    displayName = rating["userName"],
                    mainEmail= rating["userEmail"], 
                    gender = rating["gender"],
                    birthDate = rating["birthDate"],
                    zipCode = rating["zipCode"],
                )
                profile.put()
            else:
                profiles_seen.append(user_id)
                        
            c_id = Rating.allocate_ids(size=1, parent=p_key)[0]
            c_key = ndb.Key(Rating, c_id, parent=p_key)
            data['key'] = c_key
            data['createdAt'] = datetime.today().strftime('%Y%m%d')
            data["ratedType"] = rating["ratedType"]
            data["ratedName"] = rating["ratedName"]
            data["rating"] = int(rating["rating"])
            print "outgoing data: %s" % data

            # create Rating, 
            Rating(**data).put()
            
        # because it wants a return type
        return RatingForm()
    
    def _create_anonymous_user(self):
        #user = User()
        #userBits = user.name.split("_")
        #userEmail = user.name.replace("/","") + "@berated.com",
        #p_key = ndb.Key(Profile, userEmail) or str(uuid.uuid1().get_hex()) 
        #profile = Profile(  
        #    key = p_key,
        #    displayName = user.name,
        #    mainEmail= userEmail, 
        #    gender = userBits[1],
        #    birthDate = userBits[2],
        #    zipCode = userBits[3]
        #)
        #profile.put()
        #return profile
        #return user.email
        
        # same user every time, so the key is the same in the db
        return "zz_Female_08_30_1969_37568@berated.com"
    
    @endpoints.method(message_types.VoidMessage, RatingForm,
            path='filterPlayground',
            http_method='GET', name='filterPlayground')
    def filterPlayground(self, request):
        # just to play with
        
        # read in static files and write to ndb
        filenames = {  "Other": "concepts.txt",
                       "Business": "businesses.txt",
                       "Product": "products.txt",
                       "Person": "persons.txt",
                       "Places": "places.txt"  # Places, not Place
                     }
        
        for f in filenames.keys():
            things = []
            lines = open(filenames[f], "r").readlines()
            for line in lines:
                line = line.strip()
                #print line, len(line)
                thing = Thing(
                              category = f,
                              name = line
                              )
                things.append(thing)
            # batch put
            ndb.put_multi(things)
                
        # does nothing 
        return RatingForm()
    
    @endpoints.method(message_types.VoidMessage, RatingForm,
            path='filterPlayground2',
            http_method='GET', name='filterPlayground2')
    def filterPlayground2(self, request):
        # just to play with
        
        fnames = open("first_names.txt", "r").readlines()
        lnames = open("last_names.txt", "r").readlines()
        ffnames = []
        llnames = []
        for f in fnames:
            try:
                p = f.split()
                if len(p) > 0:
                    ffnames.append(p[0].strip().lower().capitalize())
            except:
                pass
            
        for l in lnames:
            try:
                p = l.split()
                llnames.append(p[0].strip().lower().capitalize())
            except:
                pass
                
        random_keys = random.sample(ffnames, 100)
        
        for ll in llnames:
            things = []
            random_fnames = random.sample(ffnames, 100)  # random first names
            for r in random_fnames:
                fullname = r + " " + ll
                print fullname
                thing = Thing(
                              category = "Person",
                              name = fullname
                              )
                things.append(thing)
            # batch put
            ndb.put_multi(things)
                
        # does nothing 
        return RatingForm()
        
        

api = endpoints.api_server([BeRatedApi]) # register API
