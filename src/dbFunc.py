import sqlite3
import collections

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
        return "http://"+ str(userData['IP']) +":"+ str(userData['PORT']) + "/receiveMessage"

def insertMessage(parameters):
	db = sqlite3.connect('db/clientData')
        cursor = db.cursor()
	cursor.execute('''INSERT INTO messages(sender, destination, message, stamp, enc, encryption, hashing, hash, decryptionKey, groupID)
                 VALUES(?,?,?,?,?,?,?,?,?,?)''', parameters)
        db.commit()
        db.close()
	print("saved msg")


def insertOnline(parameters):
	db = sqlite3.connect('db/clientData')
	db.row_factory = sqlite3.Row
        cursor = db.cursor()
	cursor.execute('''INSERT INTO online(ID, USERNAME, IP, LOCATION, LASTLOGIN, PORT)
                  VALUES(?,?,?,?,?,?)''', parameters)
        db.commit()
        db.close()

def getOnline():
	db = sqlite3.connect('db/clientData')
	db.row_factory = sqlite3.Row
        cursor = db.cursor()
	cursor.execute("SELECT username, lastlogin FROM online ORDER BY username ASC")
	#keys = ["username", "lastlogin"]
	data = []
	print(cursor)
	for row in cursor:
		print(row)
		#print(row.keys())
		data.append(row2Dict(row))
        db.commit()
        db.close()
	return data


