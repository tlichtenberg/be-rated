#!/usr/bin/env python

"""bemodels.py

BeRated server-side Python App Engine data & ProtoRPC models

$Id: bemodels.py,v 1.0 2015/09/25 $

created by tlichtenberg on 2015 sep 5

"""

__author__ = 'lichtenberg.tom@gmail.com (Tom Lichtenberg)'

import httplib
import endpoints
from protorpc import messages
from google.appengine.ext import ndb

class ConflictException(endpoints.ServiceException):
    """ConflictException -- exception mapped to HTTP 409 response"""
    http_status = httplib.CONFLICT

class Profile(ndb.Model):
    """Profile -- User profile object"""
    displayName = ndb.StringProperty()
    mainEmail = ndb.StringProperty()
    gender = ndb.StringProperty()
    zipCode = ndb.StringProperty()
    birthDate = ndb.StringProperty()

class ProfileForm(messages.Message):
    """ProfileForm -- Profile outbound form message"""
    displayName = messages.StringField(1)
    mainEmail = messages.StringField(2)
    gender = messages.StringField(3)
    zipCode = messages.StringField(4)
    birthDate = messages.StringField(5)

class BooleanMessage(messages.Message):
    """BooleanMessage-- outbound Boolean value message"""
    data = messages.BooleanField(1)

class Rating(ndb.Model):
    """Rating -- Rating object"""   
    ratedType               = ndb.StringProperty()
    ratedName               = ndb.StringProperty()
    raterId                 = ndb.StringProperty()
    rating                  = ndb.IntegerProperty() 
    numRatings              = ndb.IntegerProperty()
    cumulativeRating        = ndb.IntegerProperty()
    averageRating           = ndb.FloatProperty()
    id                      = ndb.IntegerProperty()
    createdAt               = ndb.StringProperty()
    
    @classmethod
    def query_mine(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(-cls.createdAt)
    
    @classmethod
    def query_all(cls):
        return cls.query().order(-cls.createdAt)

class RatingForm(messages.Message):
    """RatingForm -- Rating outbound form message"""
    ratedType       = messages.StringField(1)
    ratedName       = messages.StringField(2)
    rating          = messages.IntegerField(3)
    raterId         = messages.StringField(4)
    # rating created_at date to be calculated on input
    
class Browse(ndb.Model):
    """Rating -- Rating object"""
    ratedType               = ndb.StringProperty()
    ratedName               = ndb.StringProperty()
    averageRating           = ndb.FloatProperty()
    numRatings              = ndb.IntegerProperty()
    
class BrowseRatingsForm(messages.Message):
    """BrowseRatingsForm -- Rating outbound form message"""
    ratedType       = messages.StringField(1)
    ratedName       = messages.StringField(2)
    averageRating   = messages.FloatField(3)
    numRatings      = messages.IntegerField(4)
    
class BrowseRatingsForms(messages.Message):
    """BrowseRatingsForms -- multiple Browse outbound form message"""
    items = messages.MessageField(BrowseRatingsForm, 1, repeated=True)

class RatingForms(messages.Message):
    """RatingForms -- multiple Rating outbound form message"""
    items = messages.MessageField(RatingForm, 1, repeated=True)
    
class RatingQueryForm(messages.Message):
    """RatingQueryForm -- Rating query inbound form message"""
    field = messages.StringField(1)
    operator = messages.StringField(2)
    value = messages.StringField(3)

class RatingQueryForms(messages.Message):
    """RatingQueryForms -- multiple RatingQueryForm inbound form message"""
    filters = messages.MessageField(RatingQueryForm, 1, repeated=True)

class AutoRatingForm(messages.Message):
    """AutoRatingForm -- for private method"""
    numUsers       = messages.IntegerField(1)
    spread         = messages.StringField(2)
    # rating created_at date to be calculated on input
    
class Thing(ndb.Model):
    """Profile -- User profile object"""
    category = ndb.StringProperty()
    name     = ndb.StringProperty()