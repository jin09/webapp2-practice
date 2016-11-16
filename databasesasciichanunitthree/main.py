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

jinja_env = jinja2.Environment(autoescape=True,
                               loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


class Art(db.Model):
    title = db.StringProperty(required=True)
    art = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class Handler(webapp2.RequestHandler):
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template,**kw))


class MainHandler(Handler):
    def render_front(self,title="",art="",error=""):
        arts = db.GqlQuery("select * from Art order by created desc")
        self.render("index.html",title = title, error=error, art=art, arts=arts)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        asciiart = self.request.get("art")
        if title and asciiart:
            a = Art(title=title,art=asciiart)
            a.put()
            self.redirect("/")
        else:
            error = "WE NEED BOTH TITLE AND ART"
            self.render_front(title, asciiart, error)


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)