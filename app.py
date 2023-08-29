from flask import *
app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
import re
import mysql.connector
dbconfg = {
	"host" : "127.0.0.1",
	"username" : "root",
	"password" : "12345678",
	"db" : "attraction_database",
	
}
mydb = mysql.connector.pooling.MySQLConnectionPool(
	pool_name="attraction",
	pool_size= 10,		
	**dbconfg
)

# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

@app.route("/api/attractions", methods=["GET"])
def attractionsList():		
	intRegex = "^\d*$"
	pageFromQueryString = request.args.get("page")	
	keywordRegex = "^\w*$"
	keywordFromQueryString = request.args.get("keyword")
	
	#check if Query String is correct format
	if re.search(intRegex,pageFromQueryString) == None:
		return {"error":True,"message":"Page number should be interger"}
	elif keywordFromQueryString != None and re.search(keywordRegex,keywordFromQueryString) == None:
		return {"error":True,"message":"Please do not enter special characters"}
	#search in database
	mydbConnection = mydb.get_connection()	
	cursor = mydbConnection.cursor()
	if keywordFromQueryString != None:
		cursor.execute("SELECT * FROM attraction WHERE name LIKE %(keywordPlus)s OR mrt = %(keyword)s",{"keywordPlus":"%"+keywordFromQueryString+"%","keyword":keywordFromQueryString})
	else:
		cursor.execute("SELECT * FROM attraction")
	
	attractionsList = cursor.fetchall()
	mydbConnection.close()	
	
	#How many pages in total
	page = int(request.args.get("page"))
	pageCount = len(attractionsList)//12

	result = {}
	result["data"] = []

	def createAttractionListbyPage(startpoint, endpoint):
			for x in range(startpoint,endpoint):
				data = {}
				data["id"] = attractionsList[x][0]
				data["name"] = attractionsList[x][1]
				data["category"] = attractionsList[x][2]
				data["description"] = attractionsList[x][3]
				data["address"] = attractionsList[x][4]
				data["transport"] = attractionsList[x][5]
				data["mrt"] = attractionsList[x][6]
				data["lat"] = attractionsList[x][7]
				data["lng"] = attractionsList[x][8]
				data["images"] = splitJPGURL(attractionsList[x][9])
				result["data"].append(data)
	
	
	
	if page >= 0 and page < pageCount :
		result["nextPage"] = page+1
		createAttractionListbyPage(page*12,(page+1)*12)
	#the last page
	elif page == pageCount :
		result["nextPage"] = None
		createAttractionListbyPage(page*12,len(attractionsList))	
	else :
		result["nextPage"] = None
		result["data"] = None
	
	return json.dumps(result,ensure_ascii = False)

def splitJPGURL(string):
		regex = "http.*?\.jpg"
		jpgFile = re.findall(regex,string,re.IGNORECASE)
		return jpgFile

@app.route("/api/attraction/<int:attractionID>", methods=["GET"])
def attraction_byID(attractionID):
	if attractionID < 0:
		return {"error":True,"message":"attractionId should be positive integer"}
	else:
		mydbConnection = mydb.get_connection()
		cursor = mydbConnection.cursor()
		cursor.execute("SELECT * FROM attraction WHERE id = %(ID)s",{"ID":attractionID})
		dataFromDatabase = cursor.fetchall()
		mydbConnection.close()	
		print(dataFromDatabase)	
		if dataFromDatabase == []:
			return{"error":True,"message":"attractionID is incorrect"}
		else:
			data = {}
			data["id"] = dataFromDatabase[0][0]
			data["name"] = dataFromDatabase[0][1]
			data["category"] = dataFromDatabase[0][2]
			data["description"] = dataFromDatabase[0][3]
			data["address"] = dataFromDatabase[0][4]
			data["transport"] = dataFromDatabase[0][5]
			data["mrt"] = dataFromDatabase[0][6]
			data["lat"] = dataFromDatabase[0][7]
			data["lng"] = dataFromDatabase[0][8]
			data["images"] = splitJPGURL(dataFromDatabase[0][9])		

			result = {}
			result["data"] = data
			return json.dumps(result,ensure_ascii = False)
		
@app.route("/api/mrts",methods=["GET"])
def mrts():
	mydbConnection = mydb.get_connection()
	cursor = mydbConnection.cursor()
	cursor.execute("SELECT mrt FROM attraction")
	dataFromDatabase = cursor.fetchall()
	mydbConnection.close()
	#transfer data to a list
	dataOriginal = []
	for x in dataFromDatabase:
		dataOriginal.append(x[0])
	#count which mrt station occurred the most
	import collections
	mrtCount = collections.Counter(dataOriginal).most_common()
	#transfer to json and return result
	data = []
	for x in mrtCount:
		if x[0] != None:
			data.append(x[0])
	result = {}
	result["data"] = data
	return json.dumps(result,ensure_ascii = False)

app.run(host="0.0.0.0", port=3000)