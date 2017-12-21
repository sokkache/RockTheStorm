#key = AAIzaSyBsRbOdP2C-4eu-6dGXTn_HWXwcNJ7pxFs
#url = https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=AIzaSyBsRbOdP2C-4eu-6dGXTn_HWXwcNJ7pxFs

import json, urllib
import jinja2, os

# tell python where to look for template
JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)
template = JINJA_ENVIRONMENT.get_template('hw6flickrtemplate.html')
f = open("MPGetRoutes.html", 'w')
f.write(template.render())
f.close()
webbrowser.open('MPGetRoutes.html')