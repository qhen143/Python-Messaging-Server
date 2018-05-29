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
import hashlib
import socket
import sqlite3
import json

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
        Page = '<form action="/signin" method="post" enctype="multipart/form-data">' #signin the fucntion that the button does
        Page += 'Username: <input type="text" name="username"/><br/>'
        Page += 'Password: <input type="text" name="password"/>'
        Page += '<input type="submit" value="Loginxd"/></form>'
        return Page

    @cherrypy.expose
    def logout(self):
        Page = '<form action="/signout">'
        Page += '<input type="submit" value="signout"/></form>'
        return Page

    @cherrypy.expose
    def list(self):
        Page = '<form action="/getList">'
        Page += '<input type="submit" value="getList"/></form>'
        return Page

    @cherrypy.expose
    def msg(self,sender, destination):
        Page = '<form action="/receiveMessage?sender="'+sender+'"&destination="'+destination+'"&message=""&stamp="abc"" method = "post">'
	Page += 'Message: <input type="text" name="message"/><br/>'
        Page += '<input type="submit" value="send!"/></form>'
        return Page
    
    @cherrypy.expose
    def receiveMessage(self, sender, destination, message, stamp, enc=0, hashing = 0, hash = "", decryptionKey = 0 , groupID = ""): 
        print("hello")


    @cherrypy.expose    
    def sum(self, a=0, b=0): #All inputs are strings by default
        output = int(a)+int(b)
        return str(output)

    @cherrypy.expose
    def getList(self):
        username = cherrypy.session.get('username')
	#password = cherrypy.session.get('password')
	print username
	#print password
        #hash1 = hashlib.sha256(password+username).hexdigest()
        hash1 = hashlib.sha256(cherrypy.session.get('password')+username).hexdigest()
        test = urllib.urlopen("http://cs302.pythonanywhere.com/getList?username="+username+"&password="+hash1+"&enc=0&json=1")
	output = test.read().decode('utf-8')
        json1 = json.loads(output)
        print(isinstance(json1, dict))
        print(json1)
        db = sqlite3.connect('db/clientData')
        print("read")
        cursor = db.cursor()
        cursor.execute('''DELETE FROM online''')
        #cursor.execute('''CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT,
        #               ip TEXT, location INTEGER, lastlogin TEXT, port INTEGER)''')
        #db.commit()
        #cursor.execute('''INSERT INTO online(ID, USERNAME, IP, LOCATION, LASTLOGIN, PORT)
        #          VALUES(?,?,?,?,?,?)''', (4, "abc","123", 2, "1s1s1", 1004))
        columns = ['username', 'ip', 'location', 'lastLogin', 'port']
        #insert data into database
        for index, data in json1.iteritems():
            keys = (index,) + tuple(data[c] for c in columns)
            cursor.execute('''INSERT INTO online(ID, USERNAME, IP, LOCATION, LASTLOGIN, PORT)
                  VALUES(?,?,?,?,?,?)''', keys)
        
        #display from database
        cursor.execute('''SELECT * FROM online ORDER BY ID ASC''')
        data = cursor.fetchall()
        Page = "<table><tr><td>id</td>"
        for x in columns:
            Page += "<td>"+str(x)+"</td>"
        Page += "</tr>"
        for row in data:
            print(row)
            Page += "<tr>"
            for index in row:
                print(index)
                Page += "<td>"+str(index)+"</td>"
            Page += "</tr>"
        Page += "</table>"

        #testing messaging table
        Page += "<table><tr><td>" + columns[0] + "</td></tr>"
        for row in data:
            Page += "<tr><td><a href='msg?sender="+username +"&destination=" + row[1] + "'>" + row[1] + "</a></td></tr>"
        Page += "</table>"
        
        db.commit()
        #if test == 0:
        #Page = output
        #else:
        #    Page = "not allowed"
        db.close()
        return Page
#{"0": {"username": "hpat255", "ip": "115.188.149.214", "location": "2", "lastLogin": "1527417969", "port": "10001"}, "1": {"username": "acha932", "ip": "192.168.1.96", "location": "2", "lastLogin": "1527418005", "port": "8080"}, "2": {"username": "ccho416", "ip": "121.74.162.159", "location": "2", "lastLogin": "1527418022", "port": "10001"}, "3": {"username": "qhen143", "ip": "127.0.1.1", "location": "2", "lastLogin": "1527418183", "port": "10004"}}
        
    # LOGGING IN AND OUT
    @cherrypy.expose
    def signin(self, username=None, password=None):
        """Check their name and password and send them either to the main page, or back to the main login screen."""
        error = self.authoriseUserLogin(username,password)
        if (error == 0):
            cherrypy.session['username'] = username;
	    cherrypy.session['password'] = password;
            #cherrypy.session['username'] = "abc";
            raise cherrypy.HTTPRedirect('/')
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
#hashpass = hashlib.
#B3FCE8CFCA6465845E55964425D585E874818DC351037B88858C413CECAEDB19
        #test = urllib.urlopen("http://127.0.0.1:1234/sum?a=0&b=0")
	#test = urllib.urlopen("http://localhost:10004/sum?a=0&b=0")
	hash1 = hashlib.sha256(password+username).hexdigest()
	#ip = socket.gethostbyname(socket.getfqdn())
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        print(s.getsockname()[0])
        s.close()
	print ip
        test = urllib.urlopen("http://cs302.pythonanywhere.com/report?username=" + username+"&password="+ hash1+"&location=2&ip="+ip+"&port="+str(listen_port)+"&enc=0")
        #if (username.lower() == "andrew") and (password.lower() == "password"):
        #print test
	output = test.read().decode('utf-8')
	#print test.read().decode('utf-8')
	print output
        print username
        if output[0] == str(0):
            return 0
	    print "asaslasd"
        else:
            return 1
          
def runMainApp():
    # Create an instance of MainApp and tell Cherrypy to send all requests under / to it. (ie all of them)
    cherrypy.tree.mount(MainApp(), "/")

    # Tell Cherrypy to listen for connections on the configured address and port.
    cherrypy.config.update({'server.socket_host': listen_ip,
                            'server.socket_port': listen_port,
                            'engine.autoreload.on': True,
                           })

    print "========================="
    print "University of Auckland"
    print "COMPSYS302 - Software Design Application"
    print "========================================"                       
    
    # Start the web server
    cherrypy.engine.start()

    # And stop doing anything else. Let the web server take over.
    cherrypy.engine.block()
 
#Run the function to start everything
runMainApp()
