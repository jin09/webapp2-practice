#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
from google.appengine.ext import db
import hashlib
import hmac

SECRET = "IMASECRET"

jinja_env = jinja2.Environment(autoescape=True,
                               loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()


def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))


def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val


class Handler(webapp2.RequestHandler):
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template,**kw))


class MainHandler(Handler):
    def get(self):
        visits = 0
        visit_cookie = self.request.cookies.get('visits')
        if visit_cookie:
            cookie_val = check_secure_val(visit_cookie)
            if cookie_val:
                visits = int(cookie_val) + 1

        self.response.headers.add_header('Set-Cookie',"visits=%s"% make_secure_val(str(visits)))
        if visits >= 1000:
            self.write("You are the best customer we've had !!")
        else:
            self.write("You have been here %s times"% str(visits))

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
