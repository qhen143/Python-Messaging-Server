import cherrypy

def getIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        localIP = s.getsockname()[0]
        print(s.getsockname()[0])
        s.close()

	publicIP = urllib2.urlopen('http://ip.42.pl/raw').read()
	
	if "" in otherIP:
	    ip = otherIP
	     location = '0'
	elif "" in localIP:
            ip = localIP
	    location = '1'
	else
	    ip = publicIP
	    location = '2'

class abc(object):

    @cherrypy.expose
    def login(self):
        Page = open("./templates/login.html").read()
        return Page
