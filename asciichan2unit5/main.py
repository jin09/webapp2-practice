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
import logging
import webapp2
import jinja2
import os
import urllib2
from xml.dom import minidom
from google.appengine.ext import db
from google.appengine.api import memcache

jinja_env = jinja2.Environment(autoescape=True,
                               loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

link = "http://freegeoip.net/xml/"


def get_coordinates(ip):
    try:
        content = urllib2.urlopen(link + ip).read()
    except:
        print "error fetching url"

    if content:
        xml = minidom.parseString(content)
        lat = xml.getElementsByTagName("Latitude")[0].childNodes[0].nodeValue
        long = xml.getElementsByTagName("Longitude")[0].childNodes[0].nodeValue
        x = "%s,%s" % (str(lat), str(long))
        return x


map_link = "https://maps.googleapis.com/maps/api/staticmap?size=600x300&maptype=roadmap&key=AIzaSyDl70HmW2bLaafCiwtlDdM5cA1cZr-nJzA"
marker = "&markers=color:red%7Clabel:C%7C"


def create_map_link():
    all = db.GqlQuery("select * from Arts")
    final_str = map_link
    for i in all:
        lat = str(i.coords).split(',')[0]
        lng = str(i.coords).split(',')[1]
        if not (lat == "0" and lng == "0"):
            mark = marker
            mark = mark + lat + "," + lng
            final_str = final_str + mark
    return final_str


class Arts(db.Model):
    title = db.StringProperty(required=True)
    art = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    coords = db.StringProperty(required=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


#cache = {} we will now make use of google's memcache


def optimized_arts(update=False):
    arts = db.GqlQuery("select * from Arts order by created desc limit 10")
    #arts = list[arts]
    return arts


class MainHandler(Handler):
    def render_front(self, title="", art="", error=""):
        arts = optimized_arts()
        cords = []
        for i in arts:
            cords.append(str(i.coords))

        map_url = create_map_link()
        # self.response.write(map_url)
        self.render("asciichan.html", title=title, art=art, error=error, arts=arts, map_url=map_url, cords=cords)

    def get(self):
        test = db.GqlQuery("select * from Arts")
        booli = False
        for i in test:
            if i.title == "ylo":
                booli = True
                break

        if not booli:
            self.response.out.write("not")
        else:
            self.response.out.write("yes")


    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")
        coords = get_coordinates(str(self.request.remote_addr))
        if title and art and coords:
            a = Arts(title=title, art=art, coords=coords)
            a.put()
            self.redirect('/')
        else:
            error = "Enter both title and art"
            self.render_front(title=title, art=art, error=error)


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
