#!/usr/bin/python
""" cherrypy_example.py

    COMPSYS302 - Software Design
    Author: Andrew Chen (andrew.chen@auckland.ac.nz)
    Last Edited: 19/02/2018

    This program uses the CherryPy web server (from www.cherrypy.org).
"""
# Requires:  CherryPy 3.2.2  (www.cherrypy.org)
#            Python  (We use 2.7)

# The address we listen for connections on
listen_ip = "0.0.0.0"
listen_port = 10004

import cherrypy
import urllib2
import hashlib
import socket
import json
import collections
import time
import string
import base64
import mimetypes
import dbFunc as dbLib
import os, os.path

class MainApp(object):
    
    #CherryPy Configuration
    _cp_config = {'tools.encode.on': True, 
                  'tools.encode.encoding': 'utf-8',
                  'tools.sessions.on' : 'True',
                 }                 

    # If they try somewhere we don't know, catch it here and send them to the right place.
    @cherrypy.expose
    def default(self, *args, **kwargs):
        """The default page, given when we don't recognise where the request is for."""
        Page = "I don't know where you're trying to go, so have a 404 Error."
        cherrypy.response.status = 404
        return Page

   
 
    """ Read HTML files that will be viewed in browser"""
    @cherrypy.expose
    def index(self):
	dbLib.initTables()
	return self.login()
        
    @cherrypy.expose
    def login(self):
	Page = open("./templates/login.html").read()
        return Page

    @cherrypy.expose
    def home(self):
	Page = open("./templates/home.html").read()
	return Page

    @cherrypy.expose
    def messaging(self):
	Page = open("./templates/messaging.html").read()
	return Page

    @cherrypy.expose
    def editP(self):
	Page = open("./templates/editP.html").read()
	return Page

    @cherrypy.expose
    def file(self):
	Page = open("./templates/file.html").read()
	return Page    

    """Function used by AJAX call to keep track of the current user"""
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getSessionUserJSON(self):
	return {'USERNAME': cherrypy.session.get('username')}

    """Function used by AJAX call to send a message"""
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def msgJS(self,destination,message):
	sender = cherrypy.session.get('username')
	self.sendMessage(sender,destination, message, None)
	return {'status':0}

    """Gets the file conversation of a user in JSON format"""
    @cherrypy.expose
    @cherrypy.tools.json_out() 
    def getFileJSON(self, username):
	return dbLib.getFile(username)


    """Sends a file by calling the receiver's API.
	Payload is JSON formatted.
	File is saved in static directory if successful"""
    @cherrypy.expose
    def sendFile(self, sender, destination, file1, ):

	url = dbLib.getUserAddress(destination)	+ "/receiveFile"
	
	#Obtain relevant inforamtion about the file
	sender = cherrypy.session.get('username')
	filename = file1.filename
	content_type = mimetypes.guess_type(filename)[0]
	bin = file1.file.read()
        stamp = time.time()

	#Creates a dictionary with the parameters
	key = ['sender', 'destination','file', 'filename', 'content_type', 'stamp', 'encoding', 'encryption', 'hashing', 'hash', 'decryptionKey', 'groupID' ]

	param = [sender, destination, base64.b64encode(bin), filename, content_type, float(stamp), 0, 0, 0, None, None, None ]

	data = collections.OrderedDict(zip(key,param))
        data = json.dumps(data)

        request = urllib2.Request(url,data, {'Content-Type': 'application/json'})
        error = urllib2.urlopen(request, timeout = 10)
	
	#saves the file
	save_path = './static/userFiles'
	nameFile = os.path.join(save_path, filename)         
	file = open(nameFile,'w') 
	file.write(bin)
	file.close()

	param[2] = save_path
	dbLib.insertFile(param)
	raise cherrypy.HTTPRedirect('/file')

    #Receives a payload, then saves the file and store the path of it
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveFile(self):
        data = cherrypy.request.json
	
	save_path = './static/userFiles'
	nameFile = os.path.join(save_path, data.get('filename'))         
	file = open(nameFile,'w') 
	file.write(base64.b64decode(data.get('file')))
	file.close()
	
	param = [data.get('sender'), data.get('destination'), save_path, data.get('filename'), data.get('content_type'), float(data.get('stamp')), data.get('encoding', 0), data.get('encryption', 0), data.get('hashing', 0), data.get('hash', None), data.get('decryptionKey', None), data.get('groupID', None)]
	dbLib.insertFile(param)

	return '0'

    """Sends a message by calling the receiver's API.
	Payload is JSON formatted.
	File is saved in static directory if successful"""
    @cherrypy.expose
    def sendMessage(self, sender, destination, message, stamp, encoding=0, encryption = '0', hashing = 0, hash = None, decryptionKey = None , groupID = None):

	url = dbLib.getUserAddress(destination) + "/receiveMessage"

	#Creates a dictionary of information to send
        stamp = time.time()
	key = ['sender', 'destination','message', 'stamp', 'encoding', 'encryption', 'hashing', 'hash', 'decryptionKey', 'groupID' ]
	param = [sender, destination, message, float(stamp), encoding, encryption, hashing, hash, decryptionKey, groupID ]
	data = collections.OrderedDict(zip(key,param))
        data = json.dumps(data)

        request = urllib2.Request(url,data, {'Content-Type': 'application/json'})
        error = urllib2.urlopen(request, timeout = 7.0)

	dbLib.insertMessage(param)

	"""Receives the payload and saveds the message in the database"""
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveMessage(self):
        data = cherrypy.request.json

        param = [data.get('sender'), data.get('destination'), data.get('message'), float(data.get('stamp')), data.get('encoding', 0), data.get('encryption', 0), data.get('hashing', 0), data.get('hash', None), data.get('decryptionKey', None), data.get('groupID', None)]

	dbLib.insertMessage(param)
	return '0'
        
    """Ping API for other clients to test if you are responding"""
    @cherrypy.expose    
    def ping(self, sender):
        return "0"
    
	"""Function used by AJAX call to optain information about the specified user"""
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getProfileJS(self, profile_username):
	self.updateProfile(profile_username)
	profile = dbLib.getProfile(profile_username)
	profile['lastUpdated'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(profile.get('lastUpdated'))))
	return profile

	"""Sends my current profile to the requester"""
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getProfile(self):
	data = cherrypy.request.json
	return dbLib.getProfile(data['profile_username'])
	
    """Edit your own profile"""
    @cherrypy.expose
    def profileEdit(self, profile_username, fullname, position, description, location, picture):
	data = {'fullname': fullname, 'position':position, 'description':description, 'location':location, 'picture':picture, 'encoding': 0, 'encryption':0, "decryptionKey":None , "lastUpdated":time.time()}	
	dbLib.updateProfile(data,profile_username)
	return json.dumps({"test":0})
	
    """Updates a profile in your database"""
    @cherrypy.expose
    def updateProfile(self, username):
	url = dbLib.getUserAddress(username) + "/getProfile"
	param = {'profile_username':username , 'sender': cherrypy.session.get('username')}
        param = json.dumps(param)
        request = urllib2.Request(url,param,{'Content-Type': 'application/json'} )

	try:
            data = urllib2.urlopen(request, timeout = 7.0).read()
	    data = json.loads(data)
	    dbLib.updateProfile(data, username)
	except urllib2.URLError as e:
            print ('Connection timeout')
	

 	"""Get list of online users and fill the rest of the table with dummy data"""
    @cherrypy.expose
    def getList(self):

        username = cherrypy.session.get('username')
        hash1 = hashlib.sha256(cherrypy.session.get('password')+username).hexdigest()

        test = urllib2.urlopen("http://cs302.pythonanywhere.com/getList?username="+username+"&password="+hash1+"&enc=0&json=1")
	output = test.read().decode('utf-8')

        json1 = json.loads(output)
	dbLib.deleteOnline()

        columns = ['username', 'ip', 'location', 'lastLogin', 'port'] 

        for index, data in json1.iteritems():
            param = [data.get('username'), data.get('ip'), data.get('location'), data.get('lastLogin'), data.get('port'), 'Online']
            dbLib.insertOnline(param)

	string1 = urllib2.urlopen("http://cs302.pythonanywhere.com/listUsers").read()
	userList = string1.split(',')
	for user in userList:
	    param = [user, "Not Online", None, 0, 69, None]
	    dbLib.insertOnline(param)
        return '0' 
    
	"""Function called by AJAX call to optain message conversions"""
    @cherrypy.expose
    @cherrypy.tools.json_out() 
    def getMsgJSON(self, username):
	return dbLib.getMessages(username)

	"""Function to get all users in the network"""
    @cherrypy.expose
    @cherrypy.tools.json_out() 
    def getAllUsersJSON(self):
	return dbLib.getAllUsers()
	
    """Gets the list of online users"""
    @cherrypy.expose
    @cherrypy.tools.json_out() 
    def onlineJSON(self):
	data = dbLib.getOnline()
        return data

    # LOGGING IN AND OUT
    @cherrypy.expose
    def signin(self, username=None, password=None):
        """Check their name and password and send them either to the main page, or back to the main login screen."""
        error = self.authoriseUserLogin(username,password)
        if (error == 0):
            cherrypy.session['username'] = username;
	    cherrypy.session['password'] = password;
            string1 = urllib2.urlopen("http://cs302.pythonanywhere.com/listUsers").read()
	    userList = string1.split(',')
	    dbLib.initUserList(userList)
	    self.getList()
            raise cherrypy.HTTPRedirect('/home')
        else:
            raise cherrypy.HTTPRedirect('/login')

    @cherrypy.expose
    def signout(self):
        """Logs the current user out, expires their session"""
        username = cherrypy.session.get('username')
        if (username == None):
            pass
        else:
            cherrypy.lib.sessions.expire()
        raise cherrypy.HTTPRedirect('/')
        
    def authoriseUserLogin(self, username, password):
	hash1 = hashlib.sha256(password+username).hexdigest()
	
	localip = socket.gethostbyname(socket.gethostname())

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip2 = s.getsockname()[0]
	s.close()

	publicip = urllib2.urlopen('http://ip.42.pl/raw').read()
        
	if localip.startswith("10."):
	    ip = localip;
            location = 0;
	elif ip2.startswith("172.23"):
	    ip = ip2;
            location = 1;
	else:
	    ip = publicip;
            location = 2;

        test = urllib2.urlopen("http://cs302.pythonanywhere.com/report?username=" + username+"&password="+ hash1+"&location="+str(location)+"&ip="+ip+"&port="+str(listen_port)+"&enc=0")
	output = test.read().decode('utf-8')
	print output
        if output[0] == str(0):
            return 0
        else:
            return 1
          
def runMainApp():
    conf = {
        '/': {
	    'tools.encode.on': True, 
            'tools.encode.encoding': 'utf-8',
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }
    dbLib.initTables()
    # Create an instance of MainApp and tell Cherrypy to send all requests under / to it. (ie all of them)
    cherrypy.tree.mount(MainApp(), "/", conf)

    # Tell Cherrypy to listen for connections on the configured address and port.
    cherrypy.config.update({'server.socket_host': listen_ip,
                            'server.socket_port': listen_port,
                            'engine.autoreload.on': True,
			    'log.error_file': "error.log",
                            'log.access_file': "Access.log"
                           })

    print "========================="
    print "University of Auckland "
    print "COMPSYS302 - Software Design Application"
    print "========================================"                       
    
    # Start the web server
    cherrypy.engine.start()

    # And stop doing anything else. Let the web server take over.
    cherrypy.engine.block()
 
#Run the function to start everything
runMainApp()
