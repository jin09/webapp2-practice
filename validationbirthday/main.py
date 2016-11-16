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
import cgi

form = """
<form method="post">
	<label>Day
	<input name="day" value="%s">
	</label>
	
	<label>Month
	<input name="month" value="%s">
	</label>

	<label>Year
	<input name="year" value="%s">
	</label>
	<input type="submit">
</form>
"""

    


class MainHandler(webapp2.RequestHandler):
    
    def print_form(self,day,month,year):
    	#day = self.escape_html(day)
    	#month = self.escape_html(month)
    	#year = self.escape_html(year)
    	self.response.write(form%(day,month,year))


    def day_validation(self,day):
    	if(day.isdigit()):
    		day = int(day)
    		if(day > 0 and day < 32):
    			return day


    def month_validation(self,month):
    	month_list = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
    	for i in month_list:
    		if(month == i):
    			return month


    def year_validation(self,year):
    	if(year.isdigit()):
    		year = int(year)
    		if(year > 1900 and year < 2020):
    			return year


    def get(self):
        self.print_form("","","")

    
    def post(self):
    	day = self.request.get("day")
    	month = self.request.get("month")
    	year = self.request.get("year")
    	valid_day = self.day_validation(day)
    	valid_month = self.month_validation(month)
    	valid_year = self.year_validation(year)
    	if(valid_day and valid_month and valid_year):
    		self.redirect("/thanks")
    	else:
    		self.response.write("<p style = 'color : red'><b>INVALID DATE!! PLEASE TRY AGAIN</b></p>")
    		self.print_form(day,month,year)


class ThanksHandler(webapp2.RequestHandler):
	def get(self):
		self.response.write("<p style='color : green'><b>Thats a valid date you have entered !<b></p>")


app = webapp2.WSGIApplication([
    ('/', MainHandler),("/thanks",ThanksHandler)
], debug=True)
