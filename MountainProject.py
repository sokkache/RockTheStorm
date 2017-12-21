# MPkey = '200180467-8a0c5734e526a490c44ab6baf5ebc65e'
#googleKey = 'AIzaSyCflFXYgD0GnjEqcSqChTiFdhoJK_nEzmk'
#darkskyKey = '0011d827716f8b2db56daa4ecdedf415'

## Above are my keys for the API's I used
import webapp2, urllib, urllib2, webbrowser, json
import jinja2

import os
import logging

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
template_values = {}

# This class renders the template for inputs
class FirstHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("In FirstHandler")
        template_values['page_title'] = "Sunny Send"
        template = JINJA_ENVIRONMENT.get_template('MPTemplate.html')
        self.response.write(template.render(template_values))

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

# safeGet functions for URLS
def safeGet(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.HTTPError as e:
        print("The server couldn't fulfill the request.")
        print("Error code: ", e.code)
    except urllib2.URLError as e:
        print("We failed to reach a server")
        print("Reason: ", e.reason)
    return None


# Mountain Project API which returns the URL for Mountain Project
def MPREST(baseurl='https://www.mountainproject.com/data/get-routes-for-lat-lon?',
               api_key = MPkey,
               # max distance is set automatically to 50 miles
               params={},
               lat = '0',
               lon = '0',
               printurl=False
               ):
    params['key'] = api_key
    params['lat'] = lat
    params['lon'] = lon
    params['maxResults'] = '50' # max number of results is a large size
    url = baseurl + urllib.urlencode(params)
    if printurl:
        print(url)
    return safeGet(url)

# Google's geoLocate API url which returns the URl for the api
def geoLocateREST(baseurl='https://maps.googleapis.com/maps/api/geocode/json?',
               address = None,
               api_key = googleKey,
               params={},
               printurl=False
               ):
    params['address'] = address
    params['key'] = api_key
    url = baseurl + urllib.urlencode(params)
    if printurl:
        print(url)
    return safeGet(url)

# Return the precipation possibility in the passed in lon/lats
def darkSkyREST(baseurl = 'https://api.darksky.net/forecast/',
                lat = '0',
                lon = '0',
                printurl = False):
    url = baseurl + darkskyKey +"/" + lat +"," + lon
    if printurl:
        print(url)
    newUrl = safeGet(url)
    y = json.loads(newUrl.read())
    return y['currently']['precipProbability']


# returns the json file uploaded based on the google geolocate API and MountainProject
def getLatLonMP(address, maxDistance = '100', maxDiff = '5.15', minDiff = '5.1'):
    addressList = address.split()
    thisAddress=""
    for x in addressList:
        thisAddress += x + "+"
    geoURL = geoLocateREST(address = thisAddress)
    r = json.loads(geoURL.read())
    latitude = r['results'][0]['geometry']['location']['lat']
    longitude = r['results'][0]['geometry']['location']['lng']
    getUrl = MPREST(lat=latitude, lon=longitude , params = {'maxDistance' : maxDistance, 'maxDiff' : maxDiff, 'minDiff' : minDiff})
    x = json.loads(getUrl.read())
    return x

# provides a class for each route
class Routes():
    def __init__(self, dict):
        self.name = dict['name']
        self.crag = dict['location'][-2]
        self.area = dict['location'][-3]
        self.wall = dict['location'][-1]
        self.image = dict['imgSmall']
        self.type = dict['type']
        self.latitude = dict['latitude']
        self.longitude = dict['longitude']
        self.pitch = dict['pitches']
        self.rating = dict['rating']
        self.url = dict['url']

    def __str__(self):
        return self.name + " Area: " + self.area + " rating: " + self.rating + " pitch: " + str(self.pitch) + " type: " + self.type

# Provides a class for each area
class Area():
    def __init__(self, area, latitude, longitude):
        self.name = area
        self.latitude = str(latitude)
        self.longitude = str(longitude)

    def __str__(self):
        return self.name + " " + str(self.latitude) + " " + str(self.longitude)


# Returns the final dictionary of routes that are in good weather, this takes into account
# the DarkSky API and is passed into the final HTML template
def getRoutes(address, maxDistance, minDiff, maxDiff, type = "Sport"):
    dict = getLatLonMP(address = address, maxDistance = maxDistance, minDiff = minDiff, maxDiff = maxDiff)
    routeNames = {}
    areas = {}
    routeNames['routes'] = []
    routeNames['finalRoutes'] = []
    areasListFirst = []
    areasListFinal = []
    finalDict = {}
    for route in dict['routes']:
        routeNames['routes'].append(Routes(route))
    for route in routeNames['routes']:
        if route.area not in areas:
            areas[route.area] = []
            areasListFirst.append(Area(route.area, route.latitude, route.longitude))
    for x in areasListFirst:
        precip = darkSkyREST(lat = x.latitude, lon = x.longitude)
        if precip <= 0.2:
            areasListFinal.append(x.name)
    for route in routeNames['routes']:
            if route.area in areasListFinal:
                routeNames['finalRoutes'].append(route)
    for route in areasListFinal:
        print(route)
        print("***********")
    return routeNames

# returns a list of areas in the HTML template
def getAreas(dict):
    dict['areasList'] = []
    for route in dict['finalRoutes']:
        if route.area not in dict['areasList']:
            dict['areasList'].append(str(route.area))
    return dict

# Renders the final output based on the input handler
class MountainProjectHandlr(webapp2.RequestHandler):
    def post(self):
        address = self.request.get('address')
        maxDistance = self.request.get('maxDistance')
        maxDiff = self.request.get('maxDiff')
        minDiff = self.request.get('minDiff')
        dict = getRoutes(address, maxDistance, minDiff, maxDiff)
        dict = getAreas(dict)

        if dict:
            template = JINJA_ENVIRONMENT.get_template('MPFinal.html')
            self.response.write(template.render(dict))
        else:
            template = JINJA_ENVIRONMENT.get_template('MPTemplate.html')
            self.response.write(template.render(template_values))


application = webapp2.WSGIApplication([
    ('/gresponse', MountainProjectHandlr),
    ('/.*', FirstHandler)],debug=True)
