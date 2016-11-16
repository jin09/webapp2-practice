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


class Handler(webapp2.RequestHandler):
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template,**kw))


class Post(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    time = db.DateTimeProperty(auto_now_add=True)


class MainHandler(Handler):
    def get(self):
        self.render("home.html")


class BlogHandler(Handler):
    def render_blog(self):
        posts = db.GqlQuery("select * from Post order by time desc limit 10")
        self.render("blog.html",list_of_post=posts)

    def get(self):
        self.render_blog()


class PermalinkHandler(Handler):
    def get(self,post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)

        if post:
            self.render("permalink.html", post=post)
        else:
            self.error(404)


class NewPostHandler(Handler):
    def render_form(self,title="",content="",error=""):
        self.render("newpost.html", error=error, content_value=content, title_value=title)

    def get(self):
        self.render_form()

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            p = Post(title=title, content=content)
            p.put()
            self.redirect("/blog/%s" % str(p.key().id()))

        else:
            error = "Both fields are necessary"
            self.render_form(title=title, content=content, error=error)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog',BlogHandler),
    ('/blog/([0-9]+)',PermalinkHandler),
    ('/blog/newpost',NewPostHandler)
], debug=True)
