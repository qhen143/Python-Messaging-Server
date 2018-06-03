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
import urllib
import urllib2
import hashlib
import socket
import sqlite3
import json
import collections
import time
import ast
import string


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

    # PAGES (which return HTML that can be viewed in browser)
    @cherrypy.expose
    def index(self):
	
        Page = "Welcome! This is a test website for COMPSYS302!<br/>"
        
        try:
            #Page = '<form action="/signin">'
            Page += "Hello " + cherrypy.session['username'] + "!<br/>"
	    Page += "This is bad practice " + cherrypy.session['password'] + "!<br/>"
            Page += "Here is some bonus text because you've logged in!"
	    #Page += "Click here to <a href='signout'>signoutaaa</a>."
            Page += self.logout()
            Page += self.list()
	    #Page += '<input type="submit" value="signout"/></form>'
        except KeyError: #There is no username
            
            Page += "Click here to <a href='login'>login</a>." #'login' is the link. Can be replaced with any function or link
        return Page
        
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
    def logout(self):
        Page = '<form action="/signout">'
        Page += '<input type="submit" value="signout"/></form>'
        return Page
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def msgJS(self,destination,message):
	sender = cherrypy.session.get('username')
	self.sendMessage(sender,destination, message, None)
	return {'status':0}
	
    @cherrypy.expose
    def sendMessage(self, sender, destination, message, stamp, encoding=0, encryption = '0', hashing = 0, hash = None, decryptionKey = None , groupID = None):

	url = dbLib.getUserAddress(destination) + "/receiveMessage"

        stamp = str(time.time())

	key = ['sender', 'destination','message', 'stamp', 'encoding', 'encryption', 'hashing', 'hash', 'decryptionKey', 'groupID' ]
	param = [sender, destination,message, stamp, encoding, encryption, hashing, hash, decryptionKey, groupID ]
	data = collections.OrderedDict(zip(key,param))

        data = json.dumps(data)
        request = urllib2.Request(url,data, {'Content-Type': 'application/json'})

        print(request)#remove later

        error = urllib2.urlopen(request)

        print(error.read())#remove later

	dbLib.insertMessage(param)

    #NEED TO RETEST
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveMessage(self):
        data = cherrypy.request.json

	try:
            param = tuple([data['sender'],data['destination'],data['message'],data['stamp'],data['encoding'],data['encryption'],data['hashing'],data['hash'],data['decryptionKey'],data['groupID']])
	    print(param)

	except KeyError:
	    param = tuple([data['sender'],data['destination'],data['message'],data['stamp'],'0', '0', '0', None, None , None])
        
	dbLib.insertMessage(param)
	return '0'
        
    @cherrypy.expose    
    def ping(self, sender):
        return 0
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getProfileJS(self, profile_username):
	self.updateProfile(profile_username)
	#print("goodbye",self.getProfile(profile_username, cherrypy.session.get('username')))
	#return self.getProfile(json.dumps({'profile_user':profile_username,'sender': cherrypy.session.get('username')}))
	return json.dumps(dbLib.getProfile(profile_username))

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getProfile(self):
	data = cherrypy.request.json
	print(data)
	#print("hello", dbLib.getProfile(data['profile_username'])
	return dbLib.getProfile(data['profile_username'])


	
    @cherrypy.expose
    def updateProfile(self, username):
	url = dbLib.getUserAddress(username) + "/getProfile"
	param = {'profile_username':username , 'sender': cherrypy.session.get('username')}
        param = json.dumps(param)
        request = urllib2.Request(url,param, {'Content-Type': 'application/json'})

        print(request)#remove later

        data = urllib2.urlopen(request).read()
	print("lllll",data)
	data = json.loads(data)
	print(data)
	dbLib.updateProfile(data, username)
	


    @cherrypy.expose
    def getList(self):

        username = cherrypy.session.get('username')
        hash1 = hashlib.sha256(cherrypy.session.get('password')+username).hexdigest()

        test = urllib.urlopen("http://cs302.pythonanywhere.com/getList?username="+username+"&password="+hash1+"&enc=0&json=1")
	output = test.read().decode('utf-8')

        json1 = json.loads(output)
	dbLib.deleteOnline()

        columns = ['username', 'ip', 'location', 'lastLogin', 'port'] #Should change to take into acc pkey
        #insert data into database
        for index, data in json1.iteritems():
            keys = (index,) + tuple(data[c] for c in columns)
            dbLib.insertOnline(keys)
        
        return '0' 
    
    @cherrypy.expose
    @cherrypy.tools.json_out() 
    def getMsgJSON(self, username):
	print(dbLib.getMessages(username))
	return dbLib.getMessages(username)

    @cherrypy.expose
    @cherrypy.tools.json_out() 
    def getAllUsersJSON(self):
	print(dbLib.getAllUsers())
	return dbLib.getAllUsers()
	
    @cherrypy.expose
    @cherrypy.tools.json_out() 
    def onlineJSON(self):
	self.getList()
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
            raise cherrypy.HTTPRedirect('/home')
        else:
            raise cherrypy.HTTPRedirect('/sum?a=3&b=5')

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
        print username
        print password
#B3FCE8CFCA6465845E55964425D585E874818DC351037B88858C413CECAEDB19
	hash1 = hashlib.sha256(password+username).hexdigest()
	
	#ip = socket.gethostbyname(socket.gethostname())
	
	#s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #s.connect(("8.8.8.8", 80))
        #ip = s.getsockname()[0]
        #print(s.getsockname()[0])
        #s.close()

	ip = urllib2.urlopen('http://ip.42.pl/raw').read()
	print ip
        test = urllib.urlopen("http://cs302.pythonanywhere.com/report?username=" + username+"&password="+ hash1+"&location=2&ip="+ip+"&port="+str(listen_port)+"&enc=0")
	output = test.read().decode('utf-8')
	print output
        print username
        if output[0] == str(0):
            return 0
	    print "asaslasd"
        else:
            return 1
          
def runMainApp():
    conf = {
        '/': {
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
