import sqlite3
import collections

def initTables():
	db = sqlite3.connect('db/clientData')
        cursor = db.cursor()
	cursor.execute('''CREATE TABLE IF NOT EXISTS online(USERNAME TEXT UNIQUE PRIMARY KEY, IP TEXT NOT NULL, PKEY TEXT, LOCATION INTEGER, LASTLOGIN TEXT, PORT INTEGER NOT NULL, ONLINE TEXT)''')
	cursor.execute('''CREATE TABLE IF NOT EXISTS messages(ID INTEGER PRIMARY KEY, SENDER TEXT NOT NULL, DESTINATION TEXT NOT NULL, MESSAGE TEXT, STAMP TEXT, ENC INTEGER, ENCRYPTION INTEGER, HASHING INTEGER, HASH TEXT, DECRYPTIONKEY TEXT, GROUPID TEXT)''')
	cursor.execute('''CREATE TABLE IF NOT EXISTS files(ID INTEGER PRIMARY KEY, SENDER TEXT NOT NULL, DESTINATION TEXT NOT NULL, FILE TEXT, FILENAME TEXT, CONTENT_TYPE TEXT, STAMP TEXT, ENC INTEGER, ENCRYPTION INTEGER, HASHING INTEGER, HASH TEXT, DECRYPTIONKEY TEXT, GROUPID TEXT)''')
	cursor.execute('''CREATE TABLE IF NOT EXISTS profile(USERNAME TEXT UNIQUE PRIMARY KEY, FULLNAME TEXT, POSITION TEXT, DESCRIPTION TEXT, LOCATION TEXT, LASTUPDATED TEXT NOT NULL, PICTURE TEXT, ENC INTEGER, ENCRYPTION INTEGER, DECRYPTIONKEY TEXT )''')
        db.commit()
        db.close()

def initUserList(userList):
	db = sqlite3.connect('db/clientData')
        cursor = db.cursor()
	for user in userList:
		cursor.execute(''' INSERT OR IGNORE INTO profile(username, fullname, position, description, location, lastupdated, picture, enc, encryption, decryptionKey) VALUES(?,?,?,?,?,?,?,?,?,?)''', [user, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', "imgur.com/a/FrbMAY5", 0, 0, None])
	db.commit()
        db.close()

def deleteOnline():
	db = sqlite3.connect('db/clientData')
        cursor = db.cursor()
	cursor.execute('''DELETE FROM online''')
        db.commit()
        db.close()

def row2Dict(row):
	return collections.OrderedDict(zip(row.keys(),row))

def getUserAddress(username):
        db = sqlite3.connect('db/clientData')
        db.row_factory = sqlite3.Row

        cursor = db.cursor()
        cursor.execute('''SELECT ip, port FROM online where username = ? ''', [username])
        row = cursor.fetchone()

	userData = row2Dict(row) 
	db.commit()
        db.close()
	return "http://"+ str(userData.get('IP',None)) +":"+ str(userData.get('PORT',None))

def insertMessage(parameters):
	db = sqlite3.connect('db/clientData')
        cursor = db.cursor()
	cursor.execute('''INSERT INTO messages(sender, destination, message, stamp, enc, encryption, hashing, hash, decryptionKey, groupID)
                 VALUES(?,?,?,?,?,?,?,?,?,?)''', parameters)
        db.commit()
        db.close()
	print("saved msg")

def insertFile(parameters):
	db = sqlite3.connect('db/clientData')
        cursor = db.cursor()
	cursor.execute('''INSERT INTO files(sender, destination, file, filename, content_type, stamp, enc, encryption, hashing, hash, decryptionKey, groupID)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', parameters)
        db.commit()
        db.close()
	print("saved file")

def getFile(username):
	db = sqlite3.connect('db/clientData')
	db.row_factory = sqlite3.Row
        cursor = db.cursor()
	cursor.execute('''SELECT sender, destination, file, filename, content_type, stamp FROM files where sender = ? OR destination = ? ORDER BY stamp ASC''', [username,username])
	data = []
	for row in cursor:
		data.append(row2Dict(row))
        db.commit()
        db.close()
	print("retreived file")
	return data

def getMessages(username):
	db = sqlite3.connect('db/clientData')
	db.row_factory = sqlite3.Row
        cursor = db.cursor()
	cursor.execute('''SELECT sender, destination, message, stamp FROM messages where sender = ? OR destination = ? ORDER BY stamp ASC''', [username,username])
	data = []
	
	for row in cursor:
		data.append(row2Dict(row))
        db.commit()
        db.close()
	print("retreived msg")
	return data


def insertOnline(parameters):
	db = sqlite3.connect('db/clientData')
	db.row_factory = sqlite3.Row
        cursor = db.cursor()
	cursor.execute('''INSERT OR IGNORE INTO online(USERNAME, IP, LOCATION, LASTLOGIN, PORT, ONLINE)
                  VALUES(?,?,?,?,?,?)''', parameters)
        db.commit()
        db.close()
	print("saved Online")

def getOnline():
	db = sqlite3.connect('db/clientData')
	db.row_factory = sqlite3.Row
        cursor = db.cursor()
	cursor.execute("SELECT username, lastlogin, location, online FROM online ORDER BY username ASC")
	data = []
	for row in cursor:
		data.append(row2Dict(row))
        db.commit()
        db.close()
	print("retreived online")
	return data

def getProfile(username):
	db = sqlite3.connect('db/clientData')
	db.row_factory = sqlite3.Row
        cursor = db.cursor()
	cursor.execute('''SELECT username, lastupdated, fullname, position, description, location, picture, enc, encryption, decryptionKey FROM profile where username = ?''', [username])
	row = cursor.fetchone()
	keys = ['username', "lastUpdated", 'fullname', 'position', 'description', 'location', 'picture', 'encoding', 'encryption', "decryptionKey"]	
	data = dict(zip(keys,row))
	db.commit()
        db.close()
	print("retreived profile")
	return data

def updateProfile(data,username):
	db = sqlite3.connect('db/clientData')
        cursor = db.cursor()
	data = dict(data)
	info = [str(data.get('lastUpdated',None)), data.get('fullname',), data.get('position',None), data.get('description',None), data.get('location',None), data.get('picture',None), data.get('encoding',None), data.get('encryption',None), data.get('decryptionKey',None), username ]
	cursor.execute('''UPDATE profile SET lastUpdated = ?, fullname = ?, position = ?, description = ?, location = ?, picture = ?, enc = ?, encryption = ?, decryptionKey = ? WHERE USERNAME = ? ''', info)
	row = cursor.fetchone()
	db.commit()
        db.close()
	print("Updated Profile")

def getAllUsers():
	db = sqlite3.connect('db/clientData')
	db.row_factory = sqlite3.Row
        cursor = db.cursor()
	cursor.execute("SELECT username FROM profile ORDER BY username ASC")
	data = []
	for row in cursor:
		data.append(row2Dict(row))
	db.commit()
        db.close()
	return data

