import json
import mysql.connector
mydb = mysql.connector.connect(
    host="127.0.0.1",
    username="root",
    password="12345678",    
    db='attraction_database'
)
cursor = mydb.cursor()
cursor.execute("SELECT * FROM attraction")
result = cursor.fetchall()
print(result)

#json file
source = open("taipei-attractions.json","r")
sourceConverted = json.load(source)["result"]["results"]
# print(sourceConverted[0]["CAT"])
#filter .jpg files
import re
def filterJPG(string):
    regex = "http.*?\.jpg"
    jpgFile = re.findall(regex,string,re.IGNORECASE)
    return "".join(jpgFile)
# print(filterJPG(sourceConverted[0]["file"]))
#write into database
for element in range(len(sourceConverted)):
    cursor.execute("INSERT INTO attraction(id,name,category,description,address,transport,mrt,lat,lng,images) VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(sourceConverted[element]["_id"],sourceConverted[element]["name"],sourceConverted[element]["CAT"],sourceConverted[element]["description"],sourceConverted[element]["address"],sourceConverted[element]["direction"],sourceConverted[element]["MRT"],sourceConverted[element]["latitude"],sourceConverted[element]["longitude"],filterJPG(sourceConverted[element]["file"])))
    mydb.commit()

mydb.close()