#!/usr/bin/env python

"""
main.py -- BeRated server-side Python App Engine
    HTTP controller handlers for memcache & task queue access

$Id$

created by tlichtenberg on 2015 sep 5

"""

__author__ = 'lichtenberg.tom@gmail.com (Tom Lichtenberg)'

import webapp2
from google.appengine.api import app_identity
from google.appengine.api import mail
from berated import BeRatedApi

class SetAnnouncementHandler(webapp2.RequestHandler):
    def get(self):
        """Set Announcement in Memcache."""
        # TODO 1


class SendConfirmationEmailHandler(webapp2.RequestHandler):
    def post(self):
        """Send email confirming Rating creation."""
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),     # from
            self.request.get('email'),                  # to
            'You created a new Rating!',            # subj
            'Hi, you have created a following '         # body
            'rating:\r\n\r\n%s' % self.request.get(
                'ratingInfo')
        )


app = webapp2.WSGIApplication([
    ('/crons/set_announcement', SetAnnouncementHandler),
    ('/tasks/send_confirmation_email', SendConfirmationEmailHandler),
], debug=True)
