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
import random
import string
import webapp2
import jinja2
import os
import re
import hmac
from google.appengine.ext import db
import hashlib

SECRET = "bLah!bLaH|SecreT|Key!!"

jinja_env = jinja2.Environment(autoescape=True,
                               loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))


def make_user_cookie(user_val):
    return "%s|%s" % (str(user_val),str(hmac.new(SECRET,str(user_val)).hexdigest()))


def check_valid_cookie(test_cookie):
    user_val = test_cookie.split('|')[0]
    if make_user_cookie(user_val) == test_cookie:
        return True
    else:
        return False


def create_pass_hash(pwd,name):
    salt = make_salt()
    h = hashlib.sha256(name+pwd+salt).hexdigest()
    return "%s,%s" % (h,salt)


def check_valid_pass(pass_val,pass_hash,username):
    h = hashlib.sha256(username+pass_val+pass_hash.split(',')[1]).hexdigest()
    if h == pass_hash.split(',')[0]:
        return True
    else:
        return False


class user_table(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty

    @classmethod
    def by_name(cls,name):
        u = user_table.all().filter('name=', name).get()
        return u


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


def valid_username(username):
    if username and USER_RE.match(username):
        return True
    else:
        return False


PASS_RE = re.compile(r"^.{3,20}$")


def valid_pass(passw):
    if passw and PASS_RE.match(passw):
        return True
    else:
        return False

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")


def valid_email(email):
    if email and EMAIL_RE.match(email):
        return True
    else:
        return False


class Handler(webapp2.RequestHandler):
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template,**kw))


class MainHandler(Handler):

    def render_front(self,username_value="",username_error="",pass_value="",pass_error="",verifypass_value="",verifypass_error="",email_value="",email_error=""):
        self.render("signup.html",username_value = username_value,username_error=username_error,
                    pass_value=pass_value,pass_error=pass_error,verifypass_value=verifypass_value,
                    verifypass_error=verifypass_error,email_value=email_value,email_error=email_error)

    def get(self):
        self.render_front()

    def post(self):
        is_error = False
        username = self.request.get("username")
        passw = self.request.get("pass")
        verify_pass = self.request.get("verify_pass")
        email = self.request.get("email")
        username_error = ""
        pass_error = ""
        verifypass_error = ""
        email_error = ""
        if username:
            if valid_username(username) == False:
                is_error = True
                username_error = "That's not a valid username"

        if is_error == False:
            all = db.GqlQuery("select * from user_table")
            for i in all:
                if i.name == username:
                    is_error = True
                    username_error = "username already exists !!"

        if passw:
            if valid_pass(passw) == False:
                is_error = True
                pass_error = "Your password isn't strong enough !!"

        if valid_pass(passw) == True:
            if (verify_pass != passw):
                is_error = True
                verifypass_error = "Passwords Don't match"

        if (email):
            if (valid_email(email) == False):
                is_error = True
                email_error = "Invalid Email address"

        if (is_error == True):
            self.render_front(username, username_error, passw,
                        pass_error, verify_pass,
                        verifypass_error, email, email_error)
        else:
            pass_hash = create_pass_hash(passw,username)
            row = user_table(name=username,pw_hash=pass_hash,email=email)
            row.put()

            id = row.key().id()
            cookie = make_user_cookie(id)
            self.response.headers.add_header('Set-Cookie', "user_id=%s" % str(cookie))
            self.redirect('/welcome')


class WelcomeHandler(Handler):
    def get(self):
        user_id = self.request.cookies.get("user_id","0")
        if user_id == "0":
            self.redirect('/')
        if check_valid_cookie(user_id) == True:
            id = user_id.split('|')[0]
            key = db.Key.from_path('user_table',int(id))
            row = db.get(key)
            self.render("welcome.html",row=row)
        else:
            self.redirect('/')


class LoginHandler(Handler):
    def render_form(self,username_value="",username_error="", pass_val="", pass_error=""):
        self.render("login.html",username_value=username_value,username_error=username_error, pass_value=pass_val, pass_error=pass_error)

    def get(self):
        self.render_form()

    def post(self):
        username = self.request.get("username")
        passw = self.request.get("passw")
        username_error = ""
        pass_error = ""
        is_error = False
        all = db.GqlQuery("select * from user_table")
        test_global = all[0]

        if username:
            all = db.GqlQuery("select * from user_table")
            is_valid_name = False
            for i in all:
                if i.name == username:
                    test_global = i
                    is_valid_name = True
                    break
            if is_valid_name == False:
                username_error = "Invalid Username"
                is_error = True
        else:
            is_error = True
            username_error = "Invalid Username"

        if is_error == True:
            self.render_form(username,username_error,passw)

        else:
            if passw:
                actual_pass = test_global.pw_hash
                ans = check_valid_pass(passw,actual_pass,username)
                if ans == False:
                    pass_error = "Password does'nt match !!"
                    is_error = True

            if is_error == True:
                self.render_form(username,username_error,passw,pass_error)
            else:
                id = test_global.key().id()
                cookie = make_user_cookie(id)
                self.response.headers.add_header('Set-Cookie', "user_id=%s" % str(cookie))
                self.redirect('/welcome')


class LogoutHandler(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', "user_id=%s" % str(""))
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/welcome',WelcomeHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler)
], debug=True)
