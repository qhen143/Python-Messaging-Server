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
    def logout(self):
        Page = '<form action="/signout">'
        Page += '<input type="submit" value="signout"/></form>'
        return Page

    @cherrypy.expose
    def msg(self,sender, destination):
        Page = '<form action=/sendMessage?sender='+sender+'&destination='+destination+'&stamp=abc method = "post">'
	Page += 'Message: <input type="text" name="message" value = message/><br/>'
        Page += '<input type="submit" value="send!"/></form>'
        return Page
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def msgJS(self,destination,message):
	print(destination)
	sender = cherrypy.session.get('username')
	self.sendMessage(sender,destination, message, "")
	return {'status':0}
	
    @cherrypy.expose
    def sendMessage(self, sender, destination, message, stamp, enc=0, encryption = None, hashing = 0, hash = "", decryptionKey = 0 , groupID = ""): #dont need all these params
	print("asasasasas")
	print(destination,sender,message,stamp)
	print("asasasasas")
	url = dbLib.getUserAddress(destination)
	print(url)
        stamp = str(time.time())
        #data = {'sender': sender, 'destination':destination, 'message': message, 'stamp': stamp, 'enc':enc, 'encryption':encryption, 'hashing':hashing, 'hash':hash, 'decryptionKey':decryptionKey, 'groupID':groupID }
	key = ['sender', 'destination','message', 'stamp', 'enc', 'encryption', 'hashing', 'hash', 'decryptionKey', 'groupID' ]
	param = [sender, destination,message, stamp, enc, encryption, hashing, hash, decryptionKey, groupID ]
	data = collections.OrderedDict(zip(key,param))

        data = json.dumps(data)
        request = urllib2.Request(url,data, {'Content-Type': 'application/json'})
        print(request)
        error = urllib2.urlopen(request)
        print(error.read())
	dbLib.insertMessage(param)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveMessage(self):
        data = cherrypy.request.json

	try:
            param = tuple([data['sender'],data['destination'],data['message'],data['stamp'],data['enc'],data['encryption'],data['hashing'],data['hash'],data['decryptionKey'],data['groupID']])
	    print(param)

	except KeyError:
	    param = tuple([data['sender'],data['destination'],data['message'],data['stamp'],'0', "", '0', "", "" , ""])
        
	dbLib.insertMessage(param)
	return '0'

    @cherrypy.expose    
    def ping(self, sender): #All inputs are strings by default
        return 0

    @cherrypy.expose    
    def sum(self, a=0, b=0): #All inputs are strings by default
        output = int(a)+int(b)
        return str(output)

    @cherrypy.expose
    def getList(self):
        username = cherrypy.session.get('username')
        hash1 = hashlib.sha256(cherrypy.session.get('password')+username).hexdigest()
        test = urllib.urlopen("http://cs302.pythonanywhere.com/getList?username="+username+"&password="+hash1+"&enc=0&json=1")
	output = test.read().decode('utf-8')
        json1 = json.loads(output)
        print(isinstance(json1, dict))
        print(json1)
        #db = sqlite3.connect('db/clientData')
        print("read")
        #cursor = db.cursor()
        #cursor.execute('''DELETE FROM online''')
	dbLib.deleteOnline()

        columns = ['username', 'ip', 'location', 'lastLogin', 'port']
        #insert data into database
        for index, data in json1.iteritems():
            keys = (index,) + tuple(data[c] for c in columns)
            #cursor.execute('''INSERT INTO online(ID, USERNAME, IP, LOCATION, LASTLOGIN, PORT)
            #      VALUES(?,?,?,?,?,?)''', keys)
            dbLib.insertOnline(keys)
        
        #display from database
        #cursor.execute('''SELECT * FROM online ORDER BY ID ASC''')
        #data = cursor.fetchall()
        Page = "<table><tr><td>id</td>"
        for x in columns:
            Page += "<td>"+str(x)+"</td>"
        Page += "</tr>"
        #for row in data:
        #    print(row)
        #    Page += "<tr>"
        #    for index in row:
        #        print(index)
        #        Page += "<td>"+str(index)+"</td>"
        #    Page += "</tr>"
        #Page += "</table>"

        #testing messaging table
        #Page += "<table><tr><td>" + columns[0] + "</td> <td> ping! </td> </tr>"
        #for row in data:
        #    Page += "<tr><td><a href='msg?sender="+username +"&destination=" + row[1] + "'>" + row[1] + "</a></td> <td><a href='"+row[2]+":"+str(row[5])+"/ping?sender=qhen143'>ping</a></td></tr>"
        #Page += "</table>"
        #print("asass" + str(self.ping("qhen143")))
        #db.commit()
        #db.close()
       
        return Page 
    
    def row2Dict(self,row):
	return dict(zip(row.keys(),row))	
    
    @cherrypy.expose
    @cherrypy.tools.json_out() 
    def getMsgJSON(self, username):
	print(dbLib.getMessages(username))
	return dbLib.getMessages(username)
	

	
    @cherrypy.expose
    @cherrypy.tools.json_out() 
    def onlineJSON(self):
	self.getList()
	#db = sqlite3.connect('db/clientData')
        #db.row_factory = sqlite3.Row
        #cursor = db.cursor()
	#keys = ["username", "lastlogin"]
	#cursor.execute("SELECT username, lastlogin FROM online ORDER BY username ASC")
	#data = []
	#print(cursor)
	#for row in cursor:
	#	print(row)
	#	print(row.keys())
	#	data.append(self.row2Dict(row))
		#print(data)

        #data = cursor.fetchall()
	#data = zip(keys, data)
	#data = dict(data)
	#data = json.dumps(data)
    	#db.close()
	data = dbLib.getOnline()
	print(type(data))
	print data
        return data
   
    # LOGGING IN AND OUT
    @cherrypy.expose
    def signin(self, username=None, password=None):
        """Check their name and password and send them either to the main page, or back to the main login screen."""
        error = self.authoriseUserLogin(username,password)
        if (error == 0):
            cherrypy.session['username'] = username;
	    cherrypy.session['password'] = password;
            #cherrypy.session['username'] = "abc";
	    #test1 = self.getList()
	    #test = self.onlineJSON()
	    print("asasasa")
            raise cherrypy.HTTPRedirect('/home')
        else:
            #raise cherrypy.HTTPRedirect('/login')
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
