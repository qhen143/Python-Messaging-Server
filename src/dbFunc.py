import sqlite3

def row2Dict(row):
	return dict(zip(row.keys(),row))

def getUserAddress(username):
        db = sqlite3.connect('db/clientData')
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute('''SELECT ip, port FROM online where username = ? ''', [username])
        row = cursor.fetchone()
	print(row)
	userData = row2Dict(row) 
	print(userData)
	db.commit()
        db.close()
	print("http://"+ str(userData['IP']) +":"+ str(userData['PORT']) + "/receiveMessage")
        return "http://"+ str(userData['IP']) +":"+ str(userData['PORT']) + "/receiveMessage"

        


